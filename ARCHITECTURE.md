# Architecture

The public root is a minimal PIN form served by FastAPI. A valid D1-backed opaque session is required before the Worker proxies `/app/*` to Workers Static Assets. The React application owns the keystroke loop, metrics, visual keyboard, hand hints, and IndexedDB recovery. Batched session/progress aggregates go to D1. MiniMax is called only by the backend; returned lesson text is constrained, validated, cached, and replaced by deterministic built-in drills on failure.

Human-edited curriculum and keyboard JSON in `shared/` generate typed frontend and Python modules through `scripts/generate_shared.py`.

Pydantic is intentionally consumed through FastAPI rather than directly pinned: Python Workers' Pyodide resolver rejects current native `pydantic-core` wheels when `--no-build` is enforced.
