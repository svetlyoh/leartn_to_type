import type {InputEvent,TypingState} from './types';
export const createState=(prompt:string):TypingState=>({prompt,position:0,attempts:0,correctChars:0,errors:0,startedAt:null,lastCorrectAt:null,activeMs:0,intervals:[],stalls:0,pausedAt:null,complete:false,keyStats:{},lastErrorKey:null,repeatErrors:0});
const printable=(key:string)=>key.length===1||key==='Enter';
export function applyInput(state:TypingState,event:InputEvent):TypingState{
 if(state.complete||event.repeat||event.ctrlKey||event.metaKey||event.altKey||!printable(event.key)||event.key==='Backspace')return state;
 const next={...state,keyStats:{...state.keyStats},intervals:[...state.intervals]};
 if(next.startedAt===null)next.startedAt=event.time;
 next.attempts++; const expected=next.prompt[next.position]; const key=event.key==='Enter'?'\n':event.key;
 const stat={...(next.keyStats[expected]??{attempts:0,correct:0,errors:0,totalReactionMs:0})}; stat.attempts++;
 if(key===expected){const base=next.lastCorrectAt??next.startedAt;const delta=Math.max(0,event.time-base);if(next.lastCorrectAt!==null){next.intervals.push(delta);if(delta>=600)next.stalls++;}stat.correct++;stat.totalReactionMs+=delta;next.correctChars++;next.position++;next.lastCorrectAt=event.time;next.lastErrorKey=null;next.repeatErrors=0;next.complete=next.position===next.prompt.length;}
 else{stat.errors++;next.errors++;next.repeatErrors=next.lastErrorKey===expected?next.repeatErrors+1:1;next.lastErrorKey=expected;}
 next.keyStats[expected]=stat;next.activeMs=Math.max(0,event.time-next.startedAt);return next;
}
export const pause=(s:TypingState,time:number)=>s.pausedAt===null?{...s,pausedAt:time}:s;
export const resume=(s:TypingState,time:number)=>s.pausedAt===null?s:{...s,lastCorrectAt:s.lastCorrectAt===null?null:s.lastCorrectAt+(time-s.pausedAt),startedAt:s.startedAt===null?null:s.startedAt+(time-s.pausedAt),pausedAt:null};

