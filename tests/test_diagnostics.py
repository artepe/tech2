import pytest
from opentech2.diagnostics import decode_sensor, parse_dtcs, DiagnosticResponseError

def test_rpm_spaced():
    assert decode_sensor('rpm','010C\r41 0C 0B B8\r>')==750.0

def test_speed_compact():
    assert decode_sensor('speed','410D3C\r>')==60

def test_coolant():
    assert decode_sensor('coolant','41 05 7B')==83

def test_percent():
    assert decode_sensor('load','41 04 80')==pytest.approx(50.2)

def test_dtcs():
    assert parse_dtcs('43 01 33 04 20 00 00\r>')==['P0133','P0420']

def test_no_data():
    with pytest.raises(DiagnosticResponseError): decode_sensor('speed','NO DATA\r>')
