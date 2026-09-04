from datetime import datetime, timedelta, timezone
import hmac
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from app.auth.lockout import failure_state
from app.auth.input import parse_urlencoded_pin
from app.auth.pin_kdf import create_verifier, valid_pin, verify
from app.auth.sessions import COOKIE, cookie_header, new_token, token_hash
from app.security_headers import SECURITY_HEADERS

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
GENERIC = "Access unavailable. Check the PIN or try again later."
GATE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Cadence access</title><style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b1017;color:#e8edf2;font:16px system-ui}.gate{width:min(360px,90vw);padding:2.5rem;background:#131b25;border:1px solid #263343;border-radius:14px}small{color:#75d6bd;text-transform:uppercase;letter-spacing:.15em}input,button{width:100%;box-sizing:border-box;margin-top:1rem;padding:.85rem;border-radius:8px;border:1px solid #34465a;background:#0d141c;color:white}button{background:#75d6bd;color:#07120f;font-weight:bold}</style></head><body><form class="gate" method="post" action="/api/v1/auth/site-login"><small>Cadence</small><h1>Private training access</h1><label>Enter access PIN<input name="pin" type="password" inputmode="numeric" minlength="6" maxlength="12" required autofocus></label><button>Enter training</button></form></body></html>"""

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
    response = await call_next(request)
    for key, value in SECURITY_HEADERS.items(): response.headers[key] = value
    if request.url.path.startswith("/api/") or request.url.path == "/": response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/", response_class=HTMLResponse)
async def gate(): return HTMLResponse(GATE)

@app.get("/healthz")
async def health(): return {"ok": True}

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

@app.post("/api/v1/auth/site-login")
async def site_login(request: Request):
    binding = env(request); pin = await read_pin(request)
    credential = await first(binding.DB, "SELECT * FROM pin_credentials WHERE subject_type='site' AND subject_id='site'")
    if not credential: raise HTTPException(401, GENERIC)
    locked = credential.get("locked_until")
    if locked and datetime.fromisoformat(locked.replace("Z", "+00:00")) > now(): raise HTTPException(429, GENERIC)
    if not verify(pin, required_secret(binding, "PIN_PEPPER"), credential["salt_b64"], credential["verifier_b64"], int(credential["kdf_iterations"])):
        await record_failure(binding.DB, credential); raise HTTPException(401, GENERIC)
    timestamp = now(); await execute(binding.DB, "UPDATE pin_credentials SET failed_count=0,lockout_level=0,locked_until=NULL,updated_at=? WHERE id=?", iso(timestamp), credential["id"])
    raw = new_token(); digest = token_hash(raw, required_secret(binding, "SESSION_PEPPER")); expires = timestamp + timedelta(seconds=int(str(binding.SESSION_TTL_SECONDS)))
    await execute(binding.DB, "INSERT INTO auth_sessions(session_hash,role,profile_id,created_at,last_seen_at,expires_at) VALUES(?,'site',NULL,?,?,?)", digest, iso(timestamp), iso(timestamp), iso(expires))
    html = "application/x-www-form-urlencoded" in request.headers.get("content-type", "")
    response = RedirectResponse("/app/", 303) if html else JSONResponse({"ok": True, "next": "/app/"})
    response.headers["Set-Cookie"] = cookie_header(raw); return response

async def current_session(request):
    raw = request.cookies.get(COOKIE)
    if not raw: return None
    binding = env(request); row = await first(binding.DB, "SELECT role,profile_id,expires_at,revoked_at FROM auth_sessions WHERE session_hash=?", token_hash(raw, required_secret(binding, "SESSION_PEPPER")))
    if not row or row.get("revoked_at") or datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")) <= now(): return None
    return row

@app.get("/api/v1/auth/session")
async def auth_session(request: Request):
    session = await current_session(request)
    return {"authenticated": bool(session), "role": session["role"] if session else None, "profile": None}

@app.post("/api/v1/auth/logout")
async def logout(request: Request):
    raw = request.cookies.get(COOKIE)
    if raw:
        binding = env(request); await execute(binding.DB, "UPDATE auth_sessions SET revoked_at=? WHERE session_hash=?", iso(now()), token_hash(raw, required_secret(binding, "SESSION_PEPPER")))
    response = JSONResponse({"ok": True}); response.delete_cookie(COOKIE, path="/", secure=True, httponly=True, samesite="strict"); return response

async def serve_asset(path, request):
    if not await current_session(request): raise HTTPException(401, "Private training access required")
    result = await env(request).ASSETS.fetch(f"https://assets.local/app/{path or 'index.html'}")
    return Response(await result.bytes(), status_code=result.status, headers=result.headers)

@app.get("/app")
async def private_app_redirect(request: Request):
    if not await current_session(request): raise HTTPException(401, "Private training access required")
    return RedirectResponse("/app/", 308)

@app.get("/app/{path:path}")
async def private_assets(path: str, request: Request): return await serve_asset(path, request)

from workers import asgi
Default = asgi.entrypoint(app)
