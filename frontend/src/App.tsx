import{useEffect,useState}from'react';
import{api}from'./api/client';
import{MainMenuScreen}from'./screens/MainMenuScreen';
import{PlayerMenuScreen}from'./screens/PlayerMenuScreen';
import{TrainingScreen}from'./screens/TrainingScreen';
import{AccessPinScreen}from'./screens/AccessPinScreen';
import{CreatePlayerScreen}from'./screens/CreatePlayerScreen';
import{LoginNameScreen}from'./screens/LoginNameScreen';

type Session={authenticated:boolean;role:'learner'|null;activated:boolean;activation_changed:boolean;name_required:boolean;profile:{id:string;display_name:string;character_id:string}|null};
type Screen='loading'|'activate'|'name'|'main'|'create'|'how'|'accessibility'|'player'|'training'|'closed';

export default function App(){
 const[session,setSession]=useState<Session|null>(null);const[screen,setScreen]=useState<Screen>('loading');
 const refresh=async(target?:Screen)=>{const value=await api<Session>('/auth/session');if(!value.authenticated){location.assign('/');return}setSession(value);setScreen(!value.activated?'activate':value.name_required?'name':target??'main')};
 useEffect(()=>{refresh().catch(()=>location.assign('/'))},[]);
 const logout=async()=>{await api('/auth/logout',{method:'POST',body:'{}'});location.assign('/')};
 if(screen==='loading'||!session)return <main className="loading">Calibrating training space…</main>;
 if(screen==='activate')return <AccessPinScreen changed={session.activation_changed} onUnlocked={()=>void refresh('main')} onExit={()=>void logout()}/>;
 if(screen==='name')return <LoginNameScreen onReady={()=>void refresh('main')}/>;
 if(screen==='create')return <CreatePlayerScreen onBack={()=>setScreen('main')} onCreated={()=>void refresh('player')}/>;
 if(screen==='player'&&session.profile)return <PlayerMenuScreen name={session.profile.display_name} characterId={session.profile.character_id} onCharacterChanged={()=>void refresh('player')} onTrain={()=>setScreen('training')} onSwitch={()=>setScreen('main')}/>;
 if(screen==='training'&&session.profile)return <TrainingScreen profileId={session.profile.id} onExit={()=>setScreen('player')} onClosed={()=>setScreen('closed')}/>;
 if(screen==='closed')return <main className="closing"><section><p className="eyebrow">Session saved</p><h1>You can close this tab now.</h1><button onClick={()=>setScreen('main')}>Return to private menu</button></section></main>;
 if(screen==='how')return <main className="how-screen"><button className="quiet" onClick={()=>setScreen('main')}>← Main menu</button><h1>How training works</h1><div className="how-grid"><article><b>01</b><h2>Position first</h2><p>Learn the correct reach before chasing speed.</p></article><article><b>02</b><h2>Build rhythm</h2><p>Cadence measures smoothness once enough samples exist.</p></article><article><b>03</b><h2>Adapt calmly</h2><p>Weak keys shape the next drill without penalties.</p></article></div></main>;
 if(screen==='accessibility')return <main className="form-screen"><button className="quiet" onClick={()=>setScreen('main')}>← Main menu</button><section className="notice"><h1>Accessibility</h1><p>The app follows your system’s reduced-motion and contrast preferences. Learner-specific font, keyboard, hand-guide, and live-metric settings become available after selecting a profile.</p></section></main>;
 const start=()=>setScreen(session.profile?'player':'create');
 return <MainMenuScreen onStart={start} onCharacter={start} onHow={()=>setScreen('how')} onAccessibility={()=>setScreen('accessibility')} onExit={()=>void logout()}/>;
}
