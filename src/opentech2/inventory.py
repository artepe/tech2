"""Offline module/key inventory comparison. NEVER communicates with a vehicle."""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

class InventoryError(ValueError):
    pass

def _label(value, what):
    if not isinstance(value, str) or not value.strip() or len(value)>120:
        raise InventoryError(f"{what}: odotetaan 1–120 merkin tekstiä")
    return value.strip()

def analyze_inventory(filename: str | Path) -> dict:
    p=Path(filename).expanduser()
    if not p.is_file():
        raise InventoryError("Inventaarion JSON-tiedostoa ei löydy")
    if p.stat().st_size > 2*1024*1024:
        raise InventoryError("JSON-tiedosto on liian suuri (2 Mt)")
    try:
        doc=json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InventoryError(f"Virheellinen JSON: {exc}") from exc
    if not isinstance(doc,dict):
        raise InventoryError("JSON-juuren täytyy olla objekti")
    modules=doc.get("modules",[])
    keys=doc.get("key_records",[])
    if not isinstance(modules,list) or not isinstance(keys,list):
        raise InventoryError("'modules' ja 'key_records' ovat listoja")
    vehicle=doc.get("vehicle",{})
    if not isinstance(vehicle,dict):
        raise InventoryError("'vehicle' on objekti")
    vehicle_title=" ".join(str(vehicle.get(s,"")) for s in ("make","model","generation","model_year")).strip()
    by_role=defaultdict(set)
    normalized=[]
    for num,mod in enumerate(modules,1):
        if not isinstance(mod,dict):
            raise InventoryError(f"modules[{num}]: objekti vaaditaan")
        role=_label(mod.get("role"),"role")
        part=_label(mod.get("part_number"),"part_number")
        condition=str(mod.get("condition","unknown"))[:80]
        by_role[role].add(part)
        normalized.append({"index":num,"role":role,"part_number":part,"condition":condition,"compatibility":"UNVERIFIED"})
    for num,record in enumerate(keys,1):
        if not isinstance(record,dict):
            raise InventoryError(f"key_records[{num}]: objekti vaaditaan")
        _label(record.get("label"),"key label")
    contrasts=[]
    for role,parts in sorted(by_role.items()):
        if len(parts)>1:
            contrasts.append({"role":role,"different_part_numbers":sorted(parts),
                              "warning":"Eri osanumerot eivät ole todistetusti yhteensopivia; tarkista OEM-supersessio"})
    return {
        "mode":"OFFLINE READ-ONLY INVENTORY; no ECU commands, no keys programmed",
        "vehicle":vehicle_title or "ei määritelty",
        "modules_count":len(modules),
        "key_records_count":len(keys),
        "modules":normalized,
        "part_number_differences":contrasts,
        "compatibility_verdict":"UNVERIFIED: a matching part number is not sufficient for compatibility",
        "vehicle_writes":False,
        "security_access":False,
    }
