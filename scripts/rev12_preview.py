"""Local-only REV12 acceptance fixture. Never imported by the Worker entrypoint.

Runs against in-memory SQLite with synthetic users. No production secrets or data.
"""
import sys
import types
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parents[1] / 'backend'), str(Path(__file__).resolve().parents[1] / 'tests/backend')]
sys.modules['workers'] = types.SimpleNamespace(asgi=types.SimpleNamespace(entrypoint=lambda x:x))
import main
from test_rev12 import DB
from fastapi.responses import FileResponse
import uvicorn

db=DB(); timestamp=main.iso(main.now())
db.conn.execute("INSERT INTO users(id,webauthn_user_id,temporary_handle,accepted_activation_version,created_at,updated_at) VALUES('preview',X'0102','preview',1,?,?)",(timestamp,timestamp))
db.conn.execute("INSERT INTO profiles(id,user_id,display_name,curriculum_version,created_at,updated_at) VALUES('preview','preview','Preview','2026.10',?,?)",(timestamp,timestamp))
db.conn.execute("INSERT INTO progress(profile_id,save_version,curriculum_version,stage_id,current_lesson_id,updated_at) VALUES('preview',1,'2026.10','module_01','module_01_drill_01',?)",(timestamp,))
db.conn.execute("INSERT INTO passkey_credentials(credential_id,user_id,public_key,created_at,nickname) VALUES('YQ','preview',X'01',?,'Preview passkey')",(timestamp,))
binding=types.SimpleNamespace(DB=db,CURRICULUM_VERSION='2026.10',MINIMAX_MODEL='test')
stage = sys.argv[1] if len(sys.argv)>1 else 'module_01'
if not main.curriculum_stage(stage): raise ValueError('Unknown preview module')
db.conn.execute('UPDATE progress SET stage_id=?',(stage,))
async def preview_session(request): return {'role':'learner','user_id':'preview','profile_id':'preview','name_confirmed':1,'login_name':'Preview'}
main.current_session=preview_session
async def assets(path,request):
    root=(Path(__file__).resolve().parents[1]/'frontend/dist/app').resolve()
    target=(root/(path or 'index.html')).resolve()
    if not target.is_relative_to(root):raise main.HTTPException(404)
    return FileResponse(target)
main.serve_asset=assets
async def app(scope,receive,send):
    scope['env']=binding
    await main.app(scope,receive,send)
if __name__=='__main__': uvicorn.run(app,host='127.0.0.1',port=int(sys.argv[2]) if len(sys.argv)>2 else 8765)
