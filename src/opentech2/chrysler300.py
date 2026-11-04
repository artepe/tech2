"""Chrysler 300 family profiles — informational, read-only metadata.

No OBD protocol selection or OEM module access is inferred from a model name.
Year ranges refer to model years. Hardware varies by trim, market and engine.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

@dataclass(frozen=True)
class Chrysler300Profile:
    id: str
    title: str
    start_year: int
    end_year: int
    variants: tuple[str, ...]
    architecture: str
    networks: tuple[str, ...]
    transport_notes: str
    access_notes: str
    generic_obd: str = "ELM327 USB / generic OBD-II (untested on this vehicle)"
    oem_diagnostics: str = "NOT IMPLEMENTED"
    coding: str = "NOT IMPLEMENTED"

PROFILES = (
    Chrysler300Profile(
        id="300m-lh",
        title="Chrysler 300M · LH",
        start_year=1999,
        end_year=2004,
        variants=("300M", "300M Special", "300M Platinum"),
        architecture="LH / FWD; pre-CAN Chrysler vehicle network",
        networks=("Chrysler PCI / J1850-era (verify vehicle-specific diagnostic wiring)",),
        transport_notes="Older non-CAN Chrysler architecture; generic OBD-II may be readable with a compatible ELM327 USB adapter. No CAN ISO-TP assumption.",
        access_notes="OEM module procedures need year-specific Chrysler service information; not included.",
    ),
    Chrysler300Profile(
        id="300-lx-2005",
        title="Chrysler 300 / 300C · LX first generation",
        start_year=2005,
        end_year=2010,
        variants=("300", "300 Touring", "300 Limited", "300C", "300C Touring (EU)", "300C CRD (EU)", "300C SRT8"),
        architecture="LX / RWD or AWD; CAN-era vehicle network",
        networks=("CAN-C / diagnostic CAN-C", "CAN-B (body network)", "LIN (selected equipment)"),
        transport_notes="Separate vehicle networks; ELM327 USB reaches only standard emissions OBD-II in this prototype. OEM CAN addressing is not implemented.",
        access_notes="No OEM ECU/ABS/BCM diagnostic scan, key programming or module configuration.",
    ),
    Chrysler300Profile(
        id="300-ld-2011",
        title="Chrysler 300 / 300C · 2011–2017",
        start_year=2011,
        end_year=2017,
        variants=("300", "300 Limited", "300S", "300C", "300 SRT (selected markets)"),
        architecture="Redesigned 300 (LX/LD naming varies by source/market)",
        networks=("CAN-C (high speed)", "CAN-IHS (body/interior; hardware-specific access)"),
        transport_notes="Additional interface or hardware may be needed to access non-emissions modules on CAN-IHS. Standard ELM327 USB OBD-II read only is implemented.",
        access_notes="Manufacturer-specific module reading and coding not implemented.",
    ),
    Chrysler300Profile(
        id="300-sgw-2018",
        title="Chrysler 300 / 300C · 2018–2023",
        start_year=2018,
        end_year=2023,
        variants=("300", "300 Touring", "300S", "300C", "300C 6.4 HEMI (2023)"),
        architecture="Late Chrysler 300; electronic security gateway (vehicle/market-specific verification)",
        networks=("CAN-C", "CAN-IHS", "SGW access policy for protected diagnostics"),
        transport_notes="ELM327 may read permitted generic OBD-II emissions data. The exact gateway and supported readouts depend on the vehicle.",
        access_notes="For secure gateway protected functions, use manufacturer-authorized access and compatible equipment. No SGW bypass or ECU coding is provided.",
    ),
)

_BY_ID = {profile.id: profile for profile in PROFILES}
SOURCES: tuple[dict[str, str], ...] = (
    {"title": "Official Mopar 300M year list", "url": "https://store.mopar.com/v-chrysler-300m"},
    {"title": "Stellantis: 300 ends production in 2023", "url": "https://blog.stellantisnorthamerica.com/2023/12/09/last-legend-off-the-line-2023-chrysler-300c-ends-production/"},
    {"title": "2005 Chrysler 300 CAN network service description", "url": "https://charm.li/Chrysler/2005/300%20V6-3.5L%20VIN%20G/Repair%20and%20Diagnosis/Powertrain%20Management/Computers%20and%20Control%20Systems/Information%20Bus/Description%20and%20Operation/"},
    {"title": "FCA wiTECH official Secure Gateway guidance", "url": "https://kb.fcawitech.com/print-903.html"},
    {"title": "Chrysler 300 2011–2023 multi-CAN diagnostic notes (third-party)", "url": "https://appcar-diagfca.com/en/supported-vehicles/chrysler-300-lx/"},
)


def profile_for_year(year: int) -> Chrysler300Profile | None:
    if isinstance(year, bool) or not isinstance(year, int):
        raise ValueError("Vuosimallin täytyy olla kokonaisluku")
    return next((p for p in PROFILES if p.start_year <= year <= p.end_year), None)


def profile_as_json(p: Chrysler300Profile) -> dict[str, Any]:
    data = asdict(p)
    data["supported_now"] = ("generic OBD-II Mode 01 and 03; Mode 09 VIN when supported by vehicle",
                             "offline informational model profiles")
    data["vehicle_tested"] = False
    data["oem_tested"] = False
    data["profile_is_vehicle_connection"] = False
    return data


def catalog(year: int | None = None) -> dict[str, Any]:
    selected = profile_for_year(year) if year is not None else None
    return {
        "brand": "Chrysler",
        "family": "300 / 300C / 300M",
        "year_query": year,
        "selected": profile_as_json(selected) if selected else None,
        "profiles": [profile_as_json(p) for p in PROFILES],
        "historic": {
            "title": "1955–1965 Chrysler 300 letter-series",
            "status": "historic reference only; no electronic OBD-II connection",
            "note": "Before electronic OBD-II diagnostics, outside the scanner's functional scope",
        },
        "end_of_production": 2023,
        "sources": list(SOURCES),
        "warning": "MODEL INFORMATION ONLY. No Chrysler-specific ECU scanner, CAN-IHS adapter, SGW unlock, VIN binding, keys or ECU programming.",
    }
