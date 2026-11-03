"""Generic SAE J1979 Mode 09 VIN decoder for ELM327 adapters.

This is not a Saab CIM, immobilizer, or manufacturer-specific ECU reader.
"""
from __future__ import annotations
import re


class VinDecodeError(ValueError):
    pass


def decode_mode09_vin(reply: str) -> str:
    """Decode a standard Mode 09 PID 02 response.

    Accepts ELM text responses with either repeated '49 02 xx' per frame or
    number-prefixed ISO-TP lines; rejects truncated or malformed VINs.
    """
    if not isinstance(reply, str) or len(reply) > 16384:
        raise VinDecodeError("Liian pitkä tai virheellinen VIN-vastaus")
    tokens: list[bytes] = []
    started = False
    for line in reply.upper().replace("\r", "\n").splitlines():
        line = line.strip().strip(">")
        if not line or any(msg in line for msg in ("NO DATA", "ERROR", "STOPPED")):
            continue
        # Ignore first-line CAN total length e.g. '014' and numeric ISO-TP frame labels.
        line = re.sub(r"^[0-9A-F]{1,2}:\s*", "", line)
        compact = re.sub(r"\s+", "", line)
        if compact in ("0902", "014", "14") or not re.fullmatch(r"[0-9A-F]+", compact):
            continue
        if len(compact) % 2:
            continue
        frame = bytes.fromhex(compact)
        if b"\x49\x02" in frame:
            at = frame.index(b"\x49\x02")
            if len(frame) < at + 3:
                continue
            started = True
            # The third byte is the VIN message-frame order (typically 01).
            tokens.append(frame[at+3:])
        elif started:
            tokens.append(frame)
    payload = b"".join(tokens).lstrip(b"\x00")
    candidate = payload[:17]
    try:
        vin = candidate.decode("ascii")
    except UnicodeDecodeError as exc:
        raise VinDecodeError("VIN ei ole ASCII-muodossa") from exc
    if len(vin) != 17 or not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin):
        raise VinDecodeError("Autosta ei saatu kelvollista 17-merkkistä VIN-tunnistetta")
    return vin
