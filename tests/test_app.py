import json
import threading
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import pytest
from opentech2.server import make_server, PORT_PATTERN
from opentech2.adapters import ELM327Adapter

@pytest.fixture
def app():
    srv=make_server(port=0,demo=True)
    worker=threading.Thread(target=srv.serve_forever,daemon=True)
    worker.start()
    try:
        yield srv
    finally:
        srv.shutdown();srv.server_close();worker.join(timeout=2)

def base(srv):return f'http://127.0.0.1:{srv.server_port}'

def get_json(srv, route):
    with urlopen(base(srv)+route,timeout=2) as res:return json.load(res)

def test_dashboard(app):
    with urlopen(base(app),timeout=2) as res:
        assert b'OpenTech2' in res.read()
    assert get_json(app,'/api/status')['demo'] is True
    assert len(get_json(app,'/api/catalog')['card_families'])>=7

def test_demo_values_labeled(app):
    d=get_json(app,'/api/live')
    assert d['demo'] is True
    assert d['data']['rpm']['value']==775

def test_protected_endpoints_denied(app):
    req=Request(base(app)+'/api/disconnect',data=b'{}',headers={'Content-Type':'application/json'},method='POST')
    with pytest.raises(HTTPError) as err:urlopen(req,timeout=2)
    assert err.value.code==403

def test_selected_car_only_with_token(app):
    req=Request(base(app)+'/api/select',data=json.dumps({'brand':'Opel','model':'Astra'}).encode(),headers={'Content-Type':'application/json','X-Tech2-Token':app.state.token},method='POST')
    with urlopen(req,timeout=2) as res: assert json.load(res)['brand']=='Opel'

class FakeSerial:
    responses={b'ATZ':'ELM327 v1.5\r>',b'ATE0':'OK\r>',b'ATL0':'OK\r>',b'ATS0':'OK\r>',b'ATH0':'OK\r>',b'ATSP0':'OK\r>',b'010C':'41 0C 0B B8\r>',b'010D':'41 0D 00\r>',b'0105':'41 05 7A\r>',b'010F':'41 0F 45\r>',b'0104':'41 04 40\r>',b'0111':'41 11 20\r>',b'03':'43 01 33 00 00\r>'}
    def __init__(self,**kwargs):self.command=None;self.closed=False;self.responses=dict(type(self).responses)
    def write(self,data):self.command=data.strip();return len(data)
    def read(self,n):
        data=self.responses[self.command].encode('ascii');self.responses[self.command]=''
        return data
    def reset_input_buffer(self):pass
    def close(self):self.closed=True

def test_elm_adapter_with_mock():
    a=ELM327Adapter('/dev/ttyUSB0',serial_factory=FakeSerial)
    assert a.kind.startswith('ELM327')
    assert a.readings()['rpm']['value']==750.0
    assert a.dtcs()==['P0133']
    a.close()

def test_port_whitelist():
    assert PORT_PATTERN.fullmatch('/dev/cu.usbserial-0001')
    assert PORT_PATTERN.fullmatch('COM15')
    assert not PORT_PATTERN.fullmatch('/etc/passwd')
