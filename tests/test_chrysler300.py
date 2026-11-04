import json
import threading
from urllib.request import urlopen
from opentech2.chrysler300 import PROFILES, catalog, profile_for_year
from opentech2.server import make_server
import pytest


def test_every_300m_and_modern_year_mapped():
    for year in range(1999, 2024):
        profile = profile_for_year(year)
        assert profile is not None, year
        assert profile.start_year <= year <= profile.end_year
    assert profile_for_year(1999).id == "300m-lh"
    assert profile_for_year(2004).id == "300m-lh"
    assert profile_for_year(2005).id == "300-lx-2005"
    assert profile_for_year(2010).id == "300-lx-2005"
    assert profile_for_year(2011).id == "300-ld-2011"
    assert profile_for_year(2017).id == "300-ld-2011"
    assert profile_for_year(2018).id == "300-sgw-2018"
    assert profile_for_year(2023).id == "300-sgw-2018"
    assert profile_for_year(2024) is None


def test_no_unsupported_features_claimed():
    for p in PROFILES:
        assert p.oem_diagnostics == "NOT IMPLEMENTED"
        assert p.coding == "NOT IMPLEMENTED"
        row = catalog(p.start_year)["selected"]
        assert row["vehicle_tested"] is False
        assert row["profile_is_vehicle_connection"] is False
        assert row["oem_tested"] is False


def test_year_input_validation():
    with pytest.raises(ValueError):
        profile_for_year(True)
    with pytest.raises(ValueError):
        profile_for_year("2022")


def test_selected_and_unmatched_years():
    assert catalog(2007)["selected"]["id"] == "300-lx-2005"
    assert catalog(1980)["selected"] is None
    assert catalog(2025)["selected"] is None
    assert len(catalog()["profiles"]) == 4
    assert catalog()["historic"]["status"].startswith("historic")


@pytest.fixture
def app():
    server=make_server(port=0,demo=True)
    t=threading.Thread(target=server.serve_forever,daemon=True)
    t.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=3)


def test_api_catalog_year(app):
    base=f"http://127.0.0.1:{app.server_port}"
    for uri,expected in (("/api/chrysler-300?year=2002","300m-lh"),
                         ("/api/chrysler-300?year=2019","300-sgw-2018")):
        with urlopen(base+uri) as response:
            d=json.load(response)
            assert d["selected"]["id"]==expected
            assert response.status==200
    with urlopen(base+"/api/chrysler-300?year=2024") as response:
        d=json.load(response)
        assert d["selected"] is None


def test_static_page_has_chrysler_controls(app):
    with urlopen(f"http://127.0.0.1:{app.server_port}/") as response:
        body=response.read().decode()
        assert 'id="chrysler-year"' in body
        assert 'id="chrysler-profile-info"' in body
