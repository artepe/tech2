import json
import pytest
from opentech2.inventory import analyze_inventory, InventoryError

def test_inventory_demo(tmp_path):
    path=tmp_path/"my-test.json"
    path.write_text(json.dumps({"vehicle":{"make":"Saab","model":"9-3"},
      "modules":[{"role":"CIM","part_number":"DEMO-A"},{"role":"CIM","part_number":"DEMO-B"}],
      "key_records":[{"label":"Demo key "+str(i)} for i in range(80)]}),encoding="utf-8")
    data=analyze_inventory(path)
    assert data["modules_count"]==2
    assert data["key_records_count"]==80
    assert data["part_number_differences"][0]["role"]=="CIM"
    assert data["vehicle_writes"] is False
    assert data["security_access"] is False
    assert data["compatibility_verdict"].startswith("UNVERIFIED")

def test_inventory_rejects_missing_part(tmp_path):
    path=tmp_path/"bad.json"
    path.write_text(json.dumps({"modules":[{"role":"ECM"}]}),encoding="utf-8")
    with pytest.raises(InventoryError):analyze_inventory(path)
