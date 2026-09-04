$ErrorActionPreference='Stop'
python scripts/generate_shared.py
npm --prefix frontend run typecheck
npm --prefix frontend run build
