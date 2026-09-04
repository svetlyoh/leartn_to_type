import{useEffect,useState}from'react';
import{api}from'./api/client';
import{MainMenuScreen}from'./screens/MainMenuScreen';
import{CharacterSelectScreen}from'./screens/CharacterSelectScreen';
import{PlayerMenuScreen}from'./screens/PlayerMenuScreen';
import{AdminScreen}from'./screens/AdminScreen';
import{TrainingScreen}from'./screens/TrainingScreen';

type Session={authenticated:boolean;role:'site'|'learner'|'admin'|null;profile:{id:string;display_name:string;character_id:string}|null};
type Screen='loading'|'main'|'characters'|'how'|'accessibility'|'admin'|'player'|'training'|'closed';

export default function App(){
 const[session,setSession]=useState<Session|null>(null);const[screen,setScreen]=useState<Screen>('loading');
 const refresh=async()=>{const value=await api<Session>('/auth/session');setSession(value);setScreen(value.role==='learner'?'player':value.role==='admin'?'admin':'main')};
 useEffect(()=>{refresh().catch(()=>location.assign('/'))},[]);
 const logout=async()=>{await api('/auth/logout',{method:'POST',body:'{}'});location.assign('/')};
 if(screen==='loading'||!session)return <main className="loading">Calibrating training space…</main>;
 if(screen==='characters')return <CharacterSelectScreen onBack={()=>setScreen('main')} onReady={()=>void refresh()}/>;
 if(screen==='admin')return <AdminScreen authenticated={session.role==='admin'} onAuthenticated={()=>void refresh()} onBack={()=>setScreen(session.role==='admin'?'characters':'main')}/>;
 if(screen==='player'&&session.profile)return <PlayerMenuScreen name={session.profile.display_name} characterId={session.profile.character_id} onCharacterChanged={()=>void refresh()} onTrain={()=>setScreen('training')} onSwitch={async()=>{await api('/auth/profile-exit',{method:'POST',body:'{}'});await refresh()}}/>;
 if(screen==='training'&&session.profile)return <TrainingScreen profileId={session.profile.id} onExit={()=>setScreen('player')} onClosed={()=>setScreen('closed')}/>;
 if(screen==='closed')return <main className="closing"><section><p className="eyebrow">Session saved</p><h1>You can close this tab now.</h1><button onClick={()=>setScreen('main')}>Return to private menu</button></section></main>;
 if(screen==='how')return <main className="how-screen"><button className="quiet" onClick={()=>setScreen('main')}>← Main menu</button><h1>How training works</h1><div className="how-grid"><article><b>01</b><h2>Position first</h2><p>Learn the correct reach before chasing speed.</p></article><article><b>02</b><h2>Build rhythm</h2><p>Cadence measures smoothness once enough samples exist.</p></article><article><b>03</b><h2>Adapt calmly</h2><p>Weak keys shape the next drill without penalties.</p></article></div></main>;
 if(screen==='accessibility')return <main className="form-screen"><button className="quiet" onClick={()=>setScreen('main')}>← Main menu</button><section className="notice"><h1>Accessibility</h1><p>The app follows your system’s reduced-motion and contrast preferences. Learner-specific font, keyboard, hand-guide, and live-metric settings become available after selecting a profile.</p></section></main>;
 return <MainMenuScreen onProfiles={()=>setScreen('characters')} onHow={()=>setScreen('how')} onAccessibility={()=>setScreen('accessibility')} onAdmin={()=>setScreen('admin')} onExit={()=>void logout()}/>;
}
