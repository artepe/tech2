"""Informational catalogs. Never imply OEM-level support from a generic brand entry."""
from __future__ import annotations
from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class CardFamily:
    id: str
    name: str
    makes: tuple[str, ...]
    note: str = "Metadata only: no original software, ROM image, or security key supplied"

CARD_FAMILIES = (
    CardFamily("saab", "Saab Tech 2 / Tech2Win", ("Saab",)),
    CardFamily("opel", "Opel / Vauxhall Tech 2 / Tech2Win", ("Opel", "Vauxhall")),
    CardFamily("gm", "GM / Chevrolet / Cadillac Tech 2", ("Chevrolet", "Cadillac", "Buick", "GMC", "Pontiac", "Oldsmobile", "Hummer")),
    CardFamily("holden", "Holden Tech 2", ("Holden",)),
    CardFamily("isuzu", "Isuzu Tech 2", ("Isuzu",)),
    CardFamily("suzuki", "Suzuki Tech 2", ("Suzuki",)),
    CardFamily("saturn", "Saturn Astra / GM Tech 2", ("Saturn",)),
)
MAKES = tuple(sorted({
    "Audi", "BMW", "Buick", "Cadillac", "Chevrolet", "Citroën", "Dacia", "Fiat",
    "Ford", "GMC", "Holden", "Honda", "Hummer", "Hyundai", "Isuzu", "Jaguar",
    "Jeep", "Kia", "Land Rover", "Lexus", "Mazda", "Mercedes-Benz", "Mini",
    "Mitsubishi", "Nissan", "Oldsmobile", "Opel", "Peugeot", "Pontiac", "Porsche",
    "Renault", "Saab", "Saturn", "Seat", "Škoda", "Subaru", "Suzuki", "Tesla",
    "Toyota", "Volkswagen", "Volvo", "Vauxhall", "Chrysler", "Dodge"
}))

def as_json():
    return {
        "makes": [{"name": make, "obd2": "generic-only-where-supported", "oem_tech2": [c.id for c in CARD_FAMILIES if make in c.makes]} for make in MAKES],
        "card_families": [asdict(c) for c in CARD_FAMILIES],
        "warning": "These are catalog labels, not supported-model claims. Real OEM features require separate verified implementation and access rights.",
    }
