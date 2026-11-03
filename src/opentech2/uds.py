"""Explicit, allowlisted UDS ECU identification over Linux kernel CAN_ISOTP.

Safety boundaries:
* Only UDS 0x22 ReadDataByIdentifier is ever emitted.
* Only standard identity DIDs listed in IDENTIFICATION_DIDS are accepted.
* A single caller-selected 11-bit ECU request/response pair is used.
* No scanning, diagnostic-session change, security access, ECU coding or writes.
* For Saab 9440 these requests are NOT guaranteed to be implemented by the ECU.
"""
from __future__ import annotations

import re
import socket
import sys
from dataclasses import dataclass
from typing import Callable

IDENTIFICATION_DIDS: dict[int, str] = {
    0xF187: "Valmistajan varaosanumero",
    0xF188: "ECU-ohjelmistonumero",
    0xF189: "ECU-ohjelmistoversio",
    0xF18C: "ECU-sarjanumero",
    0xF190: "Ajoneuvon VIN",
    0xF191: "ECU-laitteistonumero",
    0xF192: "ECU-toimittajan laitteistonumero",
    0xF195: "ECU-toimittajan ohjelmistoversio",
}
DEFAULT_DIDS = (0xF190, 0xF187, 0xF188)
MAX_DIDS_PER_REQUEST = 6
CAN_INTERFACE = re.compile(r"(?:can|vcan|slcan)[0-9]{1,3}$")


class UdsError(Exception):
    """Transport, validation, or malformed UDS response."""


@dataclass(frozen=True)
class NegativeUdsResponse(UdsError):
    code: int

    def __str__(self):
        names = {0x11: "service not supported", 0x12: "subfunction not supported",
                 0x13: "incorrect length", 0x22: "conditions not correct",
                 0x31: "request out of range", 0x33: "security access denied",
                 0x78: "response pending"}
        return f"UDS negative response 0x{self.code:02X}: {names.get(self.code, 'unknown')}"


def parse_dids(values) -> tuple[int, ...]:
    if not isinstance(values, (list, tuple)) or not 1 <= len(values) <= MAX_DIDS_PER_REQUEST:
        raise ValueError("DID-listassa pitää olla 1–6 valmista tunnistetta")
    out = []
    for val in values:
        if isinstance(val, bool):
            raise ValueError("Virheellinen DID")
        try:
            did = int(val, 16) if isinstance(val, str) else int(val)
        except (ValueError, TypeError) as exc:
            raise ValueError("DID ei ole heksaluku") from exc
        if did not in IDENTIFICATION_DIDS:
            raise ValueError(f"UDS DID 0x{did:04X} ei ole sallitussa vain-luku-luettelossa")
        if did not in out:
            out.append(did)
    return tuple(out)


def parse_can_id(value) -> int:
    if isinstance(value, bool):
        raise ValueError("CAN-tunniste on annettava muodossa 0x7E0")
    if isinstance(value, int):
        can_id = value
    elif isinstance(value, str) and re.fullmatch(r"0x[0-9a-fA-F]{1,3}", value):
        can_id = int(value, 16)
    else:
        raise ValueError("CAN-tunniste on annettava muodossa 0x7E0")
    if not 0 < can_id <= 0x7FF or can_id == 0x7DF:
        raise ValueError("Vain erikseen valittu 11-bittinen fyysinen CAN-tunniste käy (ei 0x7DF broadcast)")
    return can_id


def validate_address(interface: str, txid: int | str, rxid: int | str) -> tuple[int, int]:
    if not isinstance(interface, str) or not CAN_INTERFACE.fullmatch(interface):
        raise ValueError("Rajapinnan nimi on esim. can0 tai vcan0")
    tx, rx = parse_can_id(txid), parse_can_id(rxid)
    if tx == rx:
        raise ValueError("Lähetys- ja vastaanotto-ID:n on oltava eri")
    return tx, rx


def decode_identity(did: int, data: bytes) -> dict:
    """Parse a single positive response. Never assume a binary part number is ASCII."""
    if not isinstance(data, bytes) or len(data) > 4095:
        raise UdsError("Virheellinen ECU-vastaus")
    if len(data) >= 3 and data[0:2] == b"\x7F\x22":
        raise NegativeUdsResponse(data[2])
    expected = b"\x62" + did.to_bytes(2, "big")
    if not data.startswith(expected) or len(data) <= len(expected):
        raise UdsError(f"ECU:n vastaus ei täsmää DID-tunnisteeseen {did:04X}")
    raw = data[3:]
    clean = raw.rstrip(b"\x00 ")
    if clean and all(32 <= x <= 126 for x in clean):
        value, representation = clean.decode("ascii"), "ascii"
    else:
        value, representation = raw.hex(" ").upper(), "hex"
    return {
        "did": f"{did:04X}",
        "name": IDENTIFICATION_DIDS[did],
        "value": value,
        "encoding": representation,
        "raw_hex": raw.hex().upper(),
        "status": "ok",
    }


class SocketCanDidReader:
    """Uses Linux's CAN_ISOTP socket and its built-in flow control/reassembly."""

    def __init__(self, interface: str, txid: int | str, rxid: int | str,
                 *, timeout: float = 1.5, socket_factory: Callable | None = None):
        tx, rx = validate_address(interface, txid, rxid)
        if not 0.2 <= timeout <= 5:
            raise ValueError("Aikakatkaisun on oltava 0,2–5 sekuntia")
        if socket_factory is None and sys.platform != "linux":
            raise UdsError("SocketCAN ISO-TP on saatavilla vain Linuxissa. Mac: käytä OBD-II USB -lukijaa.")
        factory = socket_factory or socket.socket
        try:
            sock = factory(socket.AF_CAN, socket.SOCK_DGRAM, socket.CAN_ISOTP)
            sock.settimeout(timeout)
            sock.bind((interface, rx, tx))  # Linux native order is RX, then TX
        except (OSError, AttributeError) as exc:
            try:
                sock.close()
            except (UnboundLocalError, AttributeError):
                pass
            raise UdsError(f"SocketCAN/ISO-TP-yhteyttä ei voitu avata: {exc}") from exc
        self.sock = sock
        self.interface, self.txid, self.rxid = interface, tx, rx

    def read_did(self, did: int) -> dict:
        if did not in IDENTIFICATION_DIDS:
            raise ValueError("DID ei kuulu vain-luku sallittujen tunnisteiden listaan")
        # Only the read-only 0x22 service; no diagnostic-session or security services.
        request = b"\x22" + did.to_bytes(2, "big")
        try:
            self.sock.send(request)
            reply = self.sock.recv(4095)
        except (OSError, TimeoutError) as exc:
            raise UdsError(f"ECU ei vastannut DID {did:04X}: {exc}") from exc
        return decode_identity(did, reply)

    def read_many(self, dids=DEFAULT_DIDS) -> list[dict]:
        result = []
        for did in parse_dids(dids):
            try:
                result.append(self.read_did(did))
            except (UdsError, ValueError) as exc:
                result.append({"did": f"{did:04X}", "name": IDENTIFICATION_DIDS[did],
                               "status": "not_available", "error": str(exc)})
        return result

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def read_demo_identification(dids=DEFAULT_DIDS) -> list[dict]:
    """Offline benchmark only; values are intentionally impossible-to-mistake test data."""
    samples = {
        0xF190: b"TESTVIN1234567890",
        0xF187: b"DEMO-PART-0001",
        0xF188: b"DEMO-SW-001",
        0xF189: b"DEMO-SW-v1",
        0xF18C: b"DEMO-ECU-0001",
        0xF191: b"DEMO-HW-001",
        0xF192: b"DEMO-VENDOR-001",
        0xF195: b"DEMO-VENDOR-SW-1",
    }
    return [decode_identity(did, b"\x62" + did.to_bytes(2, "big") + samples[did])
            for did in parse_dids(dids)]
