# Learn_to_Type — Codex Build Specification

**Document purpose:** implementation instructions for a Codex coding agent.

**Project:** cloud-hosted adaptive typing trainer based on the existing `typing_app_product_spec.md` and the completed Cloudflare architecture research.

**Target deployment:** the user's existing Cloudflare account/zone.

**Primary runtime decision:** React + TypeScript + Vite frontend; framework-independent TypeScript typing engine; FastAPI on Cloudflare Python Workers; Workers Static Assets; Cloudflare D1; IndexedDB for local resilience; MiniMax AI only through the backend; PIN-gated site access.

---

## 0. Codex mandate

Build the project described in this document as a production-capable V1. Do not reinterpret the product into a generic typing game, generic chatbot, social product, or arcade experience.

The implementation must preserve the product's central principles:

1. Technique before speed.
2. Progress before scores.
3. Personal bests before leaderboards.
4. Adaptation before repetition.
5. Hints before penalties.
6. Calm before hype.
7. Structure before AI improvisation.
8. Local functionality before cloud dependency.
9. User progress must survive every update.
10. The app should feel intelligent without constantly talking.
11. The coach should motivate without judging.
12. Every metric should help answer: **“What should I work on next?”**

The primary learner is a teenage beginner. The product must feel modern, intelligent, calm, purposeful, personal, and teen-appropriate. It must not feel childish, ad-heavy, noisy, school-teacher-ish, or commercially manipulative.

### Source-of-truth precedence

When implementation details conflict, use this order:

1. **This build specification** for concrete architecture and implementation choices.
2. **`typing_app_product_spec.md`** for product behavior, tone, curriculum philosophy, UX, and V1/V1.5/V2 boundaries.
3. **`Cloud-Hosted Typing Trainer on Cloudflare: Architecture and Implementation Research`** for Cloudflare/Python/MiniMax architecture and security rationale.
4. Existing repository code/configuration, where present, but only if it does not contradict items 1–3.

Do not silently discard an existing Cloudflare binding, route, database ID, or migration history. Inspect first, then extend safely.

---

# 1. Authoritative technology decisions

Treat the following as final for V1.

| Concern | Final choice |
|---|---|
| Frontend | React + TypeScript + Vite |
| Typing engine | Framework-independent TypeScript domain module |
| Full game engine | **None in V1** |
| Future game scenes | Phaser may later be mounted only for genuinely game-like challenge modules |
| Backend | Python 3.13+ + FastAPI + Pydantic |
| Cloud runtime | Cloudflare Python Workers |
| Static delivery | Cloudflare Workers Static Assets |
| Primary database | Cloudflare D1 |
| Browser-local persistence | IndexedDB |
| Authentication | Opaque server-side sessions in D1 |
| Site access | Required shared/site PIN before app assets/API are usable |
| Learner access | Profile selector; optional 4–6 digit learner PIN |
| Admin access | Separate stronger parent/admin PIN |
| PIN storage | Salted slow verifier + server-side pepper; never plaintext |
| Rate limiting | Workers Rate Limiting binding + authoritative D1 lockout |
| AI provider | MiniMax API |
| Default AI model | `MiniMax-M2.7`, configurable by non-secret environment variable |
| MiniMax key | Cloudflare Worker Secret only |
| AI execution | Event-based synchronous requests for V1 |
| AI cache | D1 |
| AI failure behavior | Cached or deterministic fallback content; never break typing |
| CI/CD | GitHub Actions preferred; Cloudflare build integration acceptable if repo already uses it |
| Production tier | Workers Paid recommended because PIN KDF/FastAPI CPU headroom matters more than traffic |
| Domain | Existing Cloudflare custom domain/subdomain; do not invent or overwrite one |

### Important terminology

- **MiniMax** = the AI provider/API.
- **minimax** = a classical adversarial game-tree algorithm.

Do **not** implement classical minimax in V1. The current typing trainer has no adversarial state/move/utility definition that would justify it. Reserve a future `backend/app/game_search/` module name only if a real adversarial typing game is specified later.

---

# 2. V1 scope

V1 must include:

- PIN-gated deployed web app
- Multiple learner profiles
- Optional learner profile PIN
- Separate admin PIN
- Beginner curriculum structure
- Deterministic typing exercise engine
- Visual keyboard
- Home-row tutorial
- Finger assignment system
- Simple hand/finger reach animation
- WPM
- Accuracy
- Key-level errors
- Basic cadence/rhythm metric
- Key mastery
- Session save
- Resume exactly where the learner stopped
- Session summaries
- Coach modes: Silent, Calm, Competitive
- Structured AI training console
- MiniMax lesson reshuffle
- MiniMax weak-key drill generation
- MiniMax training explanations
- Test/developer mode
- Save-format versioning
- Automatic save-data migration support
- D1 schema migrations
- IndexedDB active-session resilience
- Deterministic AI fallbacks
- Automated tests
- Cloudflare deployment configuration
- Security headers and auth hardening

### V1.5 — do not let these block V1

- Key heat map
- Weekly trend visualization
- More advanced cadence scoring
- Full recovery metric
- More coach personalities
- Rich topic-passage generation
- Export/import UI
- Installable PWA/offline cold start
- Async AI job system

### V2 — explicitly out of scope now

- Social network
- Public leaderboard
- Multiplayer competition
- Subscription/payments infrastructure
- Advertising
- Native mobile app
- Full AI-agent platform
- Huge authored lesson library
- Cloud account/email system
- Full multi-device conflict-resolution engine
- Classical minimax game AI

---

# 3. Repository layout

Create a clean monorepo. If the repository already exists, adapt names without destroying existing history.

```text
Learn_to_Type/
├─ AGENTS.md
├─ README.md
├─ SECURITY.md
├─ ARCHITECTURE.md
├─ DEPLOYMENT.md
├─ pyproject.toml
├─ uv.lock
├─ package.json                 # optional root convenience scripts only
├─ wrangler.jsonc
├─ .gitignore
├─ .dev.vars.example
├─ frontend/
│  ├─ package.json
│  ├─ package-lock.json
│  ├─ tsconfig.json
│  ├─ vite.config.ts
│  ├─ index.html
│  └─ src/
│     ├─ main.tsx
│     ├─ App.tsx
│     ├─ api/
│     │  ├─ client.ts
│     │  ├─ auth.ts
│     │  ├─ profiles.ts
│     │  ├─ progress.ts
│     │  ├─ sessions.ts
│     │  └─ ai.ts
│     ├─ app/
│     │  ├─ appState.ts
│     │  ├─ sessionContext.tsx
│     │  └─ routes.tsx
│     ├─ typing-core/
│     │  ├─ types.ts
│     │  ├─ engine.ts
│     │  ├─ input.ts
│     │  ├─ metrics.ts
│     │  ├─ cadence.ts
│     │  ├─ mastery.ts
│     │  ├─ lessonSelector.ts
│     │  ├─ validation.ts
│     │  └─ fingerMap.ts
│     ├─ curriculum/
│     │  ├─ curriculum.ts
│     │  ├─ builtinLessons.ts
│     │  └─ progression.ts
│     ├─ persistence/
│     │  ├─ db.ts
│     │  ├─ migrations.ts
│     │  ├─ activeSessionStore.ts
│     │  ├─ syncQueue.ts
│     │  └─ generatedContentCache.ts
│     ├─ components/
│     │  ├─ layout/
│     │  ├─ auth/
│     │  ├─ profiles/
│     │  ├─ training/
│     │  │  ├─ TypingSurface.tsx
│     │  │  ├─ PromptLine.tsx
│     │  │  ├─ VisualKeyboard.tsx
│     │  │  ├─ HandGuide.tsx
│     │  │  ├─ LiveMetrics.tsx
│     │  │  └─ LessonHeader.tsx
│     │  ├─ coach/
│     │  │  ├─ CoachPanel.tsx
│     │  │  └─ coachRules.ts
│     │  ├─ ai/
│     │  │  └─ TrainingConsole.tsx
│     │  ├─ summary/
│     │  │  └─ SessionSummary.tsx
│     │  ├─ settings/
│     │  └─ admin/
│     ├─ screens/
│     │  ├─ ProfileSelectScreen.tsx
│     │  ├─ ProfilePinScreen.tsx
│     │  ├─ ResumeScreen.tsx
│     │  ├─ TrainingScreen.tsx
│     │  ├─ SummaryScreen.tsx
│     │  ├─ SettingsScreen.tsx
│     │  └─ AdminScreen.tsx
│     ├─ styles/
│     │  ├─ tokens.css
│     │  ├─ global.css
│     │  └─ components.css
│     └─ generated/
│        ├─ curriculum.generated.ts
│        └─ finger-map.generated.ts
├─ backend/
│  ├─ main.py
│  └─ app/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ dependencies.py
│     ├─ errors.py
│     ├─ security_headers.py
│     ├─ auth/
│     │  ├─ models.py
│     │  ├─ pin_kdf.py
│     │  ├─ sessions.py
│     │  ├─ lockout.py
│     │  ├─ middleware.py
│     │  └─ routes.py
│     ├─ profiles/
│     │  ├─ models.py
│     │  ├─ repository.py
│     │  └─ routes.py
│     ├─ progress/
│     │  ├─ models.py
│     │  ├─ repository.py
│     │  └─ routes.py
│     ├─ sessions/
│     │  ├─ models.py
│     │  ├─ repository.py
│     │  └─ routes.py
│     ├─ curriculum/
│     │  ├─ generated_curriculum.py
│     │  └─ routes.py
│     ├─ ai/
│     │  ├─ models.py
│     │  ├─ minimax_provider.py
│     │  ├─ prompts.py
│     │  ├─ validator.py
│     │  ├─ cache.py
│     │  ├─ fallback.py
│     │  └─ routes.py
│     ├─ admin/
│     │  ├─ models.py
│     │  ├─ audit.py
│     │  └─ routes.py
│     └─ db/
│        ├─ d1.py
│        └─ queries.py
├─ shared/
│  ├─ curriculum/
│  │  └─ curriculum.v1.json
│  └─ keyboard/
│     └─ finger-map.us-qwerty.json
├─ scripts/
│  ├─ generate_shared.py
│  ├─ bootstrap.md
│  ├─ dev.ps1
│  ├─ test.ps1
│  └─ build.ps1
├─ migrations/
│  ├─ 0001_initial.sql
│  └─ README.md
├─ tests/
│  ├─ backend/
│  └─ fixtures/
└─ .github/
   └─ workflows/
      └─ deploy.yml
```

### Shared-data rule

`shared/curriculum/curriculum.v1.json` and `shared/keyboard/finger-map.us-qwerty.json` are the human-edited sources of truth.

`scripts/generate_shared.py` must generate:

- `frontend/src/generated/curriculum.generated.ts`
- `frontend/src/generated/finger-map.generated.ts`
- `backend/app/curriculum/generated_curriculum.py`

CI must run the generator and fail if generated files differ from committed output. This prevents frontend/backend curriculum drift.

---

# 4. Cloudflare request topology and true site gating

The user specifically requires a PIN to access the app so the deployed trainer is not freely usable.

Do not treat “API endpoints require auth” as sufficient if an unauthenticated user can still load the full React app and built-in lesson engine and use it indefinitely.

## Required route behavior

Use `assets.run_worker_first = true`.

### Public routes

Only these should be available without a valid site session:

```text
GET  /
GET  /healthz
POST /api/v1/auth/site-login
GET  /api/v1/auth/bootstrap-status
POST /api/v1/admin/bootstrap     # only before initial bootstrap; requires BOOTSTRAP_TOKEN
```

`GET /` must return a **minimal server-rendered PIN gate**, not the React application.

The gate may be plain HTML/CSS. Keep it deliberately small. It should say something like:

> Cadence  
> Private training access  
> Enter access PIN

No marketing site is required.

### Private static application

The built Vite app must live under:

```text
/app/
/app/index.html
/app/assets/*
```

Configure Vite so the production base path is `/app/` and its output physically contains the `/app` directory under `frontend/dist`.

Every `/app/*` request must pass through the Worker first. Require a valid D1 session whose role is at least `site` before calling the Static Assets binding.

### Private APIs

All non-public APIs require a valid session. Additional role/profile checks apply per route.

### Same-origin deployment

Target:

```text
https://<existing-cloudflare-domain>/
https://<existing-cloudflare-domain>/app/
https://<existing-cloudflare-domain>/api/v1/...
```

Do not create a second API host unless an existing project architecture already requires it.

---

# 5. Cloudflare configuration

Use the repository's existing Wrangler format if one exists. Do not overwrite an existing `database_id`, route, or migration tag.

A new configuration should conceptually resemble:

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "learn-to-type",
  "main": "backend/main.py",
  "compatibility_date": "2026-09-04",
  "compatibility_flags": ["python_workers"],

  "assets": {
    "directory": "./frontend/dist",
    "binding": "ASSETS",
    "run_worker_first": true
  },

  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "learn-to-type",
      "database_id": "<PIN THE REAL EXISTING/CREATED DATABASE UUID HERE>",
      "migrations_dir": "migrations"
    }
  ],

  "ratelimits": [
    {
      "name": "LOGIN_LIMITER",
      "namespace_id": "1001",
      "simple": { "limit": 5, "period": 60 }
    },
    {
      "name": "AI_LIMITER",
      "namespace_id": "1002",
      "simple": { "limit": 20, "period": 60 }
    }
  ],

  "vars": {
    "APP_ENV": "production",
    "APP_SAVE_VERSION": "1",
    "CURRICULUM_VERSION": "2026.1",
    "MINIMAX_BASE_URL": "https://api.minimax.io/v1",
    "MINIMAX_MODEL": "MiniMax-M2.7",
    "SESSION_TTL_SECONDS": "43200",
    "ADMIN_SESSION_TTL_SECONDS": "3600"
  }
}
```

The Codex agent must validate the actual Wrangler schema/version installed in the repository rather than blindly copying this example.

## Worker Secrets

Required production secrets:

```text
MINIMAX_API_KEY
PIN_PEPPER
SESSION_PEPPER
BOOTSTRAP_TOKEN        # temporary; remove after first bootstrap
```

Create them only through Cloudflare secret tooling, for example:

```bash
npx wrangler secret put MINIMAX_API_KEY
npx wrangler secret put PIN_PEPPER
npx wrangler secret put SESSION_PEPPER
npx wrangler secret put BOOTSTRAP_TOKEN
```

Never commit a real value.

`.dev.vars.example` must list variable names only with obvious placeholders.

---

# 6. Initial D1 schema

Create `migrations/0001_initial.sql` with a production-usable schema. Use TEXT UUID/ULID identifiers generated application-side. Store timestamps as UTC ISO-8601 text consistently.

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE app_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE profiles (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  pin_required INTEGER NOT NULL DEFAULT 0 CHECK (pin_required IN (0,1)),
  save_version INTEGER NOT NULL DEFAULT 1,
  curriculum_version TEXT NOT NULL,
  difficulty TEXT NOT NULL DEFAULT 'practice'
    CHECK (difficulty IN ('explore','practice','train','challenge')),
  coach_mode TEXT NOT NULL DEFAULT 'calm'
    CHECK (coach_mode IN ('silent','calm','competitive')),
  coach_frequency TEXT NOT NULL DEFAULT 'normal'
    CHECK (coach_frequency IN ('low','normal','high')),
  ui_prefs_json TEXT NOT NULL DEFAULT '{}',
  ai_prefs_json TEXT NOT NULL DEFAULT '{}',
  is_test_profile INTEGER NOT NULL DEFAULT 0 CHECK (is_test_profile IN (0,1)),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  deleted_at TEXT
);

CREATE TABLE pin_credentials (
  id TEXT PRIMARY KEY,
  subject_type TEXT NOT NULL
    CHECK (subject_type IN ('site','profile','admin')),
  subject_id TEXT NOT NULL,
  salt_b64 TEXT NOT NULL,
  verifier_b64 TEXT NOT NULL,
  kdf_name TEXT NOT NULL DEFAULT 'PBKDF2-HMAC-SHA256',
  kdf_iterations INTEGER NOT NULL,
  failed_count INTEGER NOT NULL DEFAULT 0,
  lockout_level INTEGER NOT NULL DEFAULT 0,
  locked_until TEXT,
  last_failed_at TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE(subject_type, subject_id)
);

CREATE TABLE auth_sessions (
  session_hash TEXT PRIMARY KEY,
  role TEXT NOT NULL CHECK (role IN ('site','learner','admin')),
  profile_id TEXT,
  created_at TEXT NOT NULL,
  last_seen_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT,
  FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

CREATE INDEX idx_auth_sessions_profile ON auth_sessions(profile_id);
CREATE INDEX idx_auth_sessions_expiry ON auth_sessions(expires_at);

CREATE TABLE progress (
  profile_id TEXT PRIMARY KEY,
  save_version INTEGER NOT NULL,
  metrics_version INTEGER NOT NULL DEFAULT 1,
  curriculum_version TEXT NOT NULL,
  stage_id TEXT NOT NULL,
  unlocked_keys_json TEXT NOT NULL DEFAULT '[]',
  current_lesson_id TEXT,
  resume_json TEXT NOT NULL DEFAULT '{}',
  revision INTEGER NOT NULL DEFAULT 1,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

CREATE TABLE training_sessions (
  id TEXT PRIMARY KEY,
  sync_id TEXT NOT NULL UNIQUE,
  profile_id TEXT NOT NULL,
  lesson_id TEXT,
  stage_id TEXT NOT NULL,
  mode TEXT NOT NULL DEFAULT 'normal'
    CHECK (mode IN ('normal','test')),
  difficulty TEXT NOT NULL,
  started_at TEXT NOT NULL,
  ended_at TEXT NOT NULL,
  duration_ms INTEGER NOT NULL,
  active_duration_ms INTEGER NOT NULL,
  char_attempts INTEGER NOT NULL,
  correct_chars INTEGER NOT NULL,
  error_count INTEGER NOT NULL,
  hint_count INTEGER NOT NULL DEFAULT 0,
  gross_wpm REAL NOT NULL,
  net_wpm REAL NOT NULL,
  accuracy REAL NOT NULL,
  cadence_score REAL,
  cadence_cv REAL,
  stall_count INTEGER NOT NULL DEFAULT 0,
  summary_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

CREATE INDEX idx_training_sessions_profile_time
  ON training_sessions(profile_id, started_at DESC);

CREATE TABLE key_mastery (
  profile_id TEXT NOT NULL,
  key_code TEXT NOT NULL,
  display_key TEXT NOT NULL,
  hand TEXT NOT NULL CHECK (hand IN ('left','right','either')),
  finger TEXT NOT NULL,
  introduced INTEGER NOT NULL DEFAULT 0 CHECK (introduced IN (0,1)),
  attempts INTEGER NOT NULL DEFAULT 0,
  correct INTEGER NOT NULL DEFAULT 0,
  errors INTEGER NOT NULL DEFAULT 0,
  total_reaction_ms INTEGER NOT NULL DEFAULT 0,
  mastery REAL NOT NULL DEFAULT 0,
  last_practiced TEXT,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (profile_id, key_code),
  FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

CREATE TABLE generated_content (
  id TEXT PRIMARY KEY,
  profile_id TEXT,
  constraint_hash TEXT NOT NULL,
  request_mode TEXT NOT NULL,
  stage_id TEXT NOT NULL,
  difficulty TEXT NOT NULL,
  focus_keys_json TEXT NOT NULL DEFAULT '[]',
  topic TEXT,
  text TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  validation_json TEXT NOT NULL,
  created_at TEXT NOT NULL,
  last_used_at TEXT,
  completed_count INTEGER NOT NULL DEFAULT 0,
  rating INTEGER,
  FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

CREATE INDEX idx_generated_content_constraint
  ON generated_content(constraint_hash, created_at DESC);

CREATE TABLE ai_usage (
  id TEXT PRIMARY KEY,
  profile_id TEXT,
  route TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  status TEXT NOT NULL,
  cached INTEGER NOT NULL DEFAULT 0 CHECK (cached IN (0,1)),
  input_tokens INTEGER,
  output_tokens INTEGER,
  latency_ms INTEGER,
  created_at TEXT NOT NULL,
  FOREIGN KEY (profile_id) REFERENCES profiles(id)
);

CREATE TABLE admin_events (
  id TEXT PRIMARY KEY,
  action TEXT NOT NULL,
  target_profile_id TEXT,
  detail_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL,
  FOREIGN KEY (target_profile_id) REFERENCES profiles(id)
);

CREATE INDEX idx_admin_events_time ON admin_events(created_at DESC);
```

### Data rules

- `mode='test'` sessions must never influence normal learner progress or mastery.
- Soft-deleted profiles stay recoverable until an explicit admin hard-delete operation is implemented later.
- Never store PINs, session tokens, MiniMax API keys, or secret peppers in D1.
- Never store raw per-keystroke telemetry in D1 for V1. Send exercise/session aggregates and per-key deltas only.

---

# 7. Authentication and authorization

## 7.1 Credential classes

There are three PIN credential classes:

1. **Site PIN** — required to enter the deployed application at all.
2. **Learner profile PIN** — optional 4–6 digits; protects a specific profile.
3. **Admin PIN** — separate, stronger; unlocks test mode, profile management, reset, advanced controls, and AI/curriculum configuration.

Recommended policy:

```text
Site PIN:    6–12 numeric digits
Profile PIN: 4–6 numeric digits
Admin PIN:   8–12 numeric digits
```

Do not ship a default PIN.

## 7.2 PIN verifier

Do not use raw SHA-256 of a PIN.

Credential interface:

```text
verifier = PBKDF2-HMAC-SHA256(
  secret = normalized_pin || PIN_PEPPER,
  salt = random 16+ byte per-credential salt,
  iterations = calibrated deployment work factor
)
```

Implementation requirements:

- Use Cloudflare Workers Web Crypto through Python Worker FFI when practical.
- Keep the KDF behind `backend/app/auth/pin_kdf.py` so the implementation can change without changing routes.
- Do not add a native cryptography package merely for PBKDF2 unless it is verified compatible with Python Workers.
- Start from the research target of approximately 600,000 PBKDF2-HMAC-SHA256 iterations, but benchmark in the actual deployed runtime.
- On Workers Paid, target a verifier slow enough to resist guessing without making normal login feel broken.
- Store `kdf_iterations` per credential to allow future rehash-on-login upgrades.
- Compare verifier bytes in constant-time.

## 7.3 D1 lockout

The Workers rate limiter is burst defense, not the authoritative lockout.

Implement D1 credential lockout as follows:

```text
Normal failures 1–4: no D1 time lock
5th failure: lock credential for 60 seconds; reset failed_count to 0; lockout_level = 1
Next 5-failure cycle: 5 minutes; lockout_level = 2
Next cycle: 15 minutes; lockout_level = 3
Further cycles: 60 minutes max; lockout_level = 4
Successful login: failed_count = 0, lockout_level = 0, locked_until = NULL
```

Public error text must remain generic:

```text
Access unavailable. Check the PIN or try again later.
```

Do not reveal whether the site/profile/admin credential exists.

## 7.4 Opaque server-side sessions

Generate at least 32 random bytes for the raw session token.

Browser cookie:

```http
Set-Cookie: __Host-cadence_session=<opaque-token>; Secure; HttpOnly; SameSite=Strict; Path=/
```

Store only:

```text
session_hash = HMAC-SHA256(SESSION_PEPPER, raw_session_token)
```

in D1.

Session rules:

- Site login creates role `site`, no profile.
- Selecting a no-PIN profile rotates the session into role `learner` scoped to that profile.
- Successful profile-PIN login rotates the session into `learner` scoped to that profile.
- Successful admin-PIN login rotates into `admin`.
- Admin session TTL is shorter than normal site/learner session TTL.
- Every privilege transition rotates the raw token.
- Logout revokes the current D1 row and clears the cookie.
- Expired/revoked sessions are rejected.
- Update `last_seen_at` at a bounded cadence, not every request; avoid unnecessary D1 writes.

## 7.5 Role model

`site` may:

- load private app assets
- list profile cards with non-sensitive metadata
- choose a profile
- attempt profile/admin login

`learner` may:

- read/write only its own profile progress and sessions
- call typing AI endpoints only for itself
- read its own key mastery/history
- change normal learner settings
- return to profile selector

`admin` may:

- create/edit/soft-delete profiles
- set/reset learner PINs
- enter test mode
- create test profiles
- reset learner current-session state
- inspect non-secret training summaries
- change curriculum/AI configuration exposed by the app
- perform future export/import controls

Never trust a client-supplied profile ID when the session is learner-scoped. Derive profile ID from the authenticated session.

---

# 8. Bootstrap flow

The app needs initial site and admin PINs without shipping defaults.

Implement a one-time bootstrap endpoint:

```text
POST /api/v1/admin/bootstrap
Authorization: Bearer <BOOTSTRAP_TOKEN>
```

Body:

```json
{
  "site_pin": "......",
  "admin_pin": "........"
}
```

Rules:

- Only succeeds if `app_meta.bootstrapped` is absent/false and no site/admin credentials exist.
- Requires constant-time comparison against the `BOOTSTRAP_TOKEN` Worker Secret.
- Creates site and admin credential rows using independent salts.
- Sets `app_meta.bootstrapped=true`.
- Refuses permanently afterward, even if the token is still configured.
- Log only `bootstrap_completed`, not values.
- Documentation must instruct the owner to remove `BOOTSTRAP_TOKEN` after successful bootstrap.

Public bootstrap status may return only:

```json
{ "ready": true }
```

Do not return credential metadata.

---

# 9. API contract

Version every API under `/api/v1`.

All state-changing authenticated API requests must be same-origin and include:

```http
X-Cadence-Request: 1
```

Reject unexpected `Origin` values in production.

## 9.1 Auth endpoints

### `POST /api/v1/auth/site-login`

Public. Accept JSON from tests and form-encoded data from the server-rendered PIN gate.

Input:

```json
{ "pin": "123456" }
```

Success:

- rotate/create site session
- set HttpOnly cookie
- JSON clients get `200 {"ok":true,"next":"/app/"}`
- HTML form clients get `303 Location: /app/`

Failure: generic `401` or `429`.

### `GET /api/v1/auth/session`

Returns only what the UI needs:

```json
{
  "authenticated": true,
  "role": "site|learner|admin",
  "profile": {
    "id": "...",
    "display_name": "..."
  }
}
```

### `POST /api/v1/auth/profile-login`

Requires role `site` or `admin`.

```json
{
  "profile_id": "prof_...",
  "pin": "1234"
}
```

If `pin_required=false`, allow `pin` to be omitted.

On success, rotate into learner session scoped to profile.

### `POST /api/v1/auth/admin-login`

Requires valid site session.

```json
{ "pin": "12345678" }
```

Rotate to admin session.

### `POST /api/v1/auth/profile-exit`

Learner session becomes a fresh site session. Do not require the site PIN again while the site session is still within its absolute allowed lifetime.

### `POST /api/v1/auth/logout`

Revoke and clear cookie. Browser returns to `/`.

---

## 9.2 Profiles

### `GET /api/v1/profiles`

Roles: site/admin.

Return only:

```json
[
  {
    "id": "prof_...",
    "display_name": "Julian",
    "pin_required": true,
    "is_test_profile": false
  }
]
```

Do not return performance metrics to a mere site session.

### `POST /api/v1/profiles`

Admin only.

```json
{
  "display_name": "Julian",
  "pin": "1234",
  "difficulty": "practice",
  "coach_mode": "calm"
}
```

Create profile, optional credential, initial progress row, and initial key_mastery rows transactionally where D1 capabilities permit. If a single D1 transaction abstraction is unavailable in Python Worker bindings, make the operation idempotent and rollback/cleanup explicitly.

### `PATCH /api/v1/profiles/{id}`

Admin only for identity/PIN/test flags. Learner may change only whitelisted preferences through `/me/settings`.

### `POST /api/v1/profiles/{id}/pin`

Admin only. Replaces or removes profile PIN atomically.

---

## 9.3 Learner state

### `GET /api/v1/me`

Learner/admin-as-profile only.

Return profile preferences + current progress + compact best/recent metrics.

### `PATCH /api/v1/me/settings`

Whitelist:

- difficulty
- coach_mode
- coach_frequency
- font size
- contrast
- keyboard size
- reduce motion
- hand animation enabled
- hide live metrics
- sound enabled
- session length
- AI topic preference, if any

### `GET /api/v1/curriculum`

Return current curriculum version and stage metadata. The frontend also has a generated bundled copy for loaded-session resilience; compare versions on startup.

### `GET /api/v1/progress`

Return resumable state.

### `PUT /api/v1/progress`

Input includes expected `revision`.

Use optimistic concurrency:

```json
{
  "save_version": 1,
  "curriculum_version": "2026.1",
  "revision": 7,
  "stage_id": "home_all",
  "unlocked_keys": ["a","s","d","f","j","k","l",";"," "],
  "current_lesson_id": "builtin_home_all_03",
  "resume": {
    "lesson_index": 2,
    "char_index": 84,
    "weak_keys": ["r","t"],
    "recommended_action": "weak_keys"
  }
}
```

Server updates only if revision matches, then increments revision.

On conflict, return `409` with the server's current revision and compact state. The frontend should preserve its active local draft and resolve after the exercise, not interrupt keystrokes.

---

## 9.4 Sessions and mastery

### `POST /api/v1/sessions`

Finalize one completed training session.

Require `sync_id` generated client-side. Replaying the same `sync_id` must be idempotent.

The payload contains only aggregate session metrics and per-key deltas, for example:

```json
{
  "sync_id": "sync_...",
  "lesson_id": "les_...",
  "stage_id": "home_all",
  "mode": "normal",
  "difficulty": "practice",
  "started_at": "...",
  "ended_at": "...",
  "duration_ms": 182000,
  "active_duration_ms": 171000,
  "char_attempts": 520,
  "correct_chars": 498,
  "error_count": 22,
  "hint_count": 3,
  "gross_wpm": 36.5,
  "net_wpm": 35.0,
  "accuracy": 95.77,
  "cadence_score": 71,
  "cadence_cv": 0.29,
  "stall_count": 4,
  "summary": { "...": "..." },
  "key_deltas": [
    {
      "key_code": "KeyR",
      "display_key": "r",
      "attempts": 30,
      "correct": 26,
      "errors": 4,
      "reaction_ms_total": 13200
    }
  ]
}
```

Server must:

1. verify learner scope
2. reject impossible/negative values
3. insert session idempotently
4. update key_mastery rows
5. update progress only if `mode=normal`
6. exclude `mode=test` from normal summaries/mastery

### `GET /api/v1/sessions?limit=20`

Return compact history.

### `GET /api/v1/key-mastery`

Return mastery map for current learner.

---

# 10. Typing engine

The typing engine is the most important deterministic module. It must not depend on React, D1, or MiniMax.

## 10.1 Engine inputs

Use browser keyboard events but convert them immediately to plain domain events.

```ts
export type TypingInput = {
  key: string;             // event.key
  code: string;            // event.code
  timestampMs: number;     // performance.now()
  shift: boolean;
  alt: boolean;
  ctrl: boolean;
  meta: boolean;
  repeat: boolean;
};
```

## 10.2 Input rules

- Use `performance.now()` for monotonic timing.
- Ignore `keydown` events where `event.repeat=true`.
- Ignore Ctrl/Meta/Alt shortcuts.
- Do not count Tab, Escape, function keys, browser shortcuts, or navigation keys as typing attempts.
- Use `event.key` for the actual character and `event.code` for physical-key/finger mapping.
- Treat Shift correctly for capitals and shifted punctuation.
- On focus loss or `document.visibilityState !== 'visible'`, pause active timing.
- The first keystroke after resume starts a new timing segment; do not count the hidden/background interval toward cadence.
- Paste must not complete text. Prevent paste on the typing surface.
- IME composition events should not be counted as normal keystrokes; V1 curriculum is US English/QWERTY.
- Mobile software-keyboard support is best-effort V1; desktop/laptop physical keyboard behavior is the primary acceptance target.

## 10.3 Correction policy

Use a calm retry model.

Default V1 behavior:

- A wrong printable key counts as an attempt/error.
- The cursor does **not** advance on a wrong key.
- The expected character receives a subtle error/hint state.
- The learner may press the correct character immediately; no harsh reset.
- Backspace does not erase historical accuracy/errors; it may be used only to clear an optional visual typed buffer if that buffer exists.
- Do not let repeated Backspace artificially repair accuracy.

This makes scoring deterministic while treating the mistake as information rather than punishment.

## 10.4 Engine state

At minimum:

```ts
export type TypingState = {
  lessonId: string;
  text: string;
  charIndex: number;
  startedAtMs: number | null;
  activeStartedAtMs: number | null;
  activeElapsedMs: number;
  paused: boolean;
  attempts: number;
  correct: number;
  errors: number;
  hintCount: number;
  lastCorrectAtMs: number | null;
  correctKeyTimestamps: number[];
  recentErrors: ErrorEvent[];
  perKey: Record<string, KeyAttemptAccumulator>;
  completed: boolean;
};
```

Keep raw timestamp arrays only for the active exercise/session in browser memory/IndexedDB. Do not upload the entire array to D1.

---

# 11. Metrics — exact V1 definitions

The original product spec intentionally leaves formulas open. For V1, use these deterministic formulas and document them as implementation definitions so they can be versioned later.

Set:

```text
METRICS_VERSION = 1
```

## 11.1 Gross WPM

Standard five-character word convention:

```text
gross_wpm = (printable_attempts / 5) / active_minutes
```

## 11.2 Net/display WPM

Keep accuracy separate rather than using a punitive subtract-errors formula.

```text
net_wpm = (correct_characters / 5) / active_minutes
```

Display `net_wpm` as the normal WPM value.

For “current WPM,” calculate a rolling 30-second window only after at least 10 valid characters; otherwise show a neutral placeholder.

## 11.3 Accuracy

```text
accuracy = 100 * correct_characters / printable_attempts
```

If there are no attempts, return null rather than 100.

## 11.4 Reaction time per key

For each expected character:

```text
reaction_ms = time_of_first_correct_press - time_character_became_current
```

If wrong attempts occur first, keep the timer running until the correct press. This lets repeated misses produce a meaningful slower reaction value without extra punishment.

Exclude time while document/session is paused.

## 11.5 Cadence / rhythm V1

Use correct printable keystrokes only.

Build inter-key intervals between successive correct keystrokes inside the same active timing segment.

Discard intervals:

- after a focus/visibility pause
- <= 0
- > 4000 ms from the CV calculation, but record them as long pauses

If fewer than 8 usable intervals exist, cadence is `null`.

Compute:

```text
mean_interval = mean(intervals)
stdev_interval = population_standard_deviation(intervals)
cadence_cv = stdev_interval / mean_interval
cadence_score = clamp(round(100 - cadence_cv * 100), 0, 100)
```

This is intentionally simple and versionable.

## 11.6 Stall detection

For each interval after enough history exists:

```text
baseline = median(previous up to 12 usable intervals)
stall = interval >= 500 ms AND interval >= 3 * baseline
```

The research fixture must pass:

```text
correct-key timestamps: 0, 100, 200, 300, 900, 1000 ms
intervals:              100, 100, 100, 600, 100 ms
expected: one 600 ms stall
```

## 11.7 Key mastery V1

Mastery is not a grade. It is an internal training-selection signal.

For each key:

```text
accuracy_component = correct / max(attempts, 1)
experience_component = min(attempts / 25, 1)
mastery = clamp(accuracy_component * (0.55 + 0.45 * experience_component), 0, 1)
```

A newly introduced key therefore cannot instantly become “mastered” after one lucky press.

Weak-key ranking should use a combination of:

- mastery ascending
- recent errors descending
- reaction time above profile median
- recency: avoid drilling the exact same key forever

## 11.8 Recovery

Full recovery scoring is V1.5. However, capture enough active-session data in V1 so it can later be calculated:

- error timestamp
- next correct timestamp
- next 5 correct-key intervals
- subsequent-error count within 10 seconds

Do not expose a fake precision “recovery score” in V1.

---

# 12. Curriculum

The AI must never own pedagogy. The curriculum is explicit, data-driven, versioned, and generated into frontend/backend code.

Set V1 curriculum version:

```text
CURRICULUM_VERSION = "2026.1"
```

## 12.1 Stage schema

Each stage in `shared/curriculum/curriculum.v1.json` must include:

```json
{
  "id": "home_left",
  "order": 2,
  "title": "Left home row",
  "objective": "Build relaxed left-hand home-row control.",
  "introduced_keys": ["a","s","d","f"],
  "allowed_characters": ["a","s","d","f"," "],
  "focus_keys": ["a","s","d","f"],
  "minimum_completed_drills": 2,
  "target_accuracy": 0.92,
  "target_mastery": 0.68,
  "max_hint_rate": 0.15,
  "fallback_drills": ["asdf ..."]
}
```

## 12.2 V1 stage sequence

Implement at least:

```text
00 orientation
01 home_anchors       f j space
02 home_left          a s d f + known
03 home_right         j k l ; + known
04 home_all           full home row + space
05 top_left           q w e r t + known
06 top_right          y u i o p + known
07 top_all            full top + home + space
08 bottom_left        z x c v b + known
09 bottom_right       n m , . / + known
10 lowercase_letters  all lowercase letters + space
11 shift_capitals     uppercase alphabet + Shift behavior
12 punctuation_basic  . , ? ! ' " : ; -
13 numbers            0–9
14 short_sentences    normal beginner prose within learned chars
15 paragraphs         longer normal prose
```

The authored fallback content must remain appropriate for the characters available at each stage. Early constrained stages may use patterns/n-grams rather than natural English sentences.

## 12.3 Finger map

Use standard US QWERTY touch-typing assignments in shared data.

At minimum map:

```text
Left pinky:   Q A Z, Left Shift
Left ring:    W S X
Left middle:  E D C
Left index:   R F V T G B
Right index:  Y H N U J M
Right middle: I K ,
Right ring:   O L .
Right pinky:  P ; : ' " / ? [ ] - =, Right Shift, Enter, Backspace
Thumbs:       Space
```

Store `hand`, `finger`, `home_key`, and `reach_direction` metadata.

## 12.4 Advancement logic

Never advance merely because one lesson was completed.

A stage is eligible to advance when all are true:

- minimum completed normal drills reached
- last two normal drills both meet target accuracy
- each newly introduced key has mastery >= stage target_mastery
- hint rate over those drills <= max_hint_rate
- no newly introduced key has severe repeated-error pattern

Cadence should inform recommendations but must **not** hard-block a beginner in V1.

If criteria are not met, do not show “failed.” Offer:

- one more normal round
- short weak-key drill
- hint/tutorial replay
- easier mode

Difficulty mode changes pacing and challenge, but it must not illegally bypass curriculum constraints unless admin/test mode explicitly does so.

---

# 13. Lesson engine and adaptive selection

The next lesson is selected from structured inputs:

```text
curriculum stage
known/allowed characters
new keys
weak keys
recent errors
recently used content IDs
current difficulty
session goal
user topic preference
hint dependence
```

Implement a deterministic selector first.

Suggested weighted scoring:

```text
candidate score =
  + 4.0 if targets current stage newly introduced keys
  + 3.0 if includes top weak key
  + 2.0 if different from previous content pattern
  + 1.0 if difficulty matches current setting
  - 4.0 if used in last 3 exercises
  - 2.0 if it over-focuses a key practiced heavily in the last 5 minutes
```

AI generation is one possible content source, not the selector itself.

### Repeated-error behavior

If the same key is missed 3 times within 30 seconds:

1. Do not interrupt on the first misses.
2. Add a subtle expected-key highlight.
3. Offer/show the relevant finger reach if hints are enabled.
4. Increase that key's weak-key weight for the next drill.
5. Mention it gently in the session summary if it remains relevant.

No red screen flash, buzzer, “wrong,” harsh reset, or game-over.

---

# 14. Visual keyboard and hand guidance

## VisualKeyboard

Requirements:

- faithful US QWERTY layout
- current expected key highlight
- optional finger-color grouping or finger labels, but do not make the UI visually noisy
- home-row anchor indicators on F/J
- introduced vs not-yet-introduced state
- responsive desktop/tablet sizing
- accessible text labels

## HandGuide

Use lightweight SVG + CSS/Web Animations API. Do not add PixiJS/Phaser just for this.

Behavior:

- semi-transparent hands
- highlight the correct finger
- animate from home position toward the expected key
- return to home position
- fade out
- show only:
  - when a new key is introduced
  - when learner explicitly asks for a hint
  - after repeated miss threshold
  - during short tutorial steps
- stop showing automatically after successful movement patterns
- honor `prefers-reduced-motion` and explicit “Disable hand animations” setting

A simplified instructional hand graphic is acceptable for V1; do not block the project on bespoke illustration.

---

# 15. Frontend screens and UX flow

## 15.1 Public gate

Server rendered, outside React.

- product name/working title
- “Private training access”
- numeric PIN input
- no profile names
- no app data
- generic error

## 15.2 Profile selector

After site PIN:

Heading:

> Who’s training today?

Profile card fields:

- display name
- subtle “PIN” indicator if protected
- no performance metric leakage

Admin entry should be a quiet secondary control, not a giant button.

## 15.3 Resume screen

After learner login, if progress exists:

> Welcome back. Last session you were working on R and T.

Options:

1. Continue
2. Warm up
3. Practice weak keys
4. Fresh challenge
5. Ask the coach

Resume data should include:

- current stage
- last lesson/current lesson
- char position if an active draft exists locally
- weak keys
- recent recommendation
- difficulty
- coach mode

## 15.4 Training screen

Layout:

1. Top: objective, short lesson title, subtle progress
2. Center: typing prompt/current character/word
3. Lower center: visual keyboard + optional hand guidance
4. Side/collapsible: coach, AI training console, hints, settings
5. Bottom/subtle: WPM, cadence, accuracy, optional session time

During active typing, avoid showing too many metrics. Respect “Hide live metrics.”

## 15.5 Session summary

Include:

- duration
- WPM
- accuracy
- cadence
- weak keys
- strong keys
- best moment/personal best if applicable
- hints used
- new keys introduced
- coach note
- recommended next step

Tone example:

> Strong rhythm today. R and T caused a few pauses, but the second half was steadier. Next: a short R/T drill before moving on.

Never:

> You failed.

## 15.6 Settings

Include:

- difficulty: Explore / Practice / Train / Challenge
- coach: Silent / Calm / Competitive
- coach frequency
- font size
- contrast
- keyboard size
- reduce motion
- hand animations on/off
- hide live metrics
- sound on/off
- session length

The app must work well with sound off. Do not make sound part of correctness feedback.

---

# 16. Product visual direction

Build a dark/muted, modern performance-training interface.

Qualities:

- minimal
- clean typography
- high contrast where necessary
- subtle motion
- soft transitions
- modern coding/training-dashboard feel
- sports cadence/performance metaphor
- no noisy texture
- no childish cartoon UI
- no ad-like visual clutter

Use CSS custom properties in `styles/tokens.css` for:

```text
background
surface
surface-raised
text
muted-text
border
accent
accent-soft
warning/subtle-error
success/subtle
focus-ring
spacing scale
radii
shadow
font sizes
```

Do not hard-wire visual tokens throughout components.

Do not rely on an externally hosted font for the private app if a system font stack is sufficient. If a custom font is used, self-host it within the app assets.

---

# 17. Coach system

The coach is conceptually separate from MiniMax.

V1 coach modes:

### Silent

- no unsolicited motivational text
- responds only when explicitly opened/asked

### Calm

- short, low-pressure observations
- emphasizes consistency, technique, improvement

### Competitive

- compares to personal bests only
- suggests small achievable targets
- never insults or shames

Example:

> Last session: 42 WPM. Want to try for 43 without losing rhythm?

Avoid:

> That was terrible.

### Deterministic first

The coach must work without AI. Build a rules engine from session metrics and thresholds.

MiniMax can optionally provide a post-session observation, but if the provider is unavailable, the normal summary and coach still work fully.

Keep the coach visually absent during most active typing. It may appear before/after sessions, for meaningful milestones, on explicit request, or for a brief challenge.

---

# 18. MiniMax integration

## 18.1 Hard boundary

The browser never calls MiniMax directly.

Architecture:

```text
React browser
   -> /api/v1/ai/*
FastAPI Python Worker
   -> MiniMax API
```

The MiniMax API key must never appear in:

- frontend source
- Vite environment variables exposed to browser
- D1
- logs
- error bodies
- `wrangler.jsonc`
- committed `.env` files

## 18.2 Provider adapter

`backend/app/ai/minimax_provider.py` owns all provider-specific code.

Use:

- `httpx.AsyncClient`
- base URL from `MINIMAX_BASE_URL`
- model from `MINIMAX_MODEL`
- `Authorization: Bearer <secret>`
- application timeout ~20 seconds initially
- strict max response size

Do not scatter provider URLs/model strings across routes.

## 18.3 V1 AI endpoints

### `POST /api/v1/ai/lesson`

Modes:

```text
reshuffle
weak_key
harder
easier
challenge
```

Input:

```json
{
  "request_id": "...",
  "schema_version": 1,
  "curriculum_version": "2026.1",
  "stage_id": "top_left",
  "mode": "weak_key",
  "allowed_keys": ["a","s","d","f","j","k","l","r","t"," "],
  "focus_keys": ["r","t"],
  "difficulty": "practice",
  "target_characters": 240,
  "topic": "running"
}
```

Server must cross-check `stage_id` and allowed keys against generated backend curriculum. Do not trust arbitrary client allowed-key expansion.

Output:

```json
{
  "lesson_id": "les_...",
  "schema_version": 1,
  "text": "...",
  "focus_keys": ["r","t"],
  "estimated_characters": 236,
  "source": "cache|ai|fallback",
  "validation": { "passed": true }
}
```

Do not expose provider token counts or API details in learner response.

### `POST /api/v1/ai/explain`

Narrow training questions only.

Example input:

```json
{
  "question": "Why do I keep missing P?",
  "stage_id": "top_right",
  "focus_keys": ["p"],
  "summary": {
    "p_accuracy": 0.78,
    "p_reaction_ms": 620,
    "profile_median_reaction_ms": 390
  }
}
```

Do not send the learner's name, full history, or unrelated personal data.

Return max a few concise paragraphs.

### `POST /api/v1/ai/coach-summary`

Optional post-session event. Do not call automatically if the learner has AI coaching disabled.

Input only compact aggregate metrics and weak/strong keys.

## 18.4 Training Console UX

Do not make this a generic chat app.

Display structured actions:

1. Practice weak keys
2. Start a new challenge
3. Reshuffle this lesson
4. Explain my mistakes
5. Ask the coach
6. Make it easier
7. Make it harder
8. Custom training request

The learner may click, type the number, or enter a short request.

Constrain custom requests to typing/training. Reject obviously unrelated requests politely in the app layer rather than turning the product into a general-purpose AI terminal.

---

# 19. AI prompt design

Keep prompts versioned:

```text
LESSON_PROMPT_VERSION = "lesson-v1"
EXPLAIN_PROMPT_VERSION = "explain-v1"
COACH_PROMPT_VERSION = "coach-v1"
```

## Lesson system prompt requirements

The prompt must state:

- You generate typing practice, not curriculum.
- Use only the exact allowed character set.
- Emphasize focus keys naturally/appropriately.
- No markdown, commentary, title, bullets, quotation marks unless explicitly allowed by stage.
- Output only the drill text.
- Keep tone age-appropriate.
- Avoid copyrighted lyrics.
- Avoid trying too hard to imitate slang.
- Do not mention private user information.

For early constrained stages, tell MiniMax that natural-language quality is secondary to exact allowed-character compliance.

## Explain prompt requirements

- Explain technique concisely.
- Use calm, nonjudgmental language.
- No diagnosis or psychological interpretation.
- Focus on finger reach, timing, hand position, rhythm, and recent metrics supplied.
- Max 4 short paragraphs.

## Coach prompt requirements

- Never shame.
- Compare only to the learner's own recent performance.
- One observation + one next-step suggestion.
- Concise.

---

# 20. AI validation pipeline

The AI is untrusted generated content until validated.

Pipeline:

```text
provider response
 -> extract text
 -> Unicode NFC normalization
 -> strip surrounding markdown fences/labels if accidentally added
 -> length validation
 -> allowed-character validation
 -> curriculum capitalization/punctuation validation
 -> repetition/degeneracy check
 -> age/tone sanity checks
 -> deduplication against recent generated content
 -> accept
 OR one corrective generation attempt
 OR deterministic fallback
```

## 20.1 Allowed-character validator

For lesson generation, every code point must be in the stage's `allowed_characters` set.

No silent replacement of illegal characters. Reject the output.

Normalize straight/curly quote behavior based on stage rules; early stages should simply disallow punctuation not taught.

## 20.2 Length

V1 request bounds:

```text
minimum target: 40 chars
maximum target: 1200 chars
```

Accept a tolerance such as 70%–135% of requested target unless the stage has stricter limits.

## 20.3 Repetition

Reject obviously broken generations such as one character/word repeated for most of the passage unless the stage is explicitly a pattern drill.

## 20.4 Corrective retry

At most one corrective retry for content-validation failure.

Do not create unbounded provider retry loops.

Provider 401/403: no retry; return fallback and record sanitized error classification.

Provider 429/5xx/timeout: normally use cache/fallback immediately; optional single bounded retry only if it does not degrade UX.

---

# 21. AI caching and cost control

Before MiniMax call, compute canonical constraint hash:

```text
SHA-256(
  curriculum_version |
  stage_id |
  sorted_allowed_keys |
  sorted_focus_keys |
  difficulty |
  mode |
  length_bucket |
  normalized_topic |
  prompt_version
)
```

Cache lookup policy:

1. Find validated matching generated content.
2. Exclude content used in the last few exercises.
3. Prefer least-recently-used valid match.
4. Only call MiniMax if no good cached candidate exists or the user explicitly requests a fresh generation.

Record provider/model/prompt version/validation metadata in D1.

Do not use KV just for V1 lesson caching; D1 is sufficient and simpler.

AI calls must remain event-based:

```text
Every keystroke:        0 AI calls
Every exercise:         0 AI calls by default
Explicit reshuffle:     <=1 AI call after cache
Weak-key request:       <=1 AI call after cache
Explain request:        <=1 AI call
Session summary:        0 by default; optional AI call only if enabled
```

---

# 22. Deterministic AI fallbacks

The app must remain useful when MiniMax is unavailable.

Create `backend/app/ai/fallback.py` and equivalent locally bundled fallback content.

Fallback priorities:

1. cached validated generated content
2. authored stage fallback drills
3. deterministic weighted pattern generator using only allowed characters

For weak-key fallback:

- weight focus keys approximately 2–3x normal frequency
- avoid more than 3 identical characters in a row unless the curriculum stage explicitly permits repetitive anchor drills
- include spaces/word-like chunks where stage permits

Return:

```json
"source": "fallback"
```

The learner-facing copy should be neutral, e.g.:

> Fresh AI content isn’t available right now, so I loaded another training drill.

Do not block the session.

---

# 23. IndexedDB local resilience

Use IndexedDB, not `localStorage`, for structured learner state.

Database name:

```text
cadence_local_v1
```

Initial object stores:

```text
meta
active_sessions
pending_sync
generated_lessons
curriculum_cache
profile_cache
```

Never store:

- site PIN
- profile PIN
- admin PIN
- MiniMax API key
- raw auth cookie/session token

HttpOnly auth cookie remains browser-managed.

## 23.1 Active session autosave

Save the active exercise locally:

- after meaningful checkpoints (e.g. every 10 correct chars)
- when lesson changes
- on `visibilitychange` to hidden
- before navigation away where possible
- at exercise completion

Do not perform IndexedDB writes on every keystroke.

## 23.2 Pending sync queue

Each server write operation gets an idempotency key.

If offline/network failure:

- keep operation in `pending_sync`
- continue current training
- retry when `online` fires or the next API operation succeeds
- preserve chronological order for progress/session-finalization operations

## 23.3 V1 offline semantics

V1 requirement:

- once the private app is loaded, the current exercise and locally cached built-in content continue through a temporary network outage
- metrics continue locally
- session data queues for sync

V1 does **not** need guaranteed offline cold-start/reload. Installable PWA/offline cold start is V1.5.

---

# 24. Save versioning and migration

Progress is sacred.

Keep two independent version systems:

1. D1 physical schema migrations (`migrations/000X_*.sql`)
2. Application save format (`save_version` in profile/progress/local state)

Set initial:

```text
SAVE_VERSION = 1
```

Frontend `persistence/migrations.ts` must support:

```ts
migrateSave(input: unknown): CurrentSave
```

Rules:

- detect old version
- migrate forward one version at a time
- add safe defaults
- preserve historical data
- never silently reset a profile because one field is missing
- malformed data should be copied to a recoverable local backup record before the app attempts repair

Backend should reject future unsupported save versions clearly rather than misinterpreting them.

Add migration fixtures from day one, even though V1 starts at version 1. This proves the migration mechanism exists before it is needed.

---

# 25. Test/developer mode

Admin PIN must unlock a dedicated test mode.

Required controls:

- jump to any curriculum stage
- simulate beginner/intermediate/advanced state
- unlock all keys
- set target WPM
- set artificial weak keys
- enable/disable hints
- trigger coach events
- trigger hand tutorial animation
- test AI reshuffle
- test AI weak-key generation
- test session summaries
- reset current session state without deleting profile
- create temporary test profiles

## Isolation rules

A test sandbox must never contaminate real learner metrics.

Preferred implementation:

- default test-mode simulations are in-memory/IndexedDB-only overlays
- if admin creates a persistent test profile, set `is_test_profile=1`
- session writes from test mode use `mode='test'`
- backend excludes test sessions from progress/mastery/personal-best calculations
- admin events record the action type, not simulated sensitive payloads

Add a visible but unobtrusive **TEST MODE** indicator while active so a developer cannot mistake simulated data for real progress.

---

# 26. Session summary generation

Generate a deterministic summary first from metrics.

Summary algorithm should identify at most:

- one strength
- one issue worth training
- one next step
- any genuine personal best

Examples of deterministic logic:

```text
if accuracy improved >= 2 percentage points over recent median:
    strength = "Accuracy was steadier today."

if top weak key has >= 3 errors and reaction time > profile median * 1.25:
    issue = "R caused a few extra pauses."

if cadence_score improved >= 8 over recent median:
    strength = "Rhythm was smoother in the second half."
```

Do not dump every metric.

AI coach summary may refine wording only if enabled; deterministic summary remains stored and authoritative.

---

# 27. Security requirements

## 27.1 API and static access

- Worker runs before static assets.
- `/app/*` requires site/learner/admin session.
- All learner data APIs require learner/admin authorization.
- Same-origin only in production.
- No wildcard CORS.

## 27.2 CSRF

For authenticated state-changing routes:

- require exact approved `Origin`
- require `X-Cadence-Request: 1`
- use `SameSite=Strict` cookie

This project has no cross-site integration requirement in V1.

## 27.3 Security headers

At minimum:

```http
Content-Security-Policy: default-src 'self'; connect-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
Permissions-Policy: camera=(), microphone=(), geolocation=()
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

Adjust `style-src` only as needed for the actual build. Prefer external/self-hosted CSS and avoid remote script dependencies.

## 27.4 Caching

Auth responses and learner API responses:

```http
Cache-Control: no-store
Pragma: no-cache
```

Never edge-cache:

- auth/session responses
- profile data
- progress
- session summaries
- AI content personalized to a profile

Hashed private static assets may be cacheable after Worker auth; the Worker must still gate the request before serving.

## 27.5 Logging

Never log:

- PIN values
- PIN verifier input
- PIN verifier bytes
- session cookie/token
- MiniMax API key
- secret peppers
- full request bodies on auth routes
- full AI prompts containing learner metrics

Allowed logs:

- request route
- sanitized error class
- status
- latency
- generated request correlation ID
- profile ID only where operationally necessary; prefer opaque IDs
- AI provider status category and token counts

## 27.6 XSS/content rendering

AI-generated text must render as text, never via raw HTML/`dangerouslySetInnerHTML`.

Do not add third-party analytics in V1.

---

# 28. Backend implementation notes for Python Workers

Keep dependencies deliberately small.

`pyproject.toml` baseline:

```toml
[project]
name = "learn-to-type"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
  "fastapi",
  "httpx",
  "pydantic"
]

[dependency-groups]
dev = [
  "workers-py",
  "workers-runtime-sdk",
  "pytest",
  "pytest-asyncio"
]
```

If Cloudflare's current quickstart requires slightly different package names/versions, adapt to the installed tooling and document the change.

Do not add:

- SQLAlchemy
- a heavy ORM
- native crypto packages
- Celery
- Redis client
- game engine packages

unless a concrete requirement proves necessary.

Use small repository functions for D1 queries. Keep SQL explicit and testable.

---

# 29. Frontend dependency policy

Start with:

```text
react
react-dom
typescript
vite
vitest
@testing-library/react
@testing-library/user-event
playwright (dev/E2E)
```

A small router dependency is acceptable if it materially simplifies authenticated screen navigation; otherwise keep route/state logic simple.

Do not add in V1 without demonstrated need:

- Redux
- Zustand
- large charting library
- animation framework
- Phaser
- PixiJS
- component mega-library

The typing core must remain plain TypeScript and directly unit-testable.

---

# 30. Testing requirements

No feature is complete until its associated tests pass.

## 30.1 Typing-core unit tests

Required:

- correct character advances
- wrong character does not advance
- wrong character increments error/attempt
- correct-after-error advances
- Backspace cannot erase historical error
- modifier shortcuts ignored
- repeated held key ignored
- Shift/capital handling
- punctuation handling
- focus loss pauses timing
- first key after focus resume excludes hidden interval
- WPM exact fixtures
- accuracy exact fixtures
- reaction-time exact fixtures
- cadence CV exact fixtures
- 600 ms stall fixture
- per-key accumulators
- lesson completion

## 30.2 Curriculum property tests

For every stage/fallback drill:

- every character belongs to allowed set
- introduced keys are a subset of allowed set
- stage ordering unique
- no stage accidentally removes previously known keys unless explicitly designed
- fallback drills nonempty
- AI validator rejects one deliberately forbidden character

## 30.3 Mastery/progression tests

- one correct attempt does not instantly max mastery
- mastery rises with repeated correct attempts
- errors lower mastery relative to equivalent correct sequence
- stage cannot advance after one drill
- stage advances after criteria met
- cadence does not hard-block beginner advancement in V1
- weak-key drill recommendation appears after threshold

## 30.4 Auth tests

- site gate blocks `/app/*` without session
- site PIN success sets secure session
- wrong site PIN generic error
- lockout progression
- rate-limiter response handling
- profile list requires site session
- protected profile requires correct profile PIN
- learner session cannot read another profile
- admin actions reject learner
- admin login rotates session
- logout revokes token
- expired session rejected
- raw tokens never appear in DB fixtures
- bootstrap only once

## 30.5 API tests

- Pydantic input validation
- progress optimistic revision conflict
- session `sync_id` idempotency
- negative/impossible metrics rejected
- test mode does not update normal mastery/progress
- output schemas do not leak internal AI/auth fields

## 30.6 AI tests

Use deterministic fake provider responses. Do not require live MiniMax for normal CI.

Required:

- valid generated lesson accepted
- illegal character rejected
- too-long/too-short rejected
- markdown wrapper normalized/stripped only if safe
- repeated garbage rejected
- one corrective retry maximum
- 401 maps to fallback
- 429 maps to fallback/cache
- timeout maps to fallback/cache
- cache hit prevents provider call
- constraint hash deterministic
- stage/client allowed-key mismatch rejected
- explain route sends only compact supplied metrics

## 30.7 IndexedDB tests

Use a browser-compatible fake IndexedDB for unit tests if needed.

- active session save/load
- migration version
- pending sync retry
- idempotency key preserved
- auth secrets never written

## 30.8 E2E tests

At minimum:

1. Site PIN -> profile selector -> learner profile -> home-row lesson -> mistake -> correct retry -> summary -> logout.
2. Reload after saved progress -> resume flow.
3. MiniMax fake reshuffle -> validated lesson displayed.
4. Network failure during session -> local continuation -> sync after reconnection.
5. Admin PIN -> test mode -> stage jump -> simulated weak key -> exit -> real learner progress unchanged.
6. Reduced-motion mode disables hand reach animation.
7. Hide-live-metrics removes live numbers without breaking final summary.

## 30.9 Security tests

- unauthenticated app asset access rejected/redirected
- `Origin` mismatch rejected
- missing `X-Cadence-Request` rejected for authenticated mutation
- security headers present
- auth/API cache headers no-store
- AI text rendered safely as text
- logs in tests contain no PIN/API/session values

---

# 31. Local development workflow

Target Windows-friendly commands because the user commonly works on Windows, while keeping scripts cross-platform where practical.

## Prerequisites

- current Node.js supported by Vite/Cloudflare tooling
- `uv`
- Wrangler authenticated to the user's Cloudflare account
- Python Workers dependencies installed through `uv`

## Setup

```bash
cd Learn_to_Type
uv sync
cd frontend
npm ci
npm run build
cd ..
```

Create `.dev.vars` from `.dev.vars.example` with local-only values.

Do not commit it.

## Shared generation

```bash
uv run python scripts/generate_shared.py
```

## Local Worker

```bash
uv run pywrangler dev
```

If the actual installed Cloudflare tooling uses a different current command, adapt and update `README.md`/`DEPLOYMENT.md`.

## Tests

```bash
uv run pytest
cd frontend && npm test -- --run
npm run typecheck
npm run build
npm run test:e2e
```

Create `scripts/test.ps1` to run the full sequence and fail on the first error.

---

# 32. Deployment workflow

The user already has Cloudflare hosting. The agent must **inspect existing account/project configuration before creating resources**.

## 32.1 D1

If a D1 database already exists for this project:

- read its database ID
- pin that exact ID in Wrangler config
- do not create a duplicate
- inspect applied migrations

If none exists:

- create one once
- capture the UUID
- pin it in repository config immediately

Apply migrations explicitly; do not run schema-mutating startup code.

Typical flow:

```bash
npx wrangler d1 migrations list learn-to-type --remote
npx wrangler d1 migrations apply learn-to-type --remote
```

Use the real database name/binding configured in the project.

## 32.2 Build

```bash
cd frontend
npm ci
npm run typecheck
npm test -- --run
npm run build
cd ..
uv run pytest
```

## 32.3 Secrets

Create/update Cloudflare Worker Secrets. Never echo them into logs.

## 32.4 Dry run

Run the current equivalent of a Worker deploy dry run if supported by the installed tooling.

## 32.5 Deploy

Research baseline command:

```bash
uv run pywrangler deploy
```

Use the current Cloudflare Python Worker deployment command if tooling has changed.

## 32.6 Custom domain

Attach the Worker to the user's existing intended domain/subdomain. Do not invent a production hostname in code.

Keep frontend and API same-origin.

## 32.7 Bootstrap

After first deploy:

1. Set `BOOTSTRAP_TOKEN` secret.
2. Call one-time bootstrap with chosen site/admin PINs.
3. Verify the site gate works.
4. Remove `BOOTSTRAP_TOKEN` secret.
5. Confirm bootstrap endpoint now refuses further use.

## 32.8 Production smoke tests

Verify:

- `/` shows PIN gate
- `/app/` is inaccessible without session
- correct site PIN enters app
- wrong PIN rate/lockout works
- profile creation/login works
- typing works without server requests per keystroke
- session saves D1 state
- reload resumes
- MiniMax key remains server-side
- AI fallback works when provider is intentionally disabled in staging
- logout revokes access
- security headers present

---

# 33. CI/CD

Preferred GitHub Actions pipeline:

```text
pull request
  -> shared-code generation check
  -> frontend typecheck
  -> frontend unit tests
  -> Python unit/API tests
  -> production frontend build
  -> Playwright E2E against local/staging Worker
  -> migration compatibility check

main
  -> all above
  -> apply production D1 migrations
  -> deploy Worker
  -> post-deploy smoke tests
```

Do not apply production migrations before tests pass.

Do not automatically create a new D1 database during CI.

Cloudflare API tokens used by CI belong in GitHub/Cloudflare secrets, never repository files.

---

# 34. Implementation phases for Codex

Do the work in this order. Keep the repo runnable after each phase.

## Phase 1 — foundation

Deliver:

- repository skeleton
- React/Vite build
- FastAPI Python Worker boots
- Workers Static Assets configured
- `/healthz`
- generated curriculum/finger map pipeline
- initial tests

Acceptance: one Worker serves a protected placeholder app locally.

## Phase 2 — D1 + site gate

Deliver:

- initial D1 migration
- D1 data access layer
- PIN KDF abstraction
- site credential bootstrap
- site PIN gate
- server-side session cookie
- static `/app/*` gating
- login rate limit + D1 lockout

Acceptance: unauthenticated user cannot load the typing app bundle.

## Phase 3 — profiles/admin

Deliver:

- profile selector
- optional profile PIN
- admin PIN
- create/edit profile
- role rotation
- profile isolation tests

Acceptance: two profiles have isolated state; admin controls do not leak to learner.

## Phase 4 — typing vertical slice

Deliver:

- one home-row stage
- deterministic typing engine
- visual prompt
- keyboard
- WPM/accuracy
- session completion
- D1 save
- local active-session IndexedDB
- resume

Acceptance: full login -> lesson -> summary -> reload/resume flow works.

## Phase 5 — curriculum + adaptation

Deliver:

- all V1 curriculum stages
- progression rules
- key mastery
- weak-key ranking
- deterministic lesson selector
- built-in fallback drills

Acceptance: learner progresses by criteria, not simple completion count.

## Phase 6 — cadence + instruction UX

Deliver:

- cadence CV/score
- stalls
- hand/finger SVG animations
- repeated-error hint behavior
- reduced-motion controls

Acceptance: cadence fixture exact; repeated misses trigger gentle guidance only.

## Phase 7 — MiniMax

Deliver:

- provider adapter
- lesson endpoint
- explain endpoint
- optional coach summary endpoint
- validation pipeline
- cache
- deterministic fallback
- AI usage audit rows
- structured Training Console

Acceptance: browser contains no provider key; invalid AI content cannot reach the typing engine.

## Phase 8 — coach + test mode

Deliver:

- Silent/Calm/Competitive deterministic coach
- admin test console
- simulated profile states
- test data isolation

Acceptance: test mode cannot change normal learner mastery/progress.

## Phase 9 — hardening/deploy

Deliver:

- security headers
- CSRF/origin controls
- full E2E tests
- GitHub Actions
- deployment docs
- production/staging config
- smoke tests

Acceptance: all completion criteria below pass.

---

# 35. Definition of done

The Codex agent must not report the project complete unless all applicable items below are satisfied.

## Architecture

- [ ] React/TypeScript/Vite frontend exists.
- [ ] Typing core has no React/FastAPI/MiniMax dependency.
- [ ] FastAPI runs on Cloudflare Python Worker tooling.
- [ ] Workers Static Assets serves the private app.
- [ ] D1 is the durable database.
- [ ] IndexedDB protects active-session continuity.
- [ ] No Phaser/PixiJS/game engine is used in V1.

## Access/security

- [ ] Site PIN is required before private app assets load.
- [ ] Site PIN is never stored plaintext.
- [ ] Profile PIN is optional and isolated.
- [ ] Admin PIN is separate/stronger.
- [ ] Opaque sessions are stored server-side by hash/HMAC only.
- [ ] Cookies are Secure + HttpOnly + SameSite=Strict + `__Host-`.
- [ ] Login rate limiter exists.
- [ ] D1 authoritative lockout exists.
- [ ] Origin/custom-header CSRF defense exists.
- [ ] Security headers exist.
- [ ] Sensitive routes are `no-store`.
- [ ] Secrets do not appear in logs or repo.

## Typing

- [ ] Correct/wrong key behavior deterministic.
- [ ] No per-keystroke cloud/API calls.
- [ ] WPM formula tested.
- [ ] Accuracy formula tested.
- [ ] Cadence metric tested.
- [ ] 600 ms stall fixture passes.
- [ ] Key mastery implemented.
- [ ] Visual keyboard implemented.
- [ ] Finger map implemented.
- [ ] Home-row tutorial implemented.
- [ ] Hand guide implemented and reducible/disableable.
- [ ] Calm repeated-error response implemented.

## Curriculum

- [ ] Curriculum is versioned.
- [ ] Frontend/backend generated curriculum are synchronized.
- [ ] AI cannot introduce unlearned characters.
- [ ] Advancement requires multiple signals.
- [ ] Built-in fallback lessons exist.

## Persistence

- [ ] Multiple profiles remain separate.
- [ ] Session save implemented.
- [ ] Resume implemented.
- [ ] Progress uses revision/optimistic concurrency.
- [ ] `sync_id` idempotency prevents duplicate session writes.
- [ ] Save version exists.
- [ ] Save migration mechanism has tests.
- [ ] D1 migrations are explicit and committed.

## AI

- [ ] MiniMax API called only by backend.
- [ ] `MINIMAX_API_KEY` is Worker Secret.
- [ ] MiniMax model configurable; default M2.7.
- [ ] Lesson reshuffle works.
- [ ] Weak-key generation works.
- [ ] Training explanation works.
- [ ] Structured Training Console exists.
- [ ] Validation rejects illegal characters.
- [ ] Cache used before unnecessary calls.
- [ ] Deterministic fallback works.
- [ ] AI outage does not break typing.

## Coach/test mode

- [ ] Silent coach works.
- [ ] Calm coach works.
- [ ] Competitive coach uses only personal benchmarks.
- [ ] No coach shame/failure language.
- [ ] Test mode is admin protected.
- [ ] Test mode can jump stages/simulate weak keys/trigger UI.
- [ ] Test mode never changes real progress.

## UX/accessibility

- [ ] Dark/muted modern training design.
- [ ] No ad UI/monetization UI.
- [ ] No childish reward economy.
- [ ] No red screen flash or game-over for mistakes.
- [ ] Keyboard navigation works.
- [ ] Visible focus states exist.
- [ ] Reduced motion honored.
- [ ] Sound is optional and not required.
- [ ] Live metrics can be hidden.

## Testing/deploy

- [ ] Backend tests pass.
- [ ] Frontend unit tests pass.
- [ ] TypeScript typecheck passes.
- [ ] Production build passes.
- [ ] E2E tests pass.
- [ ] D1 migrations apply cleanly in non-production before production.
- [ ] Existing Cloudflare database IDs/routes are preserved or deliberately created once.
- [ ] Production smoke test passes, or exact deployment blocker is documented.

---

# 36. Codex operating rules

While implementing:

1. **Inspect before editing.** Read current repository, Wrangler config, migration history, and package files first.
2. **Do not create duplicate Cloudflare resources.** Pin real IDs once known.
3. **Do not commit secrets.** Never place a real MiniMax key, PIN, pepper, or API token in source/config.
4. **Do not remove existing working Cloudflare bindings to simplify the task.** Integrate safely.
5. **Keep the app runnable after each phase.** Prefer vertical slices to giant untested rewrites.
6. **Write tests with the feature.** Do not defer all tests to the end.
7. **Use deterministic fake MiniMax responses in CI.** Live provider testing is a separate staging smoke test.
8. **Do not make AI a dependency of the keystroke path.** Ever.
9. **Do not invent a classical minimax game engine.** It is not part of this scope.
10. **Do not weaken PIN security because this is a small/private app.** A public Cloudflare hostname is internet reachable.
11. **Do not store raw keystroke streams in D1.** Aggregate locally.
12. **Do not silently reset old data.** Migration/repair must preserve it.
13. **Do not use `dangerouslySetInnerHTML` for AI text.**
14. **Do not introduce trackers/ads.**
15. **Do not turn the Training Console into general chat.**
16. **Do not use shame, failure, or punitive beginner UX.**

---

# 37. Required completion report from Codex

At the end, Codex must report:

## Files changed/created

List every significant file grouped by:

- frontend
- backend
- shared/generated
- migrations
- tests
- Cloudflare/deployment
- docs

## Commands run

Include exact commands and whether they passed, including:

- shared generator
- frontend install/build/typecheck/tests
- backend tests
- Wrangler/Python Worker validation
- D1 migration list/apply commands
- deployment command if performed
- smoke tests

## Cloudflare resources

Report:

- Worker name
- D1 binding name
- D1 database name
- pinned database UUID **only if it is not sensitive under the user's repo policy**; otherwise state it is pinned in config
- custom domain used
- rate limiter binding names
- secret names configured, never values

## MiniMax

Report:

- provider adapter file
- model configured
- endpoints implemented
- validation/fallback tests
- whether a live staging provider call was successfully tested

## Known limitations

Explicitly identify anything not verified, such as:

- Cloudflare account auth unavailable in agent environment
- production domain not attached
- live MiniMax credits/key unavailable
- browser-specific behavior not manually tested

Do not claim completion for anything not actually verified.

---

# 38. Open placeholders the agent must preserve, not guess

These values are intentionally not hard-coded in this document:

```text
<production Cloudflare custom domain>
<Cloudflare account ID if required by existing workflow>
<real D1 database UUID>
<real site PIN>
<real admin PIN>
<real learner PINs>
<MINIMAX_API_KEY>
<PIN_PEPPER>
<SESSION_PEPPER>
<BOOTSTRAP_TOKEN>
```

Use existing repository/account configuration where available. If deployment credentials are unavailable, complete local/staging-capable implementation and report the exact blocker; do not fake deployment success.

---

# 39. Product wording reference

Use product copy that is calm, concise, smart, modern, and respectful.

Good:

> Rhythm is improving. Try one more round at the same pace.

> Your left hand is stable. Right index reaches are slowing you down.

> Want a clean run or a harder one?

> That round got messy. Reset your rhythm and take another shot.

Avoid:

> Amazing!!! You’re a SUPER TYPER!!!

> Oops! You made 8 mistakes!

> You failed the lesson.

> That was terrible.

The product should feel like a training console/performance lab, not an elementary-school game.

---

# 40. Final architecture summary

The intended V1 architecture is:

```text
Unauthenticated browser
      |
      v
Cloudflare Python Worker / FastAPI
      |
      +--> server-rendered site PIN gate
      |
valid opaque session
      |
      v
Workers Static Assets -> React/Vite private app
      |
      +--> local TypeScript typing engine
      |       +--> WPM/accuracy/cadence/mastery
      |       +--> visual keyboard/hand hints
      |       +--> IndexedDB active state
      |
      +--> batched HTTPS API
              |
              +--> D1 profiles/progress/sessions/mastery/cache
              |
              +--> MiniMax M2.7 via backend only
                       |
                       +--> validate
                       +--> cache
                       +--> fallback if invalid/unavailable
```

The keystroke loop is local. The cloud provides access control, durable history, profile isolation, cross-request state, administration, and AI. The AI supplies constrained training material; it does not control the curriculum. The site PIN makes the deployed app private; learner/admin PINs protect profile and privileged functions separately.

That is the V1 Codex should build.
