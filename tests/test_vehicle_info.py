import pytest
from opentech2.vehicle_info import decode_mode09_vin, VinDecodeError


def test_elm_mode09_repeated_frames():
    # 17 characters distributed across responses that each repeat 49 02 NN.
    text="0902\r49 02 01 59 53 33 41 41 31 31\r49 02 02 42 32 43 33 34 35\r49 02 03 36 37 38 39\r>"
    assert decode_mode09_vin(text)=="YS3AA11B2C3456789"


def test_elm_mode09_isotp_numbered_frames():
    text="014\r0: 49 02 01 59 53 33\r1: 41 41 31 31 42 32 43\r2: 33 34 35 36 37 38 39\r>"
    assert decode_mode09_vin(text)=="YS3AA11B2C3456789"


def test_invalid_vin_rejected():
    with pytest.raises(VinDecodeError):decode_mode09_vin("NO DATA\r>")
    with pytest.raises(VinDecodeError):decode_mode09_vin("49 02 01 41 42")
    with pytest.raises(VinDecodeError):decode_mode09_vin("49 02 01 49 4F 51 41 42 43")
