"""127.0.0.1-only user interface; no network-exposed ECU-write capability."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
import secrets
import threading
from .adapters import DemoAdapter, ELM327Adapter, AdapterError
from .catalog import as_json, MAKES
from .cards import CardRegistry
from .security import PROTECTED_ACTIONS

STATIC_DIR = Path(__file__).parent / "static"
PORT_PATTERN = re.compile(r"(?:COM[0-9]{1,3}|/dev/(?:tty[A-Za-z0-9._-]+|cu\.[A-Za-z0-9._-]+|serial/by-id/[A-Za-z0-9._-]+))$", re.I)

class AppState:
    def __init__(self, demo=True):
        self.lock = threading.RLock()
        self.adapter = DemoAdapter() if demo else None
        self.brand = "Saab"
        self.model = ""
        self.port = None
        self.card_registry = CardRegistry()
        self.token = secrets.token_urlsafe(24)

    def status(self):
        with self.lock:
            return {"connected": self.adapter is not None, "adapter": self.adapter.kind if self.adapter else None,
                    "demo": isinstance(self.adapter, DemoAdapter), "brand": self.brand,
                    "model": self.model, "port": self.port, "safety": "READ ONLY: no ECU writes, unlocks or programming"}

    def connect(self, port, baud, brand, model):
        if brand not in MAKES: raise ValueError("Tuntematon automerkki")
        if not isinstance(port, str) or not PORT_PATTERN.fullmatch(port): raise ValueError("Virheellinen sarjaportti")
        if type(baud) is not int or baud not in (9600, 38400, 57600, 115200):
            raise ValueError("Baudrate: 9600 / 38400 / 57600 / 115200")
        new_adapter = ELM327Adapter(port, baud)
        with self.lock:
            old = self.adapter
            self.adapter = new_adapter
            self.brand = brand
            self.model = str(model)[:120]
            self.port = port
            if old: old.close()

    def select(self, brand, model):
        if brand not in MAKES: raise ValueError("Tuntematon automerkki")
        with self.lock:
            self.brand = brand
            self.model = str(model)[:120]

    def disconnect(self):
        with self.lock:
            if self.adapter: self.adapter.close()
            self.adapter = None
            self.port = None

class AppServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, server_address, state):
        self.state = state
        super().__init__(server_address, Handler)

class Handler(BaseHTTPRequestHandler):
    server: AppServer
    def _send(self, status, payload, content_type="application/json; charset=utf-8"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(data)

    def _bad_host(self):
        # Reject DNS rebinding while keeping localhost-only access.
        host = self.headers.get("Host", "").split(":")[0].lower()
        return host not in ("localhost", "127.0.0.1")

    def do_GET(self):
        if self._bad_host(): return self._send(403, {"error":"Localhost only"})
        path = urlsplit(self.path).path
        if path == "/":
            html = (STATIC_DIR/"index.html").read_text(encoding="utf-8")
            html = html.replace("__APP_TOKEN__", self.server.state.token)
            return self._send(200, html.encode("utf-8"), "text/html; charset=utf-8")
        if path in ("/static/app.js", "/static/style.css"):
            filename = path.split("/")[-1]
            ctype = "application/javascript; charset=utf-8" if filename.endswith(".js") else "text/css; charset=utf-8"
            return self._send(200,(STATIC_DIR/filename).read_bytes(),ctype)
        if path == "/api/catalog": return self._send(200, as_json())
        if path == "/api/status": return self._send(200, self.server.state.status())
        if path == "/api/cards": return self._send(200, self.server.state.card_registry.list())
        if path == "/api/security": return self._send(200, [vars(c) for c in PROTECTED_ACTIONS])
        if path in ("/api/live", "/api/dtcs"):
            with self.server.state.lock:
                adapter = self.server.state.adapter
                if not adapter: return self._send(409, {"error":"Ei yhteyttä"})
                try:
                    result = adapter.readings() if path == "/api/live" else adapter.dtcs()
                except (AdapterError, ValueError, OSError) as exc:
                    return self._send(502, {"error":str(exc)})
            return self._send(200, {"demo": isinstance(adapter, DemoAdapter), "data": result})
        return self._send(404, {"error":"Ei löytynyt"})

    def do_POST(self):
        if self._bad_host(): return self._send(403, {"error":"Localhost only"})
        if self.headers.get("X-Tech2-Token", "") != self.server.state.token:
            return self._send(403, {"error":"Virheellinen istunto"})
        path = urlsplit(self.path).path
        if path not in ("/api/select", "/api/connect", "/api/disconnect"):
            return self._send(404, {"error":"Toimintoa ei ole"})
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            return self._send(415, {"error":"JSON vaaditaan"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size < 0 or size > 4096: return self._send(413, {"error":"Liian suuri pyyntö"})
            body = json.loads(self.rfile.read(size))
            if not isinstance(body,dict): raise ValueError("JSON-objekti vaaditaan")
            if path == "/api/disconnect":
                self.server.state.disconnect()
            elif path == "/api/select":
                self.server.state.select(body.get("brand"),body.get("model", ""))
            else:
                self.server.state.connect(body.get("port"),body.get("baud",38400),body.get("brand"),body.get("model", ""))
            return self._send(200, self.server.state.status())
        except (ValueError, AdapterError, OSError) as exc:
            return self._send(400, {"error": str(exc)})

    def log_message(self, fmt, *args):
        pass

def make_server(host="127.0.0.1", port=8765, demo=True):
    if host != "127.0.0.1": raise ValueError("Only 127.0.0.1 bind is supported in v0.1")
    return AppServer((host,port), AppState(demo))
