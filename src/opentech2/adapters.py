"""ELM327/STN11xx optional serial adapter plus an explicitly labeled offline demo."""
from __future__ import annotations
import threading
import time
from .diagnostics import SENSORS, decode_sensor, parse_dtcs

class AdapterError(Exception):
    pass

class DemoAdapter:
    kind = "DEMO (ei oikea auto)"
    values = {"rpm": 775, "speed": 0, "coolant": 87, "intake": 22, "load": 18.4, "throttle": 12.5}
    def readings(self):
        return {key: {"label": val[1], "value": self.values[key], "unit": val[2]} for key,val in SENSORS.items()}
    def dtcs(self):
        return ["P0420", "P0130"]  # deliberately fictitious demonstration data
    def close(self):
        return None

class ELM327Adapter:
    kind = "ELM327 USB-sarjaportti (geneerinen OBD-II)"
    def __init__(self, port: str, baudrate: int = 38400, serial_factory=None):
        if serial_factory is None:
            try:
                import serial
            except ImportError as exc:
                raise AdapterError("Asenna pyserial: pip install -e '.[serial]'") from exc
            serial_factory = serial.Serial
        self._serial = serial_factory(port=port, baudrate=baudrate, timeout=0.3, write_timeout=2)
        self._lock = threading.Lock()
        try:
            for cmd in ("ATZ", "ATE0", "ATL0", "ATS0", "ATH0", "ATSP0"):
                self._query(cmd, max_seconds=6)
        except Exception:
            self.close()
            raise

    def _query(self, command: str, max_seconds: float = 4) -> str:
        with self._lock:
            self._serial.reset_input_buffer()
            self._serial.write((command + "\r").encode("ascii"))
            deadline = time.monotonic() + max_seconds
            buf = bytearray()
            while time.monotonic() < deadline and len(buf) < 16384:
                data = self._serial.read(256)
                if data:
                    buf.extend(data)
                    if b">" in buf: break
            else:
                raise AdapterError(f"Ei vastausta komennolle {command}; tarkista portti/virtalukko")
            result = buf.decode("ascii", errors="replace")
            if any(s in result.upper() for s in ("UNABLE TO CONNECT", "BUS ERROR", "CAN ERROR")):
                raise AdapterError(f"Ajoneuvoyhteys epäonnistui: {result.strip()[:120]}")
            return result

    def readings(self):
        values = {}
        for key, (cmd, label, unit) in SENSORS.items():
            try:
                reply = self._query(cmd)
                value = decode_sensor(key, reply)
                values[key] = {"label": label, "value": value, "unit": unit}
            except (DiagnosticResponseError, AdapterError, ValueError) as exc:
                values[key] = {"label": label, "value": None, "unit": unit, "error": str(exc)}
        return values

    def dtcs(self):
        return parse_dtcs(self._query("03", max_seconds=7))

    def close(self):
        if getattr(self, "_serial", None):
            self._serial.close()

from .diagnostics import DiagnosticResponseError
