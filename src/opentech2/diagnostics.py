"""Safe generic OBD-II decoding. Does not send ECU write, reset or unlock commands."""
from __future__ import annotations
import re

SENSORS = {
    "rpm": ("010C", "Moottorin kierrosluku", "rpm"),
    "speed": ("010D", "Ajonopeus", "km/h"),
    "coolant": ("0105", "Jäähdytysneste", "°C"),
    "intake": ("010F", "Imuilma", "°C"),
    "load": ("0104", "Moottorin kuormitus", "%"),
    "throttle": ("0111", "Kaasuläpän asento", "%"),
}

class DiagnosticResponseError(ValueError):
    pass


def _lines(reply: str):
    for raw in reply.upper().replace("\r", "\n").splitlines():
        s = raw.strip()
        if not s or s in (">", "OK", "NO DATA", "STOPPED") or s.startswith(("SEARCHING", "BUS INIT")):
            continue
        s = re.sub(r"^\d+:\s*", "", s)  # ELM frame counter
        compact = re.sub(r"\s+", "", s)
        if re.fullmatch(r"[0-9A-F]+", compact) and len(compact) % 2 == 0:
            yield bytes.fromhex(compact)


def pid_bytes(reply: str, pid: int) -> bytes:
    prefix = bytes((0x41, pid))
    for frame in _lines(reply):
        pos = frame.find(prefix)
        if pos >= 0:
            return frame[pos + 2:]
    raise DiagnosticResponseError(f"OBD PID {pid:02X} ei löytynyt vastauksesta")


def decode_sensor(sensor_id: str, reply: str):
    if sensor_id not in SENSORS:
        raise KeyError(sensor_id)
    pid = int(SENSORS[sensor_id][0][-2:], 16)
    data = pid_bytes(reply, pid)
    if not data:
        raise DiagnosticResponseError("Puuttuva mittausarvo")
    a = data[0]
    b = data[1] if len(data) > 1 else 0
    if sensor_id == "rpm":
        if len(data) < 2: raise DiagnosticResponseError("RPM tarvitsee kaksi tavua")
        return round(((a * 256) + b) / 4, 1)
    if sensor_id in ("coolant", "intake"):
        return a - 40
    if sensor_id in ("load", "throttle"):
        return round(a * 100 / 255, 1)
    return a


def parse_dtcs(reply: str) -> list[str]:
    """Decode generic Mode 03 emission-related DTCs (not all ECU systems)."""
    result = []
    for frame in _lines(reply):
        try: idx = frame.index(0x43)
        except ValueError: continue
        payload = frame[idx + 1:]
        # A response may include a number-of-codes byte in some adapters; do not guess.
        for p in range(0, len(payload)-1, 2):
            a, b = payload[p:p+2]
            if (a,b) == (0,0): continue
            family = "PCBU"[(a >> 6) & 3]
            code = f"{family}{(a >> 4) & 3:X}{a & 15:X}{b >> 4:X}{b & 15:X}"
            if code not in result: result.append(code)
    return result
