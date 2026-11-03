import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import pytest
from opentech2.server import make_server
import threading


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


def _base(server):
    return f"http://127.0.0.1:{server.server_port}"


def post(server,path,payload,token=True):
    headers={"Content-Type":"application/json"}
    if token: headers["X-Tech2-Token"]=server.state.token
    req=Request(_base(server)+path,headers=headers,method="POST",
                data=json.dumps(payload).encode("utf-8"))
    with urlopen(req,timeout=2) as response:
        return json.load(response)


def test_vin_api_demo_no_hardware(app):
    with urlopen(_base(app)+"/api/vehicle-identification",timeout=2) as response:
        result=json.load(response)
    assert result["demo"] is True
    assert result["data"]["source"].startswith("DEMO")
    assert "TESTVIN" in result["data"]["vin"]


def test_uds_api_demo(app):
    result=post(app,"/api/ecu/uds",{"demo":True,"dids":["F190","F187","F188"]})
    assert result["demo"] is True
    assert [entry["did"] for entry in result["data"]]==["F190","F187","F188"]


def test_uds_api_rejects_unknown_did(app):
    with pytest.raises(HTTPError) as err:
        post(app,"/api/ecu/uds",{"demo":True,"dids":["2701"]})
    assert err.value.code==400


def test_uds_api_requires_session(app):
    with pytest.raises(HTTPError) as err:
        post(app,"/api/ecu/uds",{"demo":True},token=False)
    assert err.value.code==403
