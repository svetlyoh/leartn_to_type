# Cadence — Current Implementation

Last updated: 2026-09-04

## Deployment

- Worker: `leartn-to-type`
- Production URL: `https://leartn-to-type.svetlyoh.workers.dev`
- Runtime: FastAPI on Cloudflare Python Workers
- Static app: React, TypeScript, Vite, delivered through Workers Static Assets
- Database: existing Cloudflare D1 database `learn-to-type`, bound as `DB`
- AI: MiniMax is accessed only by the backend through the Worker secret `MINIMAX_API_KEY`.

The Worker uses the existing D1 database, existing rate-limit bindings, existing domain, and existing Worker secrets. No credentials are stored in the repository.

## Authentication and access

The active learner flow is:

1. Public Cadence landing page.
2. Create an account or sign in with a WebAuthn passkey.
3. Enter the current Cadence access PIN when the account has not accepted the current access-PIN version.
4. Enter a player name for the current login session.
5. Continue to the Cadence main menu.

Passkeys identify the account. The Cadence access PIN is an app-access approval gate. Sessions have a server-side maximum lifetime of 48 hours.

The player-name prompt accepts a blank value and saves `MCP` as the player name. A player can edit their name at any time from the **Player Ready** screen using **Edit name**. Changing a name preserves the selected character and saved training progress.

Normal learner access does not use a learner/profile PIN and does not require admin or test mode. The normal learner menu does not show Admin / Test Mode.

## Player profiles and characters

Each passkey account owns its player profile and associated progress. A newly created player starts with the default Stride character (`runner_01`) and can select one of the existing characters:

- Stride — Steady rhythm
- Flux — Quick recovery
- Vector — Clean precision
- Nova — Calm focus

Character changes do not reset progress.

## Curriculum

Curriculum version: `2026.10`

The core catalog has exactly 64 ordered modules, `module_01` through `module_64`, and exactly 64 built-in seed texts, `builtin_01` through `builtin_64`.

The four curriculum phases are:

1. Foundations, modules 01–16
2. Fluency Tools, modules 17–32
3. Reading and American Literature, modules 33–48
4. Modern Fluency, modules 49–64

Every module has a built-in text that works without MiniMax. Modules 33–48 are original commentary about American/high-school literature and include metadata identifying the work and author. They are not excerpts. Modules 49–64 cover modern topics including running, gaming, technology, AI, security, science, school, original fiction, endurance, and personal bests.

The curriculum is generated from the REV10 catalog into these tracked outputs:

- `shared/curriculum/curriculum.v1.json`
- `frontend/src/generated/curriculum.generated.ts`
- `backend/app/curriculum/generated_curriculum.py`

Existing progress was migrated to closest REV10 module IDs. Key mastery and saved progress data were preserved.

## Training and persistence

- Typing remains deterministic and local on the keystroke path.
- WPM, accuracy, cadence, key mastery, module mastery, saves, resumes, and IndexedDB active-session resilience remain enabled.
- The existing Training Console remains in place; it was not converted to a flyout.
- MiniMax can generate constrained variants and passages, but built-in text is always available as a fallback.

## Security

- Public login controls use a same-origin JavaScript resource at `/auth.js`; this is required because the Content Security Policy deliberately blocks inline scripts.
- Session tokens are opaque, stored server-side by hash, and sent in secure, HttpOnly, SameSite=Strict cookies.
- PIN verifiers use the configured pepper and lockout protections.
- Normal protected APIs require an authenticated passkey account, current access-PIN approval, and ownership of requested learner data.

## Verification completed

- D1 migrations through `0006_curriculum_64_current_lesson.sql` applied to production.
- Backend tests: 10 passing.
- Frontend tests: 17 passing.
- Frontend type-check: passing.
- Production frontend build: passing.
- Production health endpoint: passing.

## Current revision references

- Primary implementation source: `LEARN_TO_TYPE_CODEX_BUILD_SPEC_REV10_64_MODULES_64_TEXTS.md`
- Access behavior: REV9 sections retained by REV10
- Current implementation commit: `2a1705b`
