import sys
import pytest
from opentech2.uds import (
    SocketCanDidReader, UdsError, NegativeUdsResponse, parse_dids,
    parse_can_id, decode_identity, read_demo_identification
)

class FakeIsoTpSocket:
    def __init__(self, *args):
        self.args=args
        self.messages=[]
        self.timeout=None
        self.bound=None
        self.closed=False
        self.reply=b"\x62\xF1\x87\x44\x45\x4D\x4F"
    def settimeout(self,timeout): self.timeout=timeout
    def bind(self,address): self.bound=address
    def send(self,payload): self.messages.append(payload)
    def recv(self,n): return self.reply
    def close(self): self.closed=True


def test_allowlisted_reader_generates_only_uds_22():
    fake=FakeIsoTpSocket()
    with SocketCanDidReader("vcan0","0x7E0","0x7E8",socket_factory=lambda *a:fake) as reader:
        result=reader.read_did(0xF187)
        assert result["value"]=="DEMO"
        assert fake.messages==[bytes.fromhex("22F187")]
        assert fake.bound==("vcan0",0x7E8,0x7E0)
    assert fake.closed


def test_rejects_unlisted_did_and_broadcast():
    fake=FakeIsoTpSocket()
    with SocketCanDidReader("vcan0","0x7E0","0x7E8",socket_factory=lambda *a:fake) as reader:
        with pytest.raises(ValueError):reader.read_did(0xF200)
        assert fake.messages==[]
    with pytest.raises(ValueError):parse_dids(["2701"])
    with pytest.raises(ValueError):parse_can_id("0x7DF")
    with pytest.raises(ValueError):parse_can_id("0x8FF")
    with pytest.raises(ValueError):parse_dids(["F190"]*7)
    assert parse_dids(["F190","F190","F187"])==(0xF190,0xF187)


def test_negative_response_and_wrong_did():
    with pytest.raises(NegativeUdsResponse) as ex:
        decode_identity(0xF190,bytes.fromhex("7F2231"))
    assert ex.value.code==0x31
    with pytest.raises(UdsError):
        decode_identity(0xF190,bytes.fromhex("62F1874142"))


def test_binary_values_hex_and_six_demo_items():
    r=decode_identity(0xF191,bytes.fromhex("62F1910001FF"))
    assert r["encoding"]=="hex"
    assert r["value"]=="00 01 FF"
    items=read_demo_identification(["F190","F187","F188","F189","F18C","F191"])
    assert len(items)==6 and items[0]["status"]=="ok"


def test_unavailable_did_reported_not_forged():
    fake=FakeIsoTpSocket()
    fake.reply=bytes.fromhex("7F2231")
    with SocketCanDidReader("vcan0","0x7E0","0x7E8",socket_factory=lambda *a:fake) as reader:
        result=reader.read_many([0xF190])
    assert result[0]["status"]=="not_available"
    assert "0x31" in result[0]["error"]
