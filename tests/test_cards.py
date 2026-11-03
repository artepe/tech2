import pytest
from opentech2.cards import CardRegistry
from opentech2.security import require_verified_oem_authorization, AuthorizationRequired

def test_register_metadata(tmp_path):
    test_file=tmp_path/'user_owned_card.bin'
    test_file.write_bytes(b'example, not firmware')
    registry=CardRegistry(tmp_path/'cards.json')
    result=registry.add(test_file, 'saab', 'Testi')
    assert result['size_bytes']==len(b'example, not firmware')
    assert 'path' not in result
    assert 'sha256' in result
    assert registry.list()[0]['name']=='Testi'
    registry.add(test_file, 'saab', 'Testi')
    assert len(registry.list())==1

def test_card_family_validation(tmp_path):
    test_file=tmp_path/'x.bin';test_file.write_bytes(b'123')
    with pytest.raises(ValueError): CardRegistry(tmp_path/'cards.json').add(test_file,'invalid','X')

def test_oem_actions_fail_closed():
    with pytest.raises(AuthorizationRequired):require_verified_oem_authorization('keys')
