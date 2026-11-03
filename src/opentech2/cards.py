"""Metadata-only card register: fingerprints user-owned binary without copying it."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path

class CardRegistry:
    def __init__(self, registry_file: Path | str | None = None):
        self.path = Path(registry_file) if registry_file else Path.home()/".opentech2"/"cards.json"

    def list(self):
        if not self.path.exists(): return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def add(self, binary_path: Path | str, family: str, label: str):
        from .catalog import CARD_FAMILIES
        valid = {card.id for card in CARD_FAMILIES}
        if family not in valid:
            raise ValueError(f"Tuntematon korttiperhe: {family}; valitse {', '.join(sorted(valid))}")
        p = Path(binary_path).expanduser().resolve(strict=True)
        if not p.is_file(): raise ValueError("Polku ei ole tiedosto")
        if p.stat().st_size > 256 * 1024 * 1024: raise ValueError("Tiedosto ylittää 256 Mt rajan")
        digest = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                digest.update(chunk)
        record = {"name": label, "family": family, "filename": p.name,
                  "size_bytes": p.stat().st_size, "sha256": digest.hexdigest(),
                  "mode": "metadata-only; no card execution or decoding"}
        items = [i for i in self.list() if i["sha256"] != record["sha256"]]
        items.append(record)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(temp, self.path)
        try: os.chmod(self.path, 0o600)
        except OSError: pass
        return record
