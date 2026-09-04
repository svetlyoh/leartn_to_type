# Deployment

Deployment is deliberately blocked until the account resources are known.

1. Install Python 3.13+, `uv`, Node, and authenticate Wrangler.
2. Inspect existing Workers, routes, D1 databases, and migration history.
3. Replace `<REAL_D1_DATABASE_UUID_REQUIRED>` in `wrangler.jsonc` with the verified UUID; do not create a duplicate database.
4. Run generator, frontend tests/typecheck/build, backend tests, and a Python Worker dry run.
5. Apply D1 migrations explicitly.
6. Configure `MINIMAX_API_KEY`, `PIN_PEPPER`, `SESSION_PEPPER`, and temporary `BOOTSTRAP_TOKEN` as Worker secrets.
7. Deploy with `uv run pywrangler deploy`, attach the intended existing domain, bootstrap once, then delete `BOOTSTRAP_TOKEN`.
8. Run the smoke tests in section 32.8 of the build specification.
