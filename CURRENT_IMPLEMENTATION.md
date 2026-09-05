# Cadence — Current Implementation

Last updated: 2026-09-05

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
4. On first authorized use only, save a player name and optional school/grade details to the account profile.
5. Continue to the Cadence main menu.

Passkeys identify the account. The Cadence access PIN is an app-access approval gate. Sessions have a server-side maximum lifetime of 48 hours.

The player-name prompt accepts a blank value and saves `MCP` persistently. Returning passkey users are recognized from their existing server profile and are not prompted again. A player can edit their name at any time from **Player Ready** without changing identity, character, progress, mastery, or history.

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
- REV11 adds server-first checkpoint reconciliation, completed-session history, key-evidence updates, a functional progress dashboard, deterministic weak-key/diagnostic practice, and per-round hand-guide reset behavior.
- Player preferences include Midnight, Soft Slate, and Soft Plum themes plus a locally generated soft typing sound toggle. Preferences save locally for startup and to the authenticated server profile.
- The F1 Training Console custom request flow now shows loading, success/error feedback, a validated preview, and explicit start/try-another/keep-current actions.

## Security

- Public login controls use a same-origin JavaScript resource at `/auth.js`; this is required because the Content Security Policy deliberately blocks inline scripts.
- Session tokens are opaque, stored server-side by hash, and sent in secure, HttpOnly, SameSite=Strict cookies.
- PIN verifiers use the configured pepper and lockout protections.
- Normal protected APIs require an authenticated passkey account, current access-PIN approval, and ownership of requested learner data.

## Verification completed

- D1 migrations through `0008_rev12_passkey_management.sql` applied to production.
- Backend tests: 26 passing.
- Frontend tests: 37 passing.
- Frontend type-check: passing.
- Production frontend build: passing.
- Cloudflare deployment dry-run: passing.
- Production landing/theme/footer/About smoke check: passing.

## Current revision references

- Primary implementation source: `LEARN_TO_TYPE_CODEX_BUILD_SPEC_REV10_64_MODULES_64_TEXTS.md`
- Access behavior: REV9 sections retained by REV10
- Current deployed revision: REV12 (REV13 implemented locally; deployment acceptance pending)


## REV12

- Physical QWERTY geometry is independent of the finger map. Locked keys stay in place, and F/J have home bumps.
- Translucent SVG hands share key centers with the keyboard. Introduced reaches animate locally; reduced motion retains silhouettes and directional indicators.
- Hide hands remembers the current placement; a changed module/reach restores the hands. Show hands restores them.
- Public `/auth.css` fixes the inline-style/CSP conflict. `/auth.js` remains public and `/app/*` stays gated.
- Login & Passkeys lists the current account's credentials, supports adding a second, and blocks third credentials and deletion of the last credential. Existing Python `webauthn` 3.0.0 remains the verifier.
- Passkey registration challenges are consumed atomically, expire after five minutes, and management challenges are bound to the existing authenticated session.
- Practice revalidates cached content, tracks recently offered text, and uses deterministic constrained variants when AI fails. Optional cache read/write failures cannot discard usable fallback content.
- New-module checkpoints synchronize before generation, preventing the reproduced immediate-F2 stage mismatch. Generated content has an explicit preview. Save & start preserves an unfinished local round with a Resume saved round action.
- Full verification details and remaining real-authenticator acceptance checks are tracked in `REV12_COMPLETION_REPORT.md`.

## REV13 (local implementation)

- Prompt layout is selected centrally as short, standard, or passage from text length, lesson kind, and estimated duration.
- Medium drills use a centered, readable multiline block; actual semantic spaces remain in the DOM while CSS supplies visible middle dots, so per-character styling no longer removes wrapping opportunities.
- Prompt, lesson, console, and training-grid sizing now shrink safely with no horizontal prompt scrolling; the card grows vertically and the keyboard/hands remain in normal flow below it.
- The hands shortcut is the training-only `Space + Shift + {` toggle. Ordinary Space remains immediate, and a completed toggle chord restores the pre-Space typing state so position and metrics do not change.
- Verification details and outstanding live viewport/production acceptance are tracked in `REV13_COMPLETION_REPORT.md`.
