$ErrorActionPreference='Stop'
python scripts/generate_shared.py
npm --prefix frontend test -- --run
npm --prefix frontend run typecheck
npm --prefix frontend run build
if(Get-Command uv -ErrorAction SilentlyContinue){uv run pytest}else{Write-Warning 'uv unavailable; backend test command skipped'}
