"""Account-scoped passkey management, extending the existing WebAuthn service."""
import json
import os
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from .passkeys import registration_options, verify_registration, b64url
from .sessions import COOKIE, token_hash

def install_routes(app, core):
    async def account(request):
        session = await core.require_session(request, 'learner')
        if not session.get('user_id'):
            raise HTTPException(403, 'Passkey sign-in required')
        return session

    @app.get('/api/v1/auth/passkeys')
    async def list_passkeys(request: Request):
        session = await account(request)
        result = await core.env(request).DB.prepare('SELECT credential_id,nickname,device_type,backed_up,created_at,last_used_at FROM passkey_credentials WHERE user_id=? ORDER BY created_at,credential_id').bind(session['user_id']).all()
        return {'passkeys': core.as_dict(result).get('results', []), 'maximum': 2}

    @app.post('/api/v1/auth/passkeys/add/options')
    async def add_options(request: Request):
        session = await account(request); binding = core.env(request)
        existing = (await list_passkeys(request))['passkeys']
        if len(existing) >= 2:
            raise HTTPException(409, 'Maximum 2. Remove one before adding another.')
        user = await core.first(binding.DB, 'SELECT webauthn_user_id,temporary_handle FROM users WHERE id=?', session['user_id'])
        challenge = os.urandom(32)
        challenge_id, nonce = await core.store_challenge(binding, 'registration', challenge, session['user_id'], user['webauthn_user_id'], user['temporary_handle'])
        session_hash = token_hash(request.cookies[COOKIE], core.required_secret(binding, 'SESSION_PEPPER'))
        await core.execute(binding.DB, 'UPDATE webauthn_challenges SET auth_session_hash=? WHERE id=?', session_hash, challenge_id)
        rp_id, _ = core.relying_party(request)
        options = registration_options(rp_id, user['temporary_handle'], bytes(user['webauthn_user_id']), challenge, [item['credential_id'] for item in existing])
        response = JSONResponse({'publicKey': options})
        response.headers['Set-Cookie'] = core.ceremony_cookie(nonce)
        return response

    @app.post('/api/v1/auth/passkeys/add/verify')
    async def add_verify(request: Request):
        session = await account(request); binding = core.env(request)
        session_hash = token_hash(request.cookies[COOKIE], core.required_secret(binding, 'SESSION_PEPPER'))
        row = await core.consume_challenge(request, 'registration', session_hash)
        if row['pending_user_id'] != session['user_id']:
            raise HTTPException(400, 'Passkey ceremony belongs to another account')
        body = await request.json(); rp_id, origin = core.relying_party(request)
        try:
            verified = verify_registration(body.get('credential', {}), bytes(row['challenge']), rp_id, origin)
        except Exception:
            raise HTTPException(400, 'Passkey registration could not be verified')
        timestamp = core.iso(core.now())
        credential_id = b64url(verified.credential_id)
        # Atomic predicate plus migration trigger protects both concurrent routes and other writers.
        inserted = await core.first(binding.DB, 'INSERT INTO passkey_credentials(credential_id,user_id,public_key,sign_count,device_type,backed_up,transports_json,created_at,nickname) SELECT ?,?,?,?,?,?,?,?,? WHERE (SELECT COUNT(*) FROM passkey_credentials WHERE user_id=?)<2 AND NOT EXISTS (SELECT 1 FROM passkey_credentials WHERE credential_id=?) RETURNING credential_id', credential_id, session['user_id'], verified.credential_public_key, verified.sign_count, verified.credential_device_type.value, int(verified.credential_backed_up), json.dumps(body.get('credential', {}).get('response', {}).get('transports', [])), timestamp, str(body.get('nickname', '')).strip()[:60], session['user_id'], credential_id)
        if not inserted:
            raise HTTPException(409, 'Maximum 2. Remove one before adding another.')
        return {'ok': True}

    @app.delete('/api/v1/auth/passkeys/{credential_id}')
    async def remove_passkey(credential_id: str, request: Request):
        session = await account(request)
        removed = await core.first(core.env(request).DB, 'DELETE FROM passkey_credentials WHERE credential_id=? AND user_id=? AND (SELECT COUNT(*) FROM passkey_credentials WHERE user_id=?)>1 RETURNING credential_id', credential_id, session['user_id'], session['user_id'])
        if not removed:
            raise HTTPException(409, 'Add a second passkey before removing this one, or refresh your passkey list.')
        return {'ok': True}

    return list_passkeys, add_options, add_verify, remove_passkey
