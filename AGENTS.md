# Project instructions

- Treat `LEARN_TO_TYPE_CODEX_BUILD_SPEC_REV4.md` as the primary source of truth. Use the earlier build spec only where REV4 is silent.
- Preserve user progress and migration history. Never reset D1 or browser data silently.
- Keep the keystroke path local and deterministic. Never call AI per keystroke.
- Never commit PINs, peppers, session tokens, provider keys, account IDs, domain names, or unverified D1 UUIDs.
- Keep generated curriculum files synchronized by running `python scripts/generate_shared.py`.
- Do not deploy until all tests pass and the real existing Cloudflare resources have been inspected.
