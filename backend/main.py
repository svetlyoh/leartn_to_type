from datetime import datetime, timedelta, timezone
import hmac
import hashlib
import json
import uuid
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from app.auth.lockout import failure_state
from app.auth.input import parse_urlencoded_pin
from app.auth.pin_kdf import create_verifier, valid_pin, verify
from app.auth.sessions import COOKIE, cookie_header, new_token, token_hash
from app.auth.passkeys import authentication_options, b64url, registration_options, verify_authentication, verify_registration
from app.ai.fallback import choose_fallback, constrained_pattern
from app.ai.minimax_provider import MiniMaxProvider
from app.ai.validator import validate
from app.curriculum.generated_curriculum import CURRICULUM
from app.progress import calculate_module_progress, capability_envelope
from app.security_headers import SECURITY_HEADERS

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
GENERIC = "Access unavailable. Check the PIN or try again later."
SAFE_MUTATION_EXEMPTIONS = {"/api/v1/auth/site-login", "/api/v1/admin/bootstrap", "/api/v1/auth/passkey/register/options", "/api/v1/auth/passkey/register/verify", "/api/v1/auth/passkey/login/options", "/api/v1/auth/passkey/login/verify"}
CEREMONY_COOKIE = "__Host-cadence_ceremony"
GATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Cadence</title><link rel="stylesheet" href="/auth.css"></head><body class="cadence-public"><section class="gate"><small>Focused touch-typing</small><h1>CADENCE</h1><p>Learn to type. Build your rhythm.</p><button id="signin">Sign in with passkey</button><p>New here?</p><button id="create" class="secondary">Create account</button><p id="status" role="status"></p></section><footer class="landing-footer"><button id="about" type="button">About</button> · Produced by Noverel · September 2026</footer><dialog id="about-dialog"><h2>CADENCE</h2><p>A focused touch-typing trainer built around technique, rhythm, and progress.</p><p>Produced by Noverel<br>September 2026</p><button id="close-about" type="button">Close</button></dialog><script>
const status=document.querySelector('#status');
const decode=s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/').padEnd(Math.ceil(s.length/4)*4,'=')),c=>c.charCodeAt(0));
const encode=b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const prep=o=>{o.challenge=decode(o.challenge);if(o.user)o.user.id=decode(o.user.id);if(o.excludeCredentials)o.excludeCredentials=o.excludeCredentials.map(x=>({...x,id:decode(x.id)}));if(o.allowCredentials)o.allowCredentials=o.allowCredentials.map(x=>({...x,id:decode(x.id)}));return o};
const pack=c=>({id:c.id,rawId:encode(c.rawId),type:c.type,authenticatorAttachment:c.authenticatorAttachment,response:{clientDataJSON:encode(c.response.clientDataJSON),...(c.response.attestationObject?{attestationObject:encode(c.response.attestationObject),transports:c.response.getTransports?.()||[]}:{authenticatorData:encode(c.response.authenticatorData),signature:encode(c.response.signature),userHandle:c.response.userHandle?encode(c.response.userHandle):null})},clientExtensionResults:c.getClientExtensionResults()});
async function run(kind){try{status.textContent='Waiting for your passkey…';const options=await fetch(`/api/v1/auth/passkey/${kind}/options`,{method:'POST'}).then(check);const credential=kind==='register'?await navigator.credentials.create({publicKey:prep(options.publicKey)}):await navigator.credentials.get({publicKey:prep(options.publicKey)});await fetch(`/api/v1/auth/passkey/${kind}/verify`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({credential:pack(credential)})}).then(check);location.assign('/app/')}catch(e){status.textContent=e.name==='NotAllowedError'?'Passkey request was canceled. Try again when ready.':'Passkey sign-in was unavailable. Please try again.'}}
async function check(r){if(!r.ok)throw new Error(String(r.status));return r.json()}
document.querySelector('#signin').onclick=()=>run('login');document.querySelector('#create').onclick=()=>run('register');
</script></body></html>"""
AUTH_CSS = ':root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;grid-template-rows:1fr auto;background:radial-gradient(circle at 50% -20%,#75d6bd18,transparent 40%),#070a0e;color:#edf4f2;font:16px system-ui}.gate{align-self:center;justify-self:center;width:min(460px,90vw);padding:clamp(1.5rem,5vw,3rem);background:#10171f;border:1px solid #283745;border-radius:16px;text-align:center;box-shadow:0 24px 80px #0008}small{color:#75d6bd;text-transform:uppercase;letter-spacing:.18em}h1{font-size:clamp(2rem,8vw,3rem);letter-spacing:.1em;margin:.35rem 0}p{color:#aebbc4}button{font:inherit;width:100%;margin-top:.8rem;padding:.9rem;border-radius:8px;border:1px solid #75d6bd;background:#75d6bd;color:#07120f;font-weight:750}button:focus-visible{outline:3px solid #75d6bd88;outline-offset:3px}button.secondary{background:transparent;color:#edf4f2;border-color:#405464}.landing-footer{padding:1.2rem;text-align:center;color:#91a0af;border-top:1px solid #283745}.landing-footer button{display:inline;width:auto;margin:0;padding:.25rem;background:transparent;border:0;color:#aebbc4;text-decoration:underline}dialog{max-width:420px;background:#10171f;color:#edf4f2;border:1px solid #405464;border-radius:16px;padding:2rem}dialog::backdrop{background:#05080dcc}#status{min-height:1.5em;color:#f0c979}'
AUTH_JS = r"""const status=document.querySelector('#status');
const decode=s=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/').padEnd(Math.ceil(s.length/4)*4,'=')),c=>c.charCodeAt(0));
const encode=b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
const prep=o=>{o.challenge=decode(o.challenge);if(o.user)o.user.id=decode(o.user.id);if(o.excludeCredentials)o.excludeCredentials=o.excludeCredentials.map(x=>({...x,id:decode(x.id)}));if(o.allowCredentials)o.allowCredentials=o.allowCredentials.map(x=>({...x,id:decode(x.id)}));return o};
const pack=c=>({id:c.id,rawId:encode(c.rawId),type:c.type,authenticatorAttachment:c.authenticatorAttachment,response:{clientDataJSON:encode(c.response.clientDataJSON),...(c.response.attestationObject?{attestationObject:encode(c.response.attestationObject),transports:c.response.getTransports?.()||[]}:{authenticatorData:encode(c.response.authenticatorData),signature:encode(c.response.signature),userHandle:c.response.userHandle?encode(c.response.userHandle):null})},clientExtensionResults:c.getClientExtensionResults()});
async function check(r){if(!r.ok)throw new Error(String(r.status));return r.json()}
async function run(kind){try{if(!window.PublicKeyCredential)throw new Error('unsupported');status.textContent='Waiting for your passkey…';const options=await fetch(`/api/v1/auth/passkey/${kind}/options`,{method:'POST'}).then(check);const credential=kind==='register'?await navigator.credentials.create({publicKey:prep(options.publicKey)}):await navigator.credentials.get({publicKey:prep(options.publicKey)});await fetch(`/api/v1/auth/passkey/${kind}/verify`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({credential:pack(credential)})}).then(check);location.assign('/app/')}catch(e){status.textContent=e.name==='NotAllowedError'?'Passkey request was canceled. Try again when ready.':e.message==='unsupported'?'Passkeys are not supported in this browser.':'Passkey sign-in was unavailable. Please try again.'}}
document.querySelector('#signin').addEventListener('click',()=>run('login'));document.querySelector('#create').addEventListener('click',()=>run('register'));"""
AUTH_JS += "\nconst about=document.querySelector('#about-dialog');document.querySelector('#about').addEventListener('click',()=>about.showModal());document.querySelector('#close-about').addEventListener('click',()=>about.close());"
# The production CSP intentionally rejects inline JavaScript. Keep the login logic
# in a same-origin resource while retaining the small server-rendered gate.
GATE = GATE[:GATE.index("<script>")] + '<script src="/auth.js" defer></script></body></html>'

def now(): return datetime.now(timezone.utc)
def iso(value): return value.isoformat().replace("+00:00", "Z")
def env(request): return request.scope["env"]
def as_dict(value): return None if value is None else (value.to_py() if hasattr(value, "to_py") else dict(value))
def required_secret(binding, name):
    value = getattr(binding, name, None)
    if value is None: raise HTTPException(503, "Service configuration unavailable")
    return str(value)
async def first(db, sql, *values): return as_dict(await db.prepare(sql).bind(*values).first())
async def execute(db, sql, *values): return await db.prepare(sql).bind(*values).run()
async def read_pin(request):
    if "application/json" in request.headers.get("content-type", ""):
        return str((await request.json()).get("pin", "")).strip()
    return parse_urlencoded_pin(await request.body())

@app.middleware("http")
async def harden(request, call_next):
    if request.method not in {"GET", "HEAD", "OPTIONS"} and request.url.path.startswith("/api/") and request.url.path not in SAFE_MUTATION_EXEMPTIONS:
        if request.headers.get("x-cadence-request") != "1":
            return JSONResponse({"detail": "Request verification failed"}, status_code=403, headers=SECURITY_HEADERS)
        origin = request.headers.get("origin")
        expected_origin = f"{request.url.scheme}://{request.url.netloc}"
        if origin and not hmac.compare_digest(origin.rstrip("/"), expected_origin.rstrip("/")):
            return JSONResponse({"detail": "Request verification failed"}, status_code=403, headers=SECURITY_HEADERS)
    response = await call_next(request)
    for key, value in SECURITY_HEADERS.items(): response.headers[key] = value
    if request.url.path.startswith("/api/") or request.url.path == "/": response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/", response_class=HTMLResponse)
async def gate(request: Request):
    session = await current_session(request)
    return RedirectResponse("/app/", 303) if session and session.get("user_id") else HTMLResponse(GATE)

@app.get("/healthz")
async def health(): return {"ok": True}

@app.get("/auth.css")
async def auth_styles():
    return Response(AUTH_CSS, media_type="text/css", headers={"Cache-Control":"public, max-age=300"})

@app.get("/auth.js")
async def auth_script():
    return Response(AUTH_JS, media_type="text/javascript", headers={"Cache-Control":"public, max-age=300"})

def relying_party(request):
    host = request.url.hostname or "localhost"
    origin = f"{request.url.scheme}://{request.url.netloc}"
    return host, origin

def ceremony_cookie(value):
    return f"{CEREMONY_COOKIE}={value}; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=300"

async def store_challenge(binding, ceremony_type, challenge, pending_user_id=None, webauthn_user_id=None, temporary_handle=None):
    challenge_id = f"chal_{uuid.uuid4().hex}"; nonce = new_token(); timestamp = now()
    await execute(binding.DB, "DELETE FROM webauthn_challenges WHERE expires_at<=?", iso(timestamp))
    await execute(binding.DB, "INSERT INTO webauthn_challenges(id,session_nonce,challenge,ceremony_type,pending_user_id,webauthn_user_id,temporary_handle,expires_at,created_at) VALUES(?,?,?,?,?,?,?,?,?)", challenge_id, token_hash(nonce, required_secret(binding, "SESSION_PEPPER")), challenge, ceremony_type, pending_user_id, webauthn_user_id, temporary_handle, iso(timestamp + timedelta(minutes=5)), iso(timestamp))
    return challenge_id, nonce

async def consume_challenge(request, ceremony_type, auth_session_hash=None):
    nonce = request.cookies.get(CEREMONY_COOKIE)
    if not nonce: raise HTTPException(400, "Passkey ceremony expired")
    binding = env(request)
    row = await first(binding.DB, "DELETE FROM webauthn_challenges WHERE session_nonce=? AND ceremony_type=? AND expires_at>? AND auth_session_hash IS ? RETURNING *", token_hash(nonce, required_secret(binding, "SESSION_PEPPER")), ceremony_type, iso(now()), auth_session_hash)
    if not row: raise HTTPException(400, "Passkey ceremony expired")
    return row

async def begin_user_session(request, user_id):
    binding = env(request); timestamp = now(); raw = new_token(); ttl = min(172800, int(str(getattr(binding, "SESSION_TTL_SECONDS", "172800"))))
    await execute(binding.DB, "INSERT INTO auth_sessions(session_hash,role,profile_id,created_at,last_seen_at,expires_at,user_id) VALUES(?,'learner',NULL,?,?,?,?)", token_hash(raw, required_secret(binding, "SESSION_PEPPER")), iso(timestamp), iso(timestamp), iso(timestamp + timedelta(seconds=ttl)), user_id)
    return raw

@app.post("/api/v1/auth/passkey/register/options")
async def passkey_register_options(request: Request):
    binding = env(request); user_id = f"usr_{uuid.uuid4().hex}"; handle = f"cadence-{uuid.uuid4().hex[:12]}"; user_handle = os.urandom(32); challenge = os.urandom(32); rp_id, _ = relying_party(request)
    _, nonce = await store_challenge(binding, "registration", challenge, user_id, user_handle, handle)
    response = JSONResponse({"publicKey": registration_options(rp_id, handle, user_handle, challenge)})
    response.headers["Set-Cookie"] = ceremony_cookie(nonce); return response

@app.post("/api/v1/auth/passkey/register/verify")
async def passkey_register_verify(request: Request):
    binding = env(request); body = await request.json(); challenge_row = await consume_challenge(request, "registration"); rp_id, origin = relying_party(request)
    try: verified = verify_registration(body.get("credential", {}), bytes(challenge_row["challenge"]), rp_id, origin)
    except Exception: raise HTTPException(400, "Passkey registration could not be verified")
    timestamp = iso(now()); credential_id = b64url(verified.credential_id)
    statements = [
        binding.DB.prepare("INSERT INTO users(id,webauthn_user_id,temporary_handle,account_status,created_at,updated_at) VALUES(?,?,?,'active',?,?)").bind(challenge_row["pending_user_id"], challenge_row["webauthn_user_id"], challenge_row["temporary_handle"], timestamp, timestamp),
        binding.DB.prepare("INSERT INTO passkey_credentials(credential_id,user_id,public_key,sign_count,device_type,backed_up,transports_json,created_at,last_used_at) VALUES(?,?,?,?,?,?,?,?,?)").bind(credential_id, challenge_row["pending_user_id"], verified.credential_public_key, verified.sign_count, str(verified.credential_device_type.value), 1 if verified.credential_backed_up else 0, json.dumps(body.get("credential",{}).get("response",{}).get("transports",[])), timestamp, timestamp),
        binding.DB.prepare("UPDATE profiles SET user_id=? WHERE user_id IS NULL").bind(challenge_row["pending_user_id"]),
    ]
    await binding.DB.batch(statements); raw = await begin_user_session(request, challenge_row["pending_user_id"])
    response = JSONResponse({"ok":True,"next":"/app/"}); response.headers.append("Set-Cookie", cookie_header(raw)); response.headers.append("Set-Cookie", f"{CEREMONY_COOKIE}=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"); return response

@app.post("/api/v1/auth/passkey/login/options")
async def passkey_login_options(request: Request):
    binding = env(request); challenge = os.urandom(32); rp_id, _ = relying_party(request); _, nonce = await store_challenge(binding, "authentication", challenge)
    response = JSONResponse({"publicKey": authentication_options(rp_id, challenge)}); response.headers["Set-Cookie"] = ceremony_cookie(nonce); return response

@app.post("/api/v1/auth/passkey/login/verify")
async def passkey_login_verify(request: Request):
    binding = env(request); body = await request.json(); supplied = body.get("credential", {}); credential_id = str(supplied.get("id", "")); row = await first(binding.DB, "SELECT p.*,u.account_status FROM passkey_credentials p JOIN users u ON u.id=p.user_id WHERE p.credential_id=?", credential_id); challenge_row = await consume_challenge(request, "authentication")
    if not row or row.get("account_status") != "active": raise HTTPException(401, "Passkey sign-in unavailable")
    rp_id, origin = relying_party(request)
    try: verified = verify_authentication(supplied, bytes(challenge_row["challenge"]), rp_id, origin, bytes(row["public_key"]), int(row["sign_count"]))
    except Exception: raise HTTPException(401, "Passkey sign-in unavailable")
    timestamp = iso(now()); await execute(binding.DB, "UPDATE passkey_credentials SET sign_count=?,device_type=?,backed_up=?,last_used_at=? WHERE credential_id=?", verified.new_sign_count, str(verified.credential_device_type.value), 1 if verified.credential_backed_up else 0, timestamp, credential_id)
    raw = await begin_user_session(request, row["user_id"]); response = JSONResponse({"ok":True,"next":"/app/"}); response.headers.append("Set-Cookie", cookie_header(raw)); response.headers.append("Set-Cookie", f"{CEREMONY_COOKIE}=; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"); return response

@app.get("/api/v1/auth/bootstrap-status")
async def bootstrap_status(request: Request):
    row = await first(env(request).DB, "SELECT value FROM app_meta WHERE key='bootstrapped'")
    return {"ready": bool(row and row.get("value") == "true")}

@app.post("/api/v1/admin/bootstrap")
async def bootstrap(request: Request):
    binding = env(request)
    supplied = request.headers.get("authorization", "").removeprefix("Bearer ")
    if not hmac.compare_digest(supplied, required_secret(binding, "BOOTSTRAP_TOKEN")): raise HTTPException(401, GENERIC)
    existing = await first(binding.DB, "SELECT value FROM app_meta WHERE key='bootstrapped'")
    if existing and existing.get("value") == "true": raise HTTPException(409, "Bootstrap is permanently closed")
    body = await request.json(); site_pin = str(body.get("site_pin", "")); admin_pin = str(body.get("admin_pin", ""))
    if not valid_pin(site_pin, "site") or not valid_pin(admin_pin, "admin"): raise HTTPException(422, "PIN policy not met")
    pepper = required_secret(binding, "PIN_PEPPER"); timestamp = iso(now())
    site_salt, site_hash, site_iterations = create_verifier(site_pin, pepper)
    admin_salt, admin_hash, admin_iterations = create_verifier(admin_pin, pepper)
    statements = [
        binding.DB.prepare("INSERT INTO pin_credentials(id,subject_type,subject_id,salt_b64,verifier_b64,kdf_iterations,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)").bind(f"pin_{uuid.uuid4().hex}", "site", "site", site_salt, site_hash, site_iterations, timestamp, timestamp),
        binding.DB.prepare("INSERT INTO pin_credentials(id,subject_type,subject_id,salt_b64,verifier_b64,kdf_iterations,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)").bind(f"pin_{uuid.uuid4().hex}", "admin", "admin", admin_salt, admin_hash, admin_iterations, timestamp, timestamp),
        binding.DB.prepare("INSERT INTO app_meta(key,value,updated_at) VALUES('bootstrapped','true',?)").bind(timestamp)]
    await binding.DB.batch(statements)
    return {"ok": True}

async def record_failure(db, credential):
    timestamp = now(); count, level, locked = failure_state(int(credential["failed_count"]), int(credential["lockout_level"]), timestamp)
    await execute(db, "UPDATE pin_credentials SET failed_count=?,lockout_level=?,locked_until=?,last_failed_at=?,updated_at=? WHERE id=?", count, level, iso(locked) if locked else None, iso(timestamp), iso(timestamp), credential["id"])

def credential_locked(credential):
    locked = credential.get("locked_until")
    return bool(locked and datetime.fromisoformat(locked.replace("Z", "+00:00")) > now())

async def verify_credential(binding, credential, pin):
    if not credential or credential_locked(credential):
        return False
    if not verify(pin, required_secret(binding, "PIN_PEPPER"), credential["salt_b64"], credential["verifier_b64"], int(credential["kdf_iterations"])):
        await record_failure(binding.DB, credential)
        return False
    timestamp = iso(now())
    await execute(binding.DB, "UPDATE pin_credentials SET failed_count=0,lockout_level=0,locked_until=NULL,last_failed_at=NULL,updated_at=? WHERE id=?", timestamp, credential["id"])
    return True

@app.post("/api/v1/auth/site-login")
async def site_login(request: Request):
    binding = env(request); pin = await read_pin(request)
    credential = await first(binding.DB, "SELECT * FROM pin_credentials WHERE subject_type='site' AND subject_id='site'")
    if not credential: raise HTTPException(401, GENERIC)
    if credential_locked(credential): raise HTTPException(429, GENERIC)
    if not await verify_credential(binding, credential, pin): raise HTTPException(401, GENERIC)
    timestamp = now()
    raw = new_token(); digest = token_hash(raw, required_secret(binding, "SESSION_PEPPER")); expires = timestamp + timedelta(seconds=int(str(binding.SESSION_TTL_SECONDS)))
    await execute(binding.DB, "INSERT INTO auth_sessions(session_hash,role,profile_id,created_at,last_seen_at,expires_at) VALUES(?,'site',NULL,?,?,?)", digest, iso(timestamp), iso(timestamp), iso(expires))
    html = "application/x-www-form-urlencoded" in request.headers.get("content-type", "")
    response = RedirectResponse("/app/", 303) if html else JSONResponse({"ok": True, "next": "/app/"})
    response.headers["Set-Cookie"] = cookie_header(raw); return response

async def current_session(request):
    raw = request.cookies.get(COOKIE)
    if not raw: return None
    binding = env(request); row = await first(binding.DB, "SELECT role,profile_id,user_id,name_confirmed,login_name,expires_at,revoked_at FROM auth_sessions WHERE session_hash=?", token_hash(raw, required_secret(binding, "SESSION_PEPPER")))
    if not row or row.get("revoked_at") or datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) <= now(): return None
    return row

async def rotate_session(request, role, profile_id=None):
    binding = env(request); raw_old = request.cookies.get(COOKIE); timestamp = now()
    if raw_old:
        await execute(binding.DB, "UPDATE auth_sessions SET revoked_at=? WHERE session_hash=?", iso(timestamp), token_hash(raw_old, required_secret(binding, "SESSION_PEPPER")))
    raw = new_token(); ttl = int(str(binding.ADMIN_SESSION_TTL_SECONDS if role == "admin" else binding.SESSION_TTL_SECONDS))
    await execute(binding.DB, "INSERT INTO auth_sessions(session_hash,role,profile_id,created_at,last_seen_at,expires_at) VALUES(?,?,?,?,?,?)", token_hash(raw, required_secret(binding, "SESSION_PEPPER")), role, profile_id, iso(timestamp), iso(timestamp), iso(timestamp + timedelta(seconds=ttl)))
    return raw

async def require_session(request, *roles):
    session = await current_session(request)
    if not session or session["role"] not in roles: raise HTTPException(403, "Access unavailable")
    if session["role"] == "learner" and session.get("user_id"):
        access = await first(env(request).DB, "SELECT u.account_status,u.accepted_activation_version,c.activation_version FROM users u CROSS JOIN app_access_config c WHERE u.id=? AND c.id=1", session["user_id"])
        if not access or access["account_status"] != "active" or access.get("accepted_activation_version") != access.get("activation_version"):
            raise HTTPException(403, "Current Cadence access PIN required")
        if not session.get("profile_id"):
            profile = await first(env(request).DB, "SELECT id FROM profiles WHERE user_id=? AND deleted_at IS NULL ORDER BY created_at LIMIT 1", session["user_id"])
            session["profile_id"] = profile.get("id") if profile else None
    return session

@app.get("/api/v1/auth/session")
async def auth_session(request: Request):
    session = await current_session(request)
    profile = None; activated = False; activation_changed = False
    if session and session.get("user_id"):
        access = await first(env(request).DB, "SELECT u.accepted_activation_version,c.activation_version FROM users u CROSS JOIN app_access_config c WHERE u.id=? AND c.id=1", session["user_id"])
        activated = bool(access and access.get("accepted_activation_version") == access.get("activation_version")); activation_changed = bool(access and access.get("accepted_activation_version") is not None and not activated)
        profile = await first(env(request).DB, "SELECT id,display_name,character_id,school_status,grade_level,theme_id,sound_enabled FROM profiles WHERE user_id=? AND deleted_at IS NULL ORDER BY created_at LIMIT 1", session["user_id"])
    elif session and session.get("profile_id"):
        profile = await first(env(request).DB, "SELECT id,display_name,character_id,school_status,grade_level,theme_id,sound_enabled FROM profiles WHERE id=? AND deleted_at IS NULL", session["profile_id"])
    # The durable profile, not a per-login flag, decides whether onboarding is needed.
    return {"authenticated": bool(session and session.get("user_id")), "role": session["role"] if session and session.get("user_id") else None, "activated": activated, "activation_changed": activation_changed, "name_required": bool(session and session.get("user_id") and activated and profile is None), "profile": profile}

@app.post("/api/v1/auth/activate")
async def activate(request: Request):
    session = await current_session(request)
    if not session or not session.get("user_id"): raise HTTPException(401, "Passkey sign-in required")
    binding = env(request); pin = await read_pin(request); credential = await first(binding.DB, "SELECT * FROM pin_credentials WHERE subject_type='site' AND subject_id='site'")
    if credential and credential_locked(credential): raise HTTPException(429, GENERIC)
    if not await verify_credential(binding, credential, pin): raise HTTPException(401, GENERIC)
    access = await first(binding.DB, "SELECT activation_version FROM app_access_config WHERE id=1"); timestamp = iso(now())
    await execute(binding.DB, "UPDATE users SET accepted_activation_version=?,activation_verified_at=?,updated_at=? WHERE id=?", int(access["activation_version"]), timestamp, timestamp, session["user_id"])
    return {"ok":True,"next":"/app/"}

@app.post("/api/v1/auth/name")
async def set_login_name(request: Request):
    session = await require_session(request, "learner"); binding = env(request); body = await request.json(); name = str(body.get("name", "")).strip() or "MCP"; school_status=str(body.get("school_status","skipped")); grade_level=str(body.get("grade_level","")).strip() or None
    if len(name) > 40: raise HTTPException(422, "Name must be 40 characters or fewer")
    if school_status not in {"student","not_student","skipped"}: raise HTTPException(422,"School status is invalid")
    timestamp = iso(now()); profile = await first(binding.DB, "SELECT id FROM profiles WHERE user_id=? AND deleted_at IS NULL ORDER BY created_at LIMIT 1", session["user_id"])
    statements = []
    if profile:
        profile_id = profile["id"]
        statements.append(binding.DB.prepare("UPDATE profiles SET display_name=?,updated_at=? WHERE id=?").bind(name,timestamp,profile_id))
    else:
        profile_id = f"prof_{uuid.uuid4().hex}"
        statements.extend([binding.DB.prepare("INSERT INTO profiles(id,display_name,pin_required,save_version,curriculum_version,character_id,user_id,school_status,grade_level,created_at,updated_at) VALUES(?,?,0,1,?,?,?,?,?,?,?)").bind(profile_id,name,str(binding.CURRICULUM_VERSION),"runner_01",session["user_id"],school_status,grade_level,timestamp,timestamp),binding.DB.prepare("INSERT INTO progress(profile_id,save_version,curriculum_version,stage_id,unlocked_keys_json,current_lesson_id,resume_json,revision,updated_at) VALUES(?,1,?,'module_01','[\"f\",\"j\",\" \"]','builtin_01','{}',1,?)").bind(profile_id,str(binding.CURRICULUM_VERSION),timestamp)])
    statements.append(binding.DB.prepare("UPDATE auth_sessions SET profile_id=?,name_confirmed=1,login_name=?,last_seen_at=? WHERE session_hash=?").bind(profile_id,name,timestamp,token_hash(request.cookies.get(COOKIE),required_secret(binding,"SESSION_PEPPER"))))
    await binding.DB.batch(statements); return {"ok":True,"name":name}

@app.post("/api/v1/auth/admin-login")
async def admin_login(request: Request):
    await require_session(request, "site"); binding = env(request); pin = await read_pin(request)
    credential = await first(binding.DB, "SELECT * FROM pin_credentials WHERE subject_type='admin' AND subject_id='admin'")
    if credential and credential_locked(credential): raise HTTPException(429, GENERIC)
    if not await verify_credential(binding, credential, pin): raise HTTPException(401, GENERIC)
    raw = await rotate_session(request, "admin"); response = JSONResponse({"ok": True}); response.headers["Set-Cookie"] = cookie_header(raw); return response

@app.get("/api/v1/profiles")
async def list_profiles(request: Request):
    session = await require_session(request, "learner"); result = await env(request).DB.prepare("SELECT id,display_name,0 pin_required,is_test_profile,character_id FROM profiles WHERE user_id=? AND deleted_at IS NULL ORDER BY created_at").bind(session["user_id"]).all(); data = as_dict(result)
    return data.get("results", []) if isinstance(data, dict) else []

@app.post("/api/v1/profiles")
async def create_profile(request: Request):
    session = await require_session(request, "learner"); binding = env(request); body = await request.json(); name = str(body.get("display_name", "")).strip(); character = str(body.get("character_id", "runner_01")); school_status = str(body.get("school_status", "skipped")); grade_level = str(body.get("grade_level", "")).strip() or None; allowed = {"runner_01","runner_02","focus_01","focus_02"}
    if not 1 <= len(name) <= 40 or character not in allowed or school_status not in {"student","not_student","skipped"}: raise HTTPException(422, "Profile data is invalid")
    existing = await first(binding.DB, "SELECT id FROM profiles WHERE user_id=? AND deleted_at IS NULL", session["user_id"])
    if existing: raise HTTPException(409, "This account already has a player")
    profile_id = f"prof_{uuid.uuid4().hex}"; timestamp = iso(now())
    statements = [binding.DB.prepare("INSERT INTO profiles(id,display_name,pin_required,save_version,curriculum_version,character_id,user_id,school_status,grade_level,created_at,updated_at) VALUES(?,?,0,1,?,?,?,?,?,?,?)").bind(profile_id,name,str(binding.CURRICULUM_VERSION),character,session["user_id"],school_status,grade_level,timestamp,timestamp), binding.DB.prepare("INSERT INTO progress(profile_id,save_version,curriculum_version,stage_id,unlocked_keys_json,current_lesson_id,resume_json,revision,updated_at) VALUES(?,1,?,'module_01','[\"f\",\"j\",\" \"]','builtin_01','{}',1,?)").bind(profile_id,str(binding.CURRICULUM_VERSION),timestamp), binding.DB.prepare("UPDATE users SET onboarding_completed=1,updated_at=? WHERE id=?").bind(timestamp,session["user_id"])]
    await binding.DB.batch(statements); return {"id": profile_id, "display_name": name, "pin_required": False, "character_id": character}

@app.patch("/api/v1/profile/character")
async def update_character(request: Request):
    session = await require_session(request, "learner"); character = str((await request.json()).get("character_id", "")); allowed = {"runner_01","runner_02","focus_01","focus_02"}
    if character not in allowed: raise HTTPException(422, "Unknown character")
    await execute(env(request).DB, "UPDATE profiles SET character_id=?,updated_at=? WHERE id=? AND deleted_at IS NULL", character, iso(now()), session["profile_id"])
    return {"ok": True, "character_id": character}

@app.get("/api/v1/settings")
async def get_settings(request: Request):
    session = await require_session(request, "learner")
    row = await first(env(request).DB, "SELECT theme_id,sound_enabled,ui_prefs_json FROM profiles WHERE id=? AND deleted_at IS NULL", session["profile_id"])
    prefs = json.loads((row or {}).get("ui_prefs_json") or "{}")
    return {"theme_id":(row or {}).get("theme_id") or "midnight","sound_enabled":bool((row or {}).get("sound_enabled",1)),"reduce_motion":bool(prefs.get("reduce_motion",False)),"hand_guidance_enabled":bool(prefs.get("hand_guidance_enabled",True))}

@app.patch("/api/v1/settings")
async def update_settings(request: Request):
    session = await require_session(request, "learner"); binding = env(request); body = await request.json()
    current = await first(binding.DB, "SELECT theme_id,sound_enabled,ui_prefs_json FROM profiles WHERE id=?", session["profile_id"])
    if not current: raise HTTPException(404, "Profile unavailable")
    theme = str(body.get("theme_id", current.get("theme_id") or "midnight")); themes = {"midnight","soft-slate","soft-plum"}
    if theme not in themes: raise HTTPException(422, "Unknown theme")
    sound = bool(body.get("sound_enabled", bool(current.get("sound_enabled",1)))); prefs = json.loads(current.get("ui_prefs_json") or "{}")
    for key in ("reduce_motion","hand_guidance_enabled"):
        if key in body: prefs[key] = bool(body[key])
    await execute(binding.DB, "UPDATE profiles SET theme_id=?,sound_enabled=?,ui_prefs_json=?,updated_at=? WHERE id=?", theme, 1 if sound else 0, json.dumps(prefs,separators=(",",":")), iso(now()), session["profile_id"])
    return {"ok":True,"theme_id":theme,"sound_enabled":sound,"reduce_motion":bool(prefs.get("reduce_motion",False)),"hand_guidance_enabled":bool(prefs.get("hand_guidance_enabled",True))}

def phase_for_order(order):
    return "Foundations" if order <= 16 else "Fluency Tools" if order <= 32 else "Reading & American Literature" if order <= 48 else "Modern Fluency"

@app.get("/api/v1/progress-dashboard")
async def progress_dashboard(request: Request):
    session = await require_session(request, "learner"); binding = env(request)
    profile = await first(binding.DB, "SELECT display_name,character_id,school_status,grade_level,theme_id,sound_enabled FROM profiles WHERE id=?", session["profile_id"])
    progress = await first(binding.DB, "SELECT stage_id,current_lesson_id,resume_json,updated_at FROM progress WHERE profile_id=?", session["profile_id"])
    stage = curriculum_stage((progress or {}).get("stage_id")) or CURRICULUM["stages"][0]; order = int(stage.get("order",1))
    module = await module_progress(request)
    rows = await binding.DB.prepare("SELECT started_at,stage_id,net_wpm,accuracy,cadence_score,active_duration_ms FROM training_sessions WHERE profile_id=? AND mode='normal' ORDER BY started_at DESC LIMIT 10").bind(session["profile_id"]).all(); history = as_dict(rows).get("results",[])
    aggregates = await first(binding.DB, "SELECT AVG(net_wpm) avg_wpm,AVG(accuracy) avg_accuracy,MAX(net_wpm) best_wpm,COUNT(*) completed,COALESCE(SUM(active_duration_ms),0) practice_ms FROM training_sessions WHERE profile_id=? AND mode='normal'", session["profile_id"])
    keys = await binding.DB.prepare("SELECT display_key,mastery,attempts,errors,total_reaction_ms,last_practiced FROM key_mastery WHERE profile_id=? AND introduced=1 ORDER BY mastery ASC,errors DESC").bind(session["profile_id"]).all(); key_rows = as_dict(keys).get("results",[])
    resume = json.loads((progress or {}).get("resume_json") or "{}")
    return {"profile":profile,"curriculum":{"phase":phase_for_order(order),"module_id":stage["id"],"module_index":order,"module_count":len(CURRICULUM["stages"]),"module_title":stage["title"],"mastery_percent":module["progress_percent"]},"recent":{"last":history[0] if history else None,"average_wpm":aggregates.get("avg_wpm"),"average_accuracy":aggregates.get("avg_accuracy"),"best_wpm":aggregates.get("best_wpm"),"completed_sessions":int(aggregates.get("completed") or 0),"practice_ms":int(aggregates.get("practice_ms") or 0)},"weak_keys":[item["display_key"] for item in key_rows[:3] if int(item.get("attempts") or 0)>=4],"strong_keys":[item["display_key"] for item in sorted(key_rows,key=lambda item:float(item.get("mastery") or 0),reverse=True)[:3]],"history":history,"resume":resume,"progress_updated_at":(progress or {}).get("updated_at")}

@app.get("/api/v1/weak-key-practice")
async def weak_key_practice(request: Request):
    session = await require_session(request, "learner"); binding = env(request); progress = await first(binding.DB,"SELECT stage_id FROM progress WHERE profile_id=?",session["profile_id"]); stage = curriculum_stage((progress or {}).get("stage_id")) or CURRICULUM["stages"][0]
    rows = await binding.DB.prepare("SELECT display_key,mastery,attempts,errors,total_reaction_ms FROM key_mastery WHERE profile_id=? AND introduced=1 AND display_key IN (SELECT value FROM json_each(?)) ORDER BY mastery ASC,errors DESC,(CASE WHEN attempts>0 THEN total_reaction_ms/attempts ELSE 0 END) DESC LIMIT 3").bind(session["profile_id"],json.dumps(stage["allowedCharacters"])).all(); evidence = [item for item in as_dict(rows).get("results",[]) if int(item.get("attempts") or 0)>=4]
    focus = [item["display_key"] for item in evidence]; base = stage["fallbackDrills"][0]
    if not focus: return {"diagnostic":True,"focus_keys":[],"text":base,"description":"I don't have a clear weak-key pattern yet. Let's run a short diagnostic round."}
    words = [word for word in base.split() if any(key.lower() in word.lower() for key in focus)] or base.split(); text = " ".join((words * max(2,24//max(1,len(words))))[:24])
    return {"diagnostic":False,"focus_keys":focus,"text":text,"description":f"Focused practice for {', '.join(key.upper() for key in focus)}."}

@app.post("/api/v1/session-checkpoint")
async def session_checkpoint(request: Request):
    session = await require_session(request, "learner"); binding = env(request); body = await request.json(); timestamp = iso(now())
    if int(body.get("save_version", 0)) != 1: raise HTTPException(422, "Unsupported save version")
    row = await first(binding.DB, "SELECT revision,resume_json FROM progress WHERE profile_id=?", session["profile_id"])
    if not row: raise HTTPException(409, "Profile progress is unavailable")
    previous = json.loads(row.get("resume_json") or "{}")
    checkpoint_id = str(body.get("local_checkpoint_id", ""))
    if checkpoint_id and previous.get("local_checkpoint_id") == checkpoint_id:
        return {"saved_at": row.get("updated_at", timestamp), "revision": int(row["revision"]), "idempotent": True}
    client_revision = body.get("revision")
    if client_revision is not None and int(client_revision) != int(row["revision"]):
        raise HTTPException(409, "A newer checkpoint already exists")
    revision = int(row["revision"]) + 1
    await execute(binding.DB, "UPDATE progress SET stage_id=?,current_lesson_id=?,resume_json=?,revision=?,updated_at=? WHERE profile_id=?", str(body.get("stage_id","orientation")), str(body.get("lesson_id","orientation-1")), json.dumps(body,separators=(",",":")), revision, timestamp, session["profile_id"])
    return {"saved_at": timestamp, "revision": revision}

def finger_for(key):
    value = key.lower()
    groups = [("left","pinky","qaz"),("left","ring","wsx"),("left","middle","edc"),("left","index","rtfgvb"),("right","index","yuhjnm"),("right","middle","ik,"),("right","ring","ol."),("right","pinky","p;/'[]")]
    if value == " ": return "either","thumb"
    return next(((hand,finger) for hand,finger,keys in groups if value in keys),("either","pinky"))

@app.post("/api/v1/training-sessions")
async def complete_training_session(request: Request):
    session = await require_session(request,"learner"); binding = env(request); body = await request.json(); sync_id = str(body.get("sync_id", ""))
    if not sync_id: raise HTTPException(422,"sync_id required")
    existing = await first(binding.DB,"SELECT id FROM training_sessions WHERE sync_id=?",sync_id)
    if existing: return {"ok":True,"idempotent":True}
    progress = await first(binding.DB,"SELECT stage_id FROM progress WHERE profile_id=?",session["profile_id"]); stage_id = (progress or {}).get("stage_id")
    if body.get("stage_id") != stage_id: raise HTTPException(409,"Training capabilities changed. Refresh and try again.")
    stage = curriculum_stage(stage_id); allowed = set((stage or {}).get("allowedCharacters", "")); key_stats = body.get("key_stats") or {}
    if any(key not in allowed for key in key_stats): raise HTTPException(422,"Key evidence is outside the current curriculum")
    timestamp = iso(now()); record_id = f"sess_{uuid.uuid4().hex}"; attempts=max(0,int(body.get("char_attempts",0))); correct=max(0,int(body.get("correct_chars",0))); errors=max(0,int(body.get("error_count",0)))
    statements=[binding.DB.prepare("INSERT INTO training_sessions(id,sync_id,profile_id,lesson_id,stage_id,mode,difficulty,started_at,ended_at,duration_ms,active_duration_ms,char_attempts,correct_chars,error_count,hint_count,gross_wpm,net_wpm,accuracy,cadence_score,cadence_cv,stall_count,summary_json,created_at) VALUES(?,?,?,?,?,'normal','practice',?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)").bind(record_id,sync_id,session["profile_id"],str(body.get("lesson_id") or ""),stage_id,str(body.get("started_at") or timestamp),timestamp,int(body.get("duration_ms") or body.get("active_duration_ms") or 0),int(body.get("active_duration_ms") or 0),attempts,correct,errors,int(body.get("hint_count") or 0),float(body.get("gross_wpm") or 0),float(body.get("net_wpm") or 0),float(body.get("accuracy") or 0),body.get("cadence_score"),body.get("cadence_cv"),int(body.get("stall_count") or 0),json.dumps({"source":body.get("source","authored")},separators=(",",":")),timestamp)]
    for key,stat in key_stats.items():
        hand,finger=finger_for(key); stat_attempts=max(0,int(stat.get("attempts",0))); stat_correct=max(0,int(stat.get("correct",0))); stat_errors=max(0,int(stat.get("errors",0))); reaction=max(0,int(stat.get("totalReactionMs",0))); mastery=(stat_correct/stat_attempts) if stat_attempts else 0
        statements.append(binding.DB.prepare("INSERT INTO key_mastery(profile_id,key_code,display_key,hand,finger,introduced,attempts,correct,errors,total_reaction_ms,mastery,last_practiced,updated_at) VALUES(?,?,?,?,?,1,?,?,?,?,?,?,?) ON CONFLICT(profile_id,key_code) DO UPDATE SET attempts=attempts+excluded.attempts,correct=correct+excluded.correct,errors=errors+excluded.errors,total_reaction_ms=total_reaction_ms+excluded.total_reaction_ms,mastery=CAST(correct+excluded.correct AS REAL)/MAX(1,attempts+excluded.attempts),last_practiced=excluded.last_practiced,updated_at=excluded.updated_at").bind(session["profile_id"],key,key,hand,finger,stat_attempts,stat_correct,stat_errors,reaction,mastery,timestamp,timestamp))
    statements.append(binding.DB.prepare("UPDATE profiles SET last_training_at=?,updated_at=? WHERE id=?").bind(timestamp,timestamp,session["profile_id"]))
    await binding.DB.batch(statements); return {"ok":True,"session_id":record_id}

@app.get("/api/v1/module-progress")
async def module_progress(request: Request):
    session = await require_session(request, "learner"); binding = env(request)
    row = await first(binding.DB, "SELECT stage_id FROM progress WHERE profile_id=?", session["profile_id"]); stage_id = row["stage_id"] if row else "orientation"
    stage = curriculum_stage(stage_id) or CURRICULUM["stages"][0]
    minimum = int(stage.get("minimumCompletedDrills", 4)); target_accuracy = float(stage.get("targetAccuracy", .92)); target_mastery = float(stage.get("targetMastery", .75)); max_hint_rate = float(stage.get("maxHintRate", .15))
    aggregate = await first(binding.DB, "SELECT COUNT(*) completed,COALESCE(SUM(correct_chars),0) correct_chars,COALESCE(SUM(char_attempts),0) attempts,COALESCE(SUM(hint_count),0) hints FROM training_sessions WHERE profile_id=? AND stage_id=? AND mode='normal'", session["profile_id"], stage_id)
    completed = int(aggregate.get("completed", 0)); attempts = int(aggregate.get("attempts", 0)); recent_accuracy = (int(aggregate.get("correct_chars", 0)) / attempts) if attempts else None; hint_rate = (int(aggregate.get("hints", 0)) / attempts) if attempts else 0
    mastery_rows = await binding.DB.prepare("SELECT display_key,mastery FROM key_mastery WHERE profile_id=?").bind(session["profile_id"]).all(); mastery_data = as_dict(mastery_rows); mastery_map = {item["display_key"]:float(item["mastery"]) for item in mastery_data.get("results", [])}
    introduced = [{"key":key,"value":mastery_map.get(key,0),"target":target_mastery,"met":mastery_map.get(key,0)>=target_mastery} for key in stage.get("introducedKeys", [])]
    percent, ready = calculate_module_progress(completed, minimum, recent_accuracy, target_accuracy, introduced, target_mastery, hint_rate, max_hint_rate)
    return {"stage_id":stage_id,"module_index":int(stage.get("order",1)),"module_count":len(CURRICULUM["stages"]),"title":stage["title"],"progress_percent":percent,"ready_to_advance":ready,"criteria":{"completed_drills":{"value":completed,"target":minimum,"met":completed>=minimum},"accuracy":{"value":recent_accuracy,"target":target_accuracy,"met":recent_accuracy is not None and recent_accuracy>=target_accuracy},"introduced_key_mastery":introduced,"hint_rate":{"value":hint_rate,"max":max_hint_rate,"met":hint_rate<=max_hint_rate}}}

def curriculum_stage(stage_id):
    return next((stage for stage in CURRICULUM["stages"] if stage["id"] == stage_id), None)

@app.get("/api/v1/ai/status")
async def ai_status(request: Request):
    await require_session(request, "learner", "admin")
    configured = getattr(env(request), "MINIMAX_API_KEY", None) is not None
    return {"state":"ready" if configured else "builtin","lesson_generation_available":configured,"explanations_available":configured}

@app.get("/api/v1/training/options")
async def training_options(request: Request):
    session = await require_session(request, "learner"); binding = env(request); progress = await first(binding.DB, "SELECT stage_id FROM progress WHERE profile_id=?", session["profile_id"]); stage_id = progress["stage_id"] if progress else "orientation"; stage = curriculum_stage(stage_id) or CURRICULUM["stages"][0]; capability = capability_envelope(stage)
    weak = await first(binding.DB, "SELECT COUNT(*) count FROM key_mastery WHERE profile_id=? AND attempts>=8 AND mastery<0.55", session["profile_id"]); has_weak = int(weak.get("count",0)) > 0
    text_enabled = int(stage.get("order",1)) >= 5
    actions=[{"id":"continue","label":"Continue the plan","enabled":True},{"id":"reshuffle","label":"Give me another short pattern","enabled":True},{"id":"text_to_type","label":"Give me text to type","enabled":text_enabled,"reason":None if text_enabled else "Full text unlocks after you learn more letters."},{"id":"weak_key","label":"Practice weak keys","enabled":has_weak,"reason":None if has_weak else "Available after I spot a repeated pattern."}]
    durations = [] if not text_enabled else ([30,60,120] if capability["long"] else [30,60])
    return {"capability_band":capability["band"],"actions":actions,"passage_options":{"durations_seconds":durations,"topic_passages":capability["topic"],"long_form":capability["long"],"numbers":capability["numbers"],"symbols":capability["symbols"]}}

@app.post("/api/v1/ai/lesson")
async def ai_lesson(request: Request):
    session = await require_session(request, "learner"); binding = env(request); body = await request.json(); progress = await first(binding.DB, "SELECT stage_id FROM progress WHERE profile_id=?", session["profile_id"]); stage_id = progress["stage_id"] if progress else "orientation"
    if str(body.get("stage_id", stage_id)) != stage_id: raise HTTPException(409, "Training capabilities changed. Refresh and try again.")
    stage = curriculum_stage(stage_id)
    if not stage: raise HTTPException(422, "Unknown curriculum stage")
    if body.get("curriculum_version", CURRICULUM["version"]) != CURRICULUM["version"]: raise HTTPException(409, "Curriculum changed. Refresh and try again.")
    allowed = stage["allowedCharacters"]; supplied = body.get("allowed_keys")
    if supplied is not None and set(supplied) != set(allowed): raise HTTPException(422, "Allowed-key mismatch")
    mode = str(body.get("mode", "reshuffle")); allowed_modes = {"reshuffle","weak_key","harder","easier","challenge","custom_passage","text_to_type"}
    if mode not in allowed_modes: raise HTTPException(422, "Unsupported training action")
    capability = capability_envelope(stage); requested = int(body.get("target_characters", 60)); duration = body.get("target_duration_seconds")
    if duration is not None:
        wpm_row = await first(binding.DB, "SELECT AVG(net_wpm) wpm FROM training_sessions WHERE profile_id=? AND mode='normal' AND active_duration_ms>=30000", session["profile_id"]); sustained_wpm = float(wpm_row.get("wpm") or 25); requested = round(sustained_wpm * 5 * max(15,min(int(duration),300)) / 60)
    target = max(capability["min"], min(requested, capability["max"])); topic = str(body.get("topic", "")).strip().lower()[:60]
    if not capability["topic"]: topic = ""
    canonical = "|".join([str(binding.CURRICULUM_VERSION),stage_id,"".join(sorted(allowed)),mode,str(target),topic,"rev4-v1"]); constraint_hash = hashlib.sha256(canonical.encode()).hexdigest()
    recent = [str(value)[:1200] for value in body.get("recent_texts", [])[:8]]
    try:
        cached = await first(binding.DB, "SELECT id,text FROM generated_content WHERE constraint_hash=? AND profile_id=? ORDER BY last_used_at ASC,created_at DESC LIMIT 1", constraint_hash, session["profile_id"])
    except Exception:
        cached = None
    if cached and (cached["text"] in recent or not validate(cached["text"], allowed, 12, 1200)["valid"]): cached = None
    if cached:
        try: await execute(binding.DB, "UPDATE generated_content SET last_used_at=? WHERE id=?", iso(now()), cached["id"])
        except Exception: pass  # Cache bookkeeping must not prevent valid practice.
        kind = "passage" if capability["topic"] and (mode in {"custom_passage","text_to_type"} or len(cached["text"])>220) else "drill"
        return {"lesson_id":cached["id"],"schema_version":1,"text":cached["text"],"focus_keys":body.get("focus_keys",[]),"estimated_characters":len(cached["text"]),"estimated_duration_seconds":int(duration) if duration is not None else None,"lesson_kind":kind,"source":"cache","validation":{"passed":True}}
    text = None; source = "fallback"; validation = None
    provider_key = getattr(binding, "MINIMAX_API_KEY", None)
    if provider_key is not None:
        provider = MiniMaxProvider(str(provider_key),str(binding.MINIMAX_BASE_URL),str(binding.MINIMAX_MODEL)); system = f"Create only typing practice text. Use exclusively these characters: {repr(allowed)}. Return plain text only, about {target} characters. Never add labels or markdown."
        user = f"Mode: {'pattern drill' if not capability['topic'] else mode}. Topic: {topic or 'neutral training'}. Keep it calm and teen-appropriate."
        try:
            for attempt in range(2):
                candidate = await provider.complete(system,user if attempt == 0 else user+" Your prior response violated constraints; correct it exactly.")
                validation = validate(candidate,allowed,max(12,int(target*.7)),min(1200,max(40,int(target*1.35))))
                if validation["valid"]: text=validation["text"];source="ai";break
        except Exception:
            text = None
    if text is None:
        text = constrained_pattern(allowed, body.get("focus_keys", []), stage_id, recent, target, str(body.get("request_id", ""))) if not capability["topic"] else choose_fallback(stage["fallbackDrills"],constraint_hash)
        validation = validate(text, allowed, 12, 1200)
        if not validation["valid"] or text in recent:
            text = constrained_pattern(allowed, body.get("focus_keys", []), stage_id, recent, target, str(body.get("request_id", "")))
            validation = validate(text, allowed, 12, 1200)
    lesson_id=f"les_{uuid.uuid4().hex}"; timestamp=iso(now())
    try:
        await execute(binding.DB,"INSERT INTO generated_content(id,profile_id,constraint_hash,request_mode,stage_id,difficulty,focus_keys_json,topic,text,provider,model,prompt_version,validation_json,created_at,last_used_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",lesson_id,session["profile_id"],constraint_hash,mode,stage_id,str(body.get("difficulty","practice")),json.dumps(body.get("focus_keys",[])),topic or None,text,"minimax" if source=="ai" else "builtin",str(binding.MINIMAX_MODEL),"rev4-v1",json.dumps(validation),timestamp,timestamp)
    except Exception:
        pass  # A valid local drill is still usable when the optional cache write fails.
    kind = "passage" if capability["topic"] and (mode in {"custom_passage","text_to_type"} or len(text)>220) else "drill"
    return {"lesson_id":lesson_id,"schema_version":1,"text":text,"focus_keys":body.get("focus_keys",[]),"estimated_characters":len(text),"estimated_duration_seconds":int(duration) if duration is not None else None,"lesson_kind":kind,"source":source,"validation":{"passed":True}}

@app.post("/api/v1/auth/logout")
async def logout(request: Request):
    raw = request.cookies.get(COOKIE)
    if raw:
        binding = env(request); await execute(binding.DB, "UPDATE auth_sessions SET revoked_at=? WHERE session_hash=?", iso(now()), token_hash(raw, required_secret(binding, "SESSION_PEPPER")))
    response = JSONResponse({"ok": True}); response.delete_cookie(COOKIE, path="/", secure=True, httponly=True, samesite="strict"); return response

async def serve_asset(path, request):
    session = await current_session(request)
    if not session or not session.get("user_id"): raise HTTPException(401, "Passkey sign-in required")
    result = await env(request).ASSETS.fetch(f"https://assets.local/app/{path or 'index.html'}")
    return Response(await result.bytes(), status_code=result.status, headers=result.headers)

@app.get("/app")
async def private_app_redirect(request: Request):
    session = await current_session(request)
    if not session or not session.get("user_id"): return RedirectResponse("/", 303)
    return RedirectResponse("/app/", 308)

@app.get("/app/{path:path}")
async def private_assets(path: str, request: Request): return await serve_asset(path, request)

import sys
from app.auth.management import install_routes
install_routes(app, sys.modules[__name__])

from workers import asgi
Default = asgi.entrypoint(app)
