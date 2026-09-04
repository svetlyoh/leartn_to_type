# Cadence

Cadence is a calm, adaptive typing trainer built with React/TypeScript and a FastAPI Cloudflare Python Worker. The typing loop runs entirely in the browser; Cloudflare provides private access, durable profile state, and constrained MiniMax assistance.

## Local frontend

```powershell
python scripts/generate_shared.py
npm --prefix frontend install
npm --prefix frontend run typecheck
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

The Worker requires Python 3.13+, `uv`, and authenticated Cloudflare tooling:

```powershell
uv sync
uv run pywrangler dev
```

`wrangler.jsonc` pins the verified `learn-to-type` D1 database and preserves the existing Cloudflare Worker name `leartn-to-type`.
