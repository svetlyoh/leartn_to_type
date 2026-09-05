import { useState } from 'react';
import { api } from '../api/client';

export function LoginNameScreen({ onReady }: { onReady: () => void }) {
  const [name, setName] = useState(''); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const submit = async (event: React.FormEvent) => { event.preventDefault(); setBusy(true); setError(''); try { await api('/auth/name', { method: 'POST', body: JSON.stringify({ name }) }); onReady(); } catch { setError('Cadence could not save that name. Try again.'); } finally { setBusy(false); } };
  return <main className="form-screen"><form onSubmit={submit}><p className="eyebrow">Player check-in</p><h1>What’s your name?</h1><p>Enter the name you want Cadence to use this time.</p><label>Player name<input autoFocus value={name} maxLength={40} placeholder="MCP" onChange={event => setName(event.target.value)} /></label><button disabled={busy}>{busy ? 'Getting ready…' : 'Continue'}</button><p className="notice">Leave it blank and your name will be MCP. Haha.</p>{error && <p className="warning" role="alert">{error}</p>}</form></main>;
}
