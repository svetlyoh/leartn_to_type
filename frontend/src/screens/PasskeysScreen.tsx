import { useEffect, useState } from 'react';
import { api } from '../api/client';

type Passkey = {credential_id:string;nickname:string;backed_up:number;created_at:string;last_used_at:string|null};
type Options = Omit<PublicKeyCredentialCreationOptions,'challenge'|'user'|'excludeCredentials'> & {challenge:string;user:Omit<PublicKeyCredentialUserEntity,'id'>&{id:string};excludeCredentials:{id:string;type:'public-key'}[]};
const decode=(s:string)=>Uint8Array.from(atob(s.replace(/-/g,'+').replace(/_/g,'/').padEnd(Math.ceil(s.length/4)*4,'=')),c=>c.charCodeAt(0));
const encode=(b:ArrayBuffer)=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
export function PasskeysScreen({onBack}:{onBack:()=>void}) {
  const [keys,setKeys]=useState<Passkey[]>([]),[nickname,setNickname]=useState(''),[busy,setBusy]=useState(false),[ready,setReady]=useState(false),[message,setMessage]=useState(''),[removing,setRemoving]=useState<Passkey|null>(null);
  const refresh=async()=>{const result=await api<{passkeys:Passkey[]}>('/auth/passkeys');setKeys(result.passkeys);setReady(true)};
  useEffect(()=>{void refresh().catch(()=>setMessage('Could not load passkeys. Return to the menu and try again.'))},[]);
  const add=async()=>{
    setBusy(true);setMessage('Waiting for your passkey…');
    try {
      const {publicKey:o}=await api<{publicKey:Options}>('/auth/passkeys/add/options',{method:'POST',body:'{}'});
      const credential=await navigator.credentials.create({publicKey:{...o,challenge:decode(o.challenge),user:{...o.user,id:decode(o.user.id)},excludeCredentials:o.excludeCredentials.map(k=>({...k,id:decode(k.id)}))}}) as PublicKeyCredential|null;
      if(!credential)throw new Error('Canceled');
      const response=credential.response as AuthenticatorAttestationResponse;
      await api('/auth/passkeys/add/verify',{method:'POST',body:JSON.stringify({nickname,credential:{id:credential.id,rawId:encode(credential.rawId),type:credential.type,authenticatorAttachment:credential.authenticatorAttachment,response:{clientDataJSON:encode(response.clientDataJSON),attestationObject:encode(response.attestationObject),transports:response.getTransports?.()??[]},clientExtensionResults:credential.getClientExtensionResults()}})});
      await refresh();setNickname('');setMessage('Passkey added to this account. Your player and progress are unchanged.');
    }catch(error){setMessage(error instanceof DOMException&&error.name==='NotAllowedError'?'Passkey request canceled. Try again when ready.':`Passkey could not be added. ${error instanceof Error?error.message:''}`)}
    finally{setBusy(false)}
  };
  const remove=async()=>{
    if(!removing)return;setBusy(true);
    try{await api(`/auth/passkeys/${encodeURIComponent(removing.credential_id)}`,{method:'DELETE',body:'{}'});await refresh();setRemoving(null);setMessage('Passkey removed. Your other passkey still works.')}
    catch{setMessage('Could not remove this passkey. Refresh your list and try again.')}finally{setBusy(false)}
  };
  return <main className="form-screen"><button className="quiet" onClick={onBack}>← Main menu</button><section>
    <p className="eyebrow">Account security</p><h1>Login &amp; Passkeys</h1><p>Use a passkey to sign in to Cadence.</p>
    <h2>{ready?`${keys.length} of 2 passkeys`:'Loading passkeys…'}</h2>
    {keys.map(k=><article className="notice" key={k.credential_id}><h3>{k.nickname||'Passkey'}</h3><p>{k.backed_up?'Synced passkey':'Passkey'} · Added {new Date(k.created_at).toLocaleDateString()}</p><p>Last used {k.last_used_at?new Date(k.last_used_at).toLocaleDateString():'not yet'}</p><button disabled={busy||keys.length<2} onClick={()=>setRemoving(k)}>Remove</button>{keys.length<2&&<p>Add a second passkey before removing this one.</p>}</article>)}
    <label>Optional nickname<input maxLength={60} value={nickname} onChange={e=>setNickname(e.target.value)} placeholder="My laptop"/></label>
    <button disabled={!ready||busy||keys.length>=2} onClick={()=>void add()}>Add another passkey</button>
    {keys.length>=2&&<p>Maximum 2. Remove one before adding another.</p>}
    <p>To replace a passkey, add another first. If you already have two, confirm your remaining passkey works before removing the one you want to replace.</p>
    <p>For best recovery, keep a second passkey on another device or security key.</p>
    {message&&<p role="status">{message}</p>}
    {removing&&<div className="modal" role="dialog" aria-modal="true" aria-label="Remove this passkey?"><div><h2>Remove this passkey?</h2><p>It will no longer be able to sign in to Cadence. Your other passkey will keep working.</p><button disabled={busy} onClick={()=>void remove()}>Remove passkey</button><button disabled={busy} onClick={()=>setRemoving(null)}>Cancel</button></div></div>}
  </section></main>;
}
