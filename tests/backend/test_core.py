from datetime import datetime,timezone
from backend.app.auth.lockout import failure_state
from backend.app.auth.input import parse_urlencoded_pin
from backend.app.auth.pin_kdf import create_verifier,verify,valid_pin
from backend.app.auth.sessions import new_token,token_hash,cookie_header
from backend.app.ai.validator import validate
from backend.app.ai.fallback import choose_fallback
def test_pin_verifier_and_policy():
    salt,digest,iterations=create_verifier('123456','pepper',1000)
    assert verify('123456','pepper',salt,digest,iterations)
    assert not verify('654321','pepper',salt,digest,iterations)
    assert valid_pin('1234','profile') and not valid_pin('1234','admin')
def test_lockout_progression():
    now=datetime(2026,9,4,tzinfo=timezone.utc);count=0
    for _ in range(5):count,level,locked=failure_state(count,0,now)
    assert count==0 and level==1 and int((locked-now).total_seconds())==60
def test_opaque_session():
    token=new_token();digest=token_hash(token,'pepper')
    assert token not in digest and len(digest)==64
    assert 'Secure' in cookie_header(token) and 'HttpOnly' in cookie_header(token) and 'SameSite=Strict' in cookie_header(token)
def test_ai_validation_and_fallback():
    assert validate('asdf asdf asdf','asdf ',5)['valid']
    assert 'forbidden_character' in validate('asdf q asdf','asdf ',5)['errors']
    assert choose_fallback(['a','b'],'00000001')=='b'
def test_urlencoded_pin_input():
    assert parse_urlencoded_pin(b'pin=123456') == '123456'
    assert parse_urlencoded_pin(b'other=value') == ''
def test_login_page_uses_csp_compatible_external_script():
    source = open('backend/main.py', encoding='utf-8').read()
    assert '<script src="/auth.js" defer></script>' in source
    assert '@app.get("/auth.js")' in source
