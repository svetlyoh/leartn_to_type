# REV12 implementation and verification report

Date: 2026-09-05

## Deployment

Deployed to the existing Cloudflare Worker. Final version: `21eb1ef1-6544-4f77-9678-a9f4d8d263bd`.
Migration `0008_rev12_passkey_management.sql` was applied to the inspected existing D1 database. No replacement database, account table, identity system, or hosting service was created. Pre-existing uncommitted changes were retained.

## Screenshot defects

| Defect | Confirmed cause | Changes | Verification |
|---|---|---|---|
| Keyboard order | VisualKeyboard iterated FINGER_MAP directly. | `frontend/src/components/training/VisualKeyboard.tsx`, `keyboardGeometry.ts`, `keyboard.css` | Exact QWERTY row-order, stable locked keys/targets, finger ownership and F/J bump tests pass. Local browser and authenticated production rendering inspected. |
| Missing hands | HandGuide rendered a text strip with no hand artwork. | `HandsOverlay.tsx`, shared geometry/CSS, TrainingScreen placement state | Ten addressable fingers, translucent palm/finger paths, J-to-Y keyframe geometry, reduced-motion silhouettes, hide/show and module reset tests pass. Browser inspection confirms visible hands and reappearance after a module change. |
| Unstyled login | Inline CSS was rejected by `style-src 'self'`. | `backend/main.py` external `/auth.css`, responsive title and inherited button font | Production CSS and JS return 200 with correct MIME types; strict CSP retained. Dark public page visually inspected; private app returns 401 without a session. |
| F1/F2 failure | Reproduced an immediate-after-module-change HTTP 409: client stage advanced before the 45-second checkpoint updated the server. Also found unvalidated cache reuse, unconditional cache I/O errors, and fixed fallback reuse. | TrainingScreen checkpoint synchronization and recent previews; backend cache validation/failure isolation; deterministic constrained generator; TrainingConsole early-stage guidance; API error details | Regression test reproduces module transition and requires checkpoint synchronization before generation. Timeout, invalid characters, cache failure and all 64 module constraints tested. Local F2 with Coach open/closed, custom running request, preview and save/start verified. The original screenshot's Anchor Keys error was not reproduced before editing: its original local request succeeded; therefore the transition defect is not claimed as the proven cause of that particular screenshot. |

`Shift + {` hides hands, is displayed on the button, and is excluded from typing input. New placement/module changes still restore hands. F1/F2 work while the Coach input has focus; ordinary input retains its normal behavior.

Starting generated content remains explicit. An unfinished round is checkpointed and retained in IndexedDB under a separate suspended-round record, with a Resume saved round action. The extra suspended record is device-local; ordinary active checkpoint synchronization remains server-backed.

## Passkeys

- Existing implementation: `backend/app/auth/passkeys.py`, existing auth routes in `backend/main.py`; new account management routes in `backend/app/auth/management.py`.
- Installed verifier: Python `webauthn` **3.0.0**, not SimpleWebAuthn. Installed registration signatures were inspected before extending them.
- List: `GET /api/v1/auth/passkeys`.
- Add: `POST /api/v1/auth/passkeys/add/options` and `/add/verify`.
- Remove: `DELETE /api/v1/auth/passkeys/{credential_id}`.
- Options preserve the existing WebAuthn user handle and exclude existing credential IDs.
- Server maximum: options count check, atomic insert predicate and D1 trigger prohibit a third key, including concurrent inserts.
- Challenges remain in `webauthn_challenges`, expire after five minutes, and are consumed atomically with `DELETE … RETURNING`. Add ceremonies additionally require the same account and authenticated session hash. Public registration cannot consume a management challenge.
- Remove is an account-scoped conditional DELETE requiring more than one credential. Concurrent attempts cannot remove the final credential.
- Credential fields: existing credential ID, account ID, public key, signature counter, device type, backup flag, transports, creation and last-use timestamps; new optional nickname. New challenge field: `auth_session_hash`.
- Real verifier tests cover second-key registration, wrong challenge/origin/RP, expiration, session mismatch and replay. Database tests cover account isolation, last-key protection and third-key rejection.
- No credential material is included in this report. No password or learner PIN was added; session lifetime and access-PIN acceptance are unchanged.

## Commands and checks

| Command/check | Result |
|---|---|
| `python scripts/generate_shared.py` | Completed; generated catalog synchronized. |
| `npm test` | 37 tests passing. |
| `.venv/Scripts/python.exe -m pytest -q` | 26 tests passing. |
| `npm run typecheck` | Passing. |
| `npm run build` | Passing. |
| `.tools/uv/bin/uv.exe run --no-sync pywrangler deploy --dry-run` | Passing. |
| `npx wrangler deployments list` | Existing Worker inspected. |
| `npx wrangler d1 info learn-to-type` | Existing database verified against binding. |
| `npx wrangler d1 migrations list learn-to-type --remote` | Only 0008 pending before apply; none pending afterward. |
| `npx wrangler d1 migrations apply learn-to-type --remote` | 0008 applied successfully. |
| `.tools/uv/bin/uv.exe run --no-sync pywrangler deploy` | Deployed successfully, including final shortcut and checkpoint fix. Project-local uv added to PATH for the existing build command. |
| Production HTTP smoke | `/healthz`, `/auth.css`, `/auth.js`: 200; unauthenticated `/app/`: 401; passkey list: 403. CSP unchanged. |
| Browser E2E | Performed through the in-app browser, backed locally by `scripts/rev12_preview.py` and synthetic in-memory SQLite. No Playwright CLI E2E suite was present/run. |

The local preview fixture is not imported by the Worker and never accesses production data or secrets.

## Final authenticated production checks

- Existing passkey sign-in succeeded after the user completed authentication.
- Login & Passkeys displayed `1 of 2`, the correct creation/last-used metadata, enabled Add and disabled Remove.
- Training restored the existing module, mastery and unfinished typing position.
- F2 required confirmation for the unfinished round, then returned a validated current-key preview. Keep current lesson preserved the original round; no generated practice was started on the user's account.
- The final deployed `Shift + {` shortcut was exercised as Shift + [ on a US keyboard. Hands disappeared and Show hands appeared; position and accuracy did not change.
- Final `/auth.css` returned 200 and contained the corrected responsive title and inherited button font.

## Acceptance status

Implementation is deployed and automated checks pass. Authenticated production sign-in, existing progress restoration and account-scoped passkey-list/last-key protection are confirmed. Real-device second-key addition and login/removal acceptance require the user's authenticator and are not claimed complete until observed. The specification's full real-authenticator acceptance remains pending.
