$ErrorActionPreference='Stop'
python scripts/generate_shared.py
if(-not(Get-Command uv -ErrorAction SilentlyContinue)){throw 'uv and Python 3.13+ are required for the Worker'}
uv run pywrangler dev
