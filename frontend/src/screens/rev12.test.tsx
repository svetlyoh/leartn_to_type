import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {afterEach,beforeEach,it,expect,vi} from 'vitest';
import 'fake-indexeddb/auto';
import {TrainingScreen} from './TrainingScreen';
import {PasskeysScreen} from './PasskeysScreen';
const response=(data:unknown)=>Promise.resolve({ok:true,json:()=>Promise.resolve(data)} as Response);
beforeEach(()=>{
  localStorage.clear();
  vi.stubGlobal('matchMedia',()=>({matches:false}));
  vi.stubGlobal('fetch',vi.fn((input:string)=>{
    const url=String(input);
    if(url.includes('module-progress'))return response({stage_id:'module_01',title:'Anchor Keys',progress_percent:10,criteria:{completed_drills:{value:0,target:4},accuracy:{value:0,target:.9},introduced_key_mastery:[],hint_rate:{value:0,max:.15}}});
    if(url.includes('progress-dashboard'))return response({resume:{},progress_updated_at:null});
    if(url.includes('ai/lesson'))return response({lesson_id:'fresh',text:'fj jf ff jj f j jf fj f',source:'fallback',lesson_kind:'drill'});
    if(url.includes('training/options'))return response({actions:[{id:'reshuffle',label:'Give me another short pattern',enabled:true}],passage_options:{topic_passages:false}});
    if(url.includes('auth/passkeys'))return response({passkeys:[{credential_id:'a',nickname:'Laptop',created_at:'2026-09-05'}]});
    return response({});
  }));
});
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it('F1 opens Coach; F2 stages valid Anchor Keys practice with Coach closed and open',async()=>{
  render(<TrainingScreen profileId={crypto.randomUUID()} soundEnabled={false} onExit={()=>{}} onClosed={()=>{}}/>);
  await screen.findByText('Anchor Keys');
  fireEvent.keyDown(window,{key:'F2'});
  await screen.findByRole('button',{name:'Start practice'});
  expect(screen.getByText('fj jf ff jj f j jf fj f')).toBeTruthy();
  fireEvent.click(screen.getByRole('button',{name:'Keep current lesson'}));
  fireEvent.keyDown(window,{key:'F2'});
  await screen.findByRole('button',{name:'Start practice'});
  fireEvent.click(screen.getByRole('button',{name:'Start practice'}));
  await waitFor(()=>expect(screen.queryByRole('button',{name:'Start practice'})).toBeNull());
  fireEvent.keyDown(window,{key:'F1'});
  expect(screen.getByRole('complementary',{name:'Training Console'})).toBeTruthy();
  await screen.findByText('Full sentences unlock after you learn more letters. I can build a fresh pattern with the keys you know now.');
  const calls=vi.mocked(fetch).mock.calls.filter(call=>String(call[0]).includes('ai/lesson'));
  expect(calls.length).toBe(2);
  expect(JSON.parse(calls[0][1]!.body as string).curriculum_version).toBe('2026.10');
});
it('hands hide and can be restored manually',async()=>{
  const {container}=render(<TrainingScreen profileId={crypto.randomUUID()} soundEnabled={false} onExit={()=>{}} onClosed={()=>{}}/>);
  await screen.findByText('Anchor Keys');
  expect(container.querySelectorAll('[data-hand]').length).toBe(2);
  fireEvent.click(screen.getByRole('button',{name:'Hide hands'}));
  expect(container.querySelectorAll('[data-hand]').length).toBe(0);
  fireEvent.click(screen.getByRole('button',{name:'Show hands'}));
  expect(container.querySelectorAll('[data-hand]').length).toBe(2);
  fireEvent.keyDown(window,{key:' ',code:'Space'});
  fireEvent.keyDown(window,{key:'{',code:'BracketLeft',shiftKey:true});
  expect(container.querySelectorAll('[data-hand]').length).toBe(0);
  expect(screen.getByText(/Round progress/).textContent).toContain('0 /');
  fireEvent.keyUp(window,{key:' ',code:'Space'});
  fireEvent.keyDown(window,{key:' ',code:'Space'});
  fireEvent.keyDown(window,{key:'{',code:'BracketLeft',shiftKey:true});
  expect(container.querySelectorAll('[data-hand]').length).toBe(2);
  fireEvent.keyUp(window,{key:' ',code:'Space'});
  fireEvent.keyDown(window,{key:'{',code:'BracketLeft',shiftKey:true});
  expect(container.querySelectorAll('[data-hand]').length).toBe(2);
});
it('passkey UI protects the final credential and shows 2 of 2 with Add disabled',async()=>{
  const {unmount}=render(<PasskeysScreen onBack={()=>{}}/>);
  await screen.findByText('1 of 2 passkeys');
  expect((screen.getByRole('button',{name:'Remove'}) as HTMLButtonElement).disabled).toBe(true);
  unmount();
  vi.mocked(fetch).mockImplementation(()=>response({passkeys:[{credential_id:'a',created_at:'2026-09-05'},{credential_id:'b',created_at:'2026-09-05'}]}));
  render(<PasskeysScreen onBack={()=>{}}/>);
  await screen.findByText('2 of 2 passkeys');
  expect((screen.getByRole('button',{name:'Add another passkey'}) as HTMLButtonElement).disabled).toBe(true);
});
it('synchronizes a new module before F2 generation instead of waiting for autosave',async()=>{
  let serverStage='module_01';
  const original=vi.mocked(fetch).getMockImplementation()!;
  vi.mocked(fetch).mockImplementation((input,init)=>{
    const url=String(input);
    if(url.includes('session-checkpoint')){serverStage=JSON.parse(init!.body as string).stage_id;return response({})}
    if(url.includes('module-progress'))return response({stage_id:serverStage,title:serverStage,progress_percent:10,criteria:{completed_drills:{value:0,target:4},accuracy:{value:0,target:.9},introduced_key_mastery:[],hint_rate:{value:0,max:.15}}});
    if(url.includes('ai/lesson'))expect(JSON.parse(init!.body as string).stage_id).toBe(serverStage);
    return original(input,init);
  });
  render(<TrainingScreen profileId={crypto.randomUUID()} soundEnabled={false} onExit={()=>{}} onClosed={()=>{}}/>);
  await screen.findByText(/module_01/);
  for(const key of 'f j f j fj jf f j jf fj')fireEvent.keyDown(document.body,{key});
  fireEvent.click(await screen.findByRole('button',{name:/Next training round/}));
  fireEvent.keyDown(window,{key:'F2'});
  await screen.findByRole('button',{name:'Start practice'});
  expect(serverStage).toBe('module_02');
});
