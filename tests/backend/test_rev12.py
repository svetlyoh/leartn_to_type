import asyncio
import importlib
import json
import sqlite3
import sys
import types
from pathlib import Path
from datetime import timedelta
import pytest
from fastapi import HTTPException
from backend.app.ai.fallback import constrained_pattern
from backend.app.ai.validator import validate
from backend.app.curriculum.generated_curriculum import CURRICULUM

class Statement:
    def __init__(self, db, sql): self.db, self.sql, self.values = db, sql, ()
    def bind(self, *values): self.values = values; return self
    async def first(self):
        row = self.db.conn.execute(self.sql, self.values).fetchone()
        return dict(row) if row else None
    async def all(self): return {'results': [dict(row) for row in self.db.conn.execute(self.sql,self.values).fetchall()]}
    async def run(self): self.db.conn.execute(self.sql,self.values); return {}

class DB:
    def __init__(self):
        self.conn = sqlite3.connect(':memory:'); self.conn.row_factory = sqlite3.Row
        for path in sorted(Path('migrations').glob('*.sql')): self.conn.executescript(path.read_text())
    def prepare(self, sql): return Statement(self, sql)

@pytest.fixture
def core(monkeypatch):
    monkeypatch.syspath_prepend('backend')
    monkeypatch.setitem(sys.modules,'workers',types.SimpleNamespace(asgi=types.SimpleNamespace(entrypoint=lambda x:x)))
    return importlib.import_module('main')

@pytest.fixture
def setup(core, monkeypatch):
    db=DB(); timestamp=core.iso(core.now())
    for user in ['one','other']:
        db.conn.execute("INSERT INTO users(id,webauthn_user_id,temporary_handle,created_at,updated_at) VALUES(?,?,?,?,?)",(user,user.encode(),user,timestamp,timestamp))
        db.conn.execute("INSERT INTO passkey_credentials(credential_id,user_id,public_key,created_at) VALUES(?,?,?,?)",('YQ' if user=='one' else 'Yg',user,b'test',timestamp))
    binding=types.SimpleNamespace(DB=db,SESSION_PEPPER='test-only',CURRICULUM_VERSION='2026.10',MINIMAX_MODEL='test')
    class Request:
        scope={'env':binding};cookies={core.COOKIE:'test-session'}
        url=types.SimpleNamespace(hostname='localhost',scheme='https',netloc='localhost')
        body={}
        async def json(self): return self.body
    async def session(*args): return {'user_id':'one','profile_id':None,'role':'learner'}
    monkeypatch.setattr(core,'require_session',session)
    endpoints={route.path:route.endpoint for route in core.app.routes}
    return db,Request(),endpoints

def run(coro): return asyncio.run(coro)

def test_patterns_are_varied_deterministic_and_key_safe():
    for stage in CURRICULUM['stages']:
        results=[constrained_pattern(stage['allowedCharacters'],stage['introducedKeys'],stage['id'],target=60,seed=str(i)) for i in range(8)]
        assert len(set(results))>1
        assert all(validate(text,stage['allowedCharacters'],12,1200)['valid'] for text in results)
        assert results[0]==constrained_pattern(stage['allowedCharacters'],stage['introducedKeys'],stage['id'],target=60,seed='0')

def test_list_and_last_passkey_ownership(setup):
    db,request,routes=setup
    result=run(routes['/api/v1/auth/passkeys'](request))
    assert [k['credential_id'] for k in result['passkeys']]==['YQ']
    for key in ['YQ','Yg']:
        with pytest.raises(HTTPException):run(routes['/api/v1/auth/passkeys/{credential_id}'](key,request))
    db.conn.execute("INSERT INTO passkey_credentials(credential_id,user_id,public_key,created_at) VALUES('c','one',X'01','today')")
    with pytest.raises(HTTPException):run(routes['/api/v1/auth/passkeys/{credential_id}']('Yg',request))
    run(routes['/api/v1/auth/passkeys/{credential_id}']('YQ',request))
    assert db.conn.execute("SELECT credential_id FROM passkey_credentials WHERE user_id='one'").fetchone()[0]=='c'

def test_options_same_user_exclusion_and_atomic_challenge(core,setup):
    db,request,routes=setup
    result=run(routes['/api/v1/auth/passkeys/add/options'](request))
    options=json.loads(result.body)['publicKey']
    assert options['user']['id']==core.b64url(b'one')
    assert options['excludeCredentials'][0]['id']=='YQ'
    row=dict(db.conn.execute('SELECT * FROM webauthn_challenges').fetchone())
    assert 0<(core.datetime.fromisoformat(row['expires_at'].replace('Z','+00:00'))-core.now()).total_seconds()<=300
    request.cookies[core.CEREMONY_COOKIE]=result.headers['set-cookie'].split(';')[0].split('=',1)[1]
    with pytest.raises(HTTPException):run(core.consume_challenge(request,'registration'))
    run(core.consume_challenge(request,'registration',row['auth_session_hash']))
    with pytest.raises(HTTPException):run(core.consume_challenge(request,'registration',row['auth_session_hash']))

def test_third_key_rejected_at_options_and_database(setup):
    db,request,routes=setup
    db.conn.execute("INSERT INTO passkey_credentials(credential_id,user_id,public_key,created_at) VALUES('c','one',X'01','today')")
    with pytest.raises(HTTPException):run(routes['/api/v1/auth/passkeys/add/options'](request))
    with pytest.raises(sqlite3.IntegrityError):db.conn.execute("INSERT INTO passkey_credentials(credential_id,user_id,public_key,created_at) VALUES('d','one',X'01','today')")

@pytest.mark.parametrize('provider_mode',['timeout','invalid','none'])
def test_anchor_custom_request_survives_provider_and_cache_failure(core,setup,monkeypatch,provider_mode):
    db,request,routes=setup
    request.body={'stage_id':'module_01','curriculum_version':'2026.10','mode':'custom_passage','topic':'running','request_id':'fresh'}
    original=core.first
    async def first(db,sql,*values):
        if 'FROM progress' in sql:return {'stage_id':'module_01'}
        if 'generated_content' in sql:raise RuntimeError('cache unavailable')
        return await original(db,sql,*values)
    monkeypatch.setattr(core,'first',first)
    if provider_mode!='none':
        request.scope['env'].MINIMAX_API_KEY='test'
        request.scope['env'].MINIMAX_BASE_URL='https://example.invalid'
        async def complete(*args):
            if provider_mode=='timeout':raise TimeoutError()
            return 'This contains locked characters.'
        monkeypatch.setattr(core.MiniMaxProvider,'complete',complete)
    result=run(core.ai_lesson(request))
    assert result['source']=='fallback'
    assert validate(result['text'],' fj',12,1200)['valid']

def test_public_styles_and_private_gate(core):
    assert '<style>' not in core.GATE
    assert '<link rel="stylesheet" href="/auth.css">' in core.GATE
    assert 'cadence-public' in core.GATE
    result=run(core.auth_styles())
    assert result.media_type=='text/css' and b'#070a0e' in result.body

def registration_fixture(core, challenge, origin='https://localhost', rp='localhost'):
    import cbor2, hashlib
    from cryptography.hazmat.primitives.asymmetric import ec
    key=ec.generate_private_key(ec.SECP256R1()).public_key().public_numbers()
    credential_id=b'second-test-credential'
    cose=cbor2.dumps({1:2,3:-7,-1:1,-2:key.x.to_bytes(32,'big'),-3:key.y.to_bytes(32,'big')})
    auth=hashlib.sha256(rp.encode()).digest()+bytes([65])+(0).to_bytes(4,'big')+bytes(16)+len(credential_id).to_bytes(2,'big')+credential_id+cose
    client=json.dumps({'type':'webauthn.create','challenge':core.b64url(challenge),'origin':origin}).encode()
    return {'id':core.b64url(credential_id),'rawId':core.b64url(credential_id),'type':'public-key','response':{'clientDataJSON':core.b64url(client),'attestationObject':core.b64url(cbor2.dumps({'fmt':'none','attStmt':{},'authData':auth}))}}

@pytest.mark.parametrize('fault',[None,'challenge','origin','rp','expired','session'])
def test_real_registration_verification(core,setup,fault):
    db,request,routes=setup
    response=run(routes['/api/v1/auth/passkeys/add/options'](request))
    row=dict(db.conn.execute('SELECT * FROM webauthn_challenges').fetchone())
    request.cookies[core.CEREMONY_COOKIE]=response.headers['set-cookie'].split(';')[0].split('=',1)[1]
    credential=registration_fixture(core,b'wrong' if fault=='challenge' else row['challenge'],origin='https://wrong.example' if fault=='origin' else 'https://localhost',rp='wrong.example' if fault=='rp' else 'localhost')
    request.body={'credential':credential,'nickname':'Backup'}
    if fault=='expired':db.conn.execute("UPDATE webauthn_challenges SET expires_at='2000-01-01'")
    if fault=='session':request.cookies[core.COOKIE]='other-session'
    if fault:
        with pytest.raises(HTTPException):run(routes['/api/v1/auth/passkeys/add/verify'](request))
        assert db.conn.execute("SELECT COUNT(*) FROM passkey_credentials WHERE user_id='one'").fetchone()[0]==1
    else:
        run(routes['/api/v1/auth/passkeys/add/verify'](request))
        rows=db.conn.execute("SELECT user_id,nickname FROM passkey_credentials WHERE user_id='one'").fetchall()
        assert len(rows)==2 and rows[1]['nickname']=='Backup'
        with pytest.raises(HTTPException):run(routes['/api/v1/auth/passkeys/add/verify'](request))
