from datetime import datetime, timedelta, timezone
import hmac
import hashlib
import json
import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from app.auth.lockout import failure_state
from app.auth.input import parse_urlencoded_pin
from app.auth.pin_kdf import create_verifier, valid_pin, verify
from app.auth.sessions import COOKIE, cookie_header, new_token, token_hash
from app.ai.fallback import choose_fallback
from app.ai.minimax_provider import MiniMaxProvider
from app.ai.validator import validate
from app.curriculum.generated_curriculum import CURRICULUM
from app.progress import calculate_module_progress, capability_envelope
from app.security_headers import SECURITY_HEADERS

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
GENERIC = "Access unavailable. Check the PIN or try again later."
SAFE_MUTATION_EXEMPTIONS = {"/api/v1/auth/site-login", "/api/v1/admin/bootstrap"}
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
    binding = env(request); row = await first(binding.DB, "SELECT role,profile_id,expires_at,revoked_at FROM auth_sessions WHERE session_hash=?", token_hash(raw, required_secret(binding, "SESSION_PEPPER")))
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
    return session

@app.get("/api/v1/auth/session")
async def auth_session(request: Request):
    session = await current_session(request)
    profile = None
    if session and session.get("profile_id"):
        profile = await first(env(request).DB, "SELECT id,display_name,character_id FROM profiles WHERE id=? AND deleted_at IS NULL", session["profile_id"])
    return {"authenticated": bool(session), "role": session["role"] if session else None, "profile": profile}

@app.post("/api/v1/auth/admin-login")
async def admin_login(request: Request):
    await require_session(request, "site"); binding = env(request); pin = await read_pin(request)
    credential = await first(binding.DB, "SELECT * FROM pin_credentials WHERE subject_type='admin' AND subject_id='admin'")
    if credential and credential_locked(credential): raise HTTPException(429, GENERIC)
    if not await verify_credential(binding, credential, pin): raise HTTPException(401, GENERIC)
    raw = await rotate_session(request, "admin"); response = JSONResponse({"ok": True}); response.headers["Set-Cookie"] = cookie_header(raw); return response

@app.post("/api/v1/auth/profile-login")
async def profile_login(request: Request):
    await require_session(request, "site", "admin"); binding = env(request); body = await request.json(); profile_id = str(body.get("profile_id", "")); pin = str(body.get("pin", ""))
    profile = await first(binding.DB, "SELECT id,pin_required FROM profiles WHERE id=? AND deleted_at IS NULL", profile_id)
    if not profile: raise HTTPException(401, GENERIC)
    if int(profile["pin_required"]):
        credential = await first(binding.DB, "SELECT * FROM pin_credentials WHERE subject_type='profile' AND subject_id=?", profile_id)
        if credential and credential_locked(credential): raise HTTPException(429, GENERIC)
        if not await verify_credential(binding, credential, pin): raise HTTPException(401, GENERIC)
    raw = await rotate_session(request, "learner", profile_id); response = JSONResponse({"ok": True}); response.headers["Set-Cookie"] = cookie_header(raw); return response

@app.post("/api/v1/auth/profile-exit")
async def profile_exit(request: Request):
    await require_session(request, "learner"); raw = await rotate_session(request, "site"); response = JSONResponse({"ok": True}); response.headers["Set-Cookie"] = cookie_header(raw); return response

@app.get("/api/v1/profiles")
async def list_profiles(request: Request):
    await require_session(request, "site", "admin"); result = await env(request).DB.prepare("SELECT id,display_name,pin_required,is_test_profile,character_id FROM profiles WHERE deleted_at IS NULL ORDER BY created_at").all(); data = as_dict(result)
    return data.get("results", []) if isinstance(data, dict) else []

@app.post("/api/v1/profiles")
async def create_profile(request: Request):
    await require_session(request, "admin"); binding = env(request); body = await request.json(); name = str(body.get("display_name", "")).strip(); pin = str(body.get("pin", "")).strip(); character = str(body.get("character_id", "runner_01")); allowed = {"runner_01","runner_02","focus_01","focus_02"}
    if not 1 <= len(name) <= 40 or character not in allowed or (pin and not valid_pin(pin, "profile")): raise HTTPException(422, "Profile data is invalid")
    profile_id = f"prof_{uuid.uuid4().hex}"; timestamp = iso(now()); pin_required = 1 if pin else 0
    statements = [binding.DB.prepare("INSERT INTO profiles(id,display_name,pin_required,save_version,curriculum_version,character_id,created_at,updated_at) VALUES(?,?,?,1,?,?,?,?)").bind(profile_id,name,pin_required,str(binding.CURRICULUM_VERSION),character,timestamp,timestamp), binding.DB.prepare("INSERT INTO progress(profile_id,save_version,curriculum_version,stage_id,unlocked_keys_json,current_lesson_id,resume_json,revision,updated_at) VALUES(?,1,?,'orientation','[\"f\",\"j\",\" \"]','orientation-1','{}',1,?)").bind(profile_id,str(binding.CURRICULUM_VERSION),timestamp)]
    if pin:
        salt, digest, iterations = create_verifier(pin, required_secret(binding, "PIN_PEPPER")); statements.append(binding.DB.prepare("INSERT INTO pin_credentials(id,subject_type,subject_id,salt_b64,verifier_b64,kdf_iterations,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)").bind(f"pin_{uuid.uuid4().hex}","profile",profile_id,salt,digest,iterations,timestamp,timestamp))
    await binding.DB.batch(statements); return {"id": profile_id, "display_name": name, "pin_required": bool(pin), "character_id": character}

@app.patch("/api/v1/profile/character")
async def update_character(request: Request):
    session = await require_session(request, "learner"); character = str((await request.json()).get("character_id", "")); allowed = {"runner_01","runner_02","focus_01","focus_02"}
    if character not in allowed: raise HTTPException(422, "Unknown character")
    await execute(env(request).DB, "UPDATE profiles SET character_id=?,updated_at=? WHERE id=? AND deleted_at IS NULL", character, iso(now()), session["profile_id"])
    return {"ok": True, "character_id": character}

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
    cached = await first(binding.DB, "SELECT id,text FROM generated_content WHERE constraint_hash=? ORDER BY last_used_at ASC,created_at DESC LIMIT 1", constraint_hash)
    if cached:
        await execute(binding.DB, "UPDATE generated_content SET last_used_at=? WHERE id=?", iso(now()), cached["id"])
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
        text = choose_fallback(stage["fallbackDrills"],constraint_hash); validation = validate(text,allowed,1,1200)
    lesson_id=f"les_{uuid.uuid4().hex}"; timestamp=iso(now()); await execute(binding.DB,"INSERT INTO generated_content(id,profile_id,constraint_hash,request_mode,stage_id,difficulty,focus_keys_json,topic,text,provider,model,prompt_version,validation_json,created_at,last_used_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",lesson_id,session["profile_id"],constraint_hash,mode,stage_id,str(body.get("difficulty","practice")),json.dumps(body.get("focus_keys",[])),topic or None,text,"minimax" if source=="ai" else "builtin",str(binding.MINIMAX_MODEL),"rev4-v1",json.dumps(validation),timestamp,timestamp)
    kind = "passage" if capability["topic"] and (mode in {"custom_passage","text_to_type"} or len(text)>220) else "drill"
    return {"lesson_id":lesson_id,"schema_version":1,"text":text,"focus_keys":body.get("focus_keys",[]),"estimated_characters":len(text),"estimated_duration_seconds":int(duration) if duration is not None else None,"lesson_kind":kind,"source":source,"validation":{"passed":True}}

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
