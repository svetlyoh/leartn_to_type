import runner01 from '../../assets/characters/runner-01.svg';
import runner02 from '../../assets/characters/runner-02.svg';
import focus01 from '../../assets/characters/focus-01.svg';
import focus02 from '../../assets/characters/focus-02.svg';
export const CHARACTERS=[
 {id:'runner_01',name:'Stride',image:runner01,trait:'Steady rhythm'},
 {id:'runner_02',name:'Flux',image:runner02,trait:'Quick recovery'},
 {id:'focus_01',name:'Vector',image:focus01,trait:'Clean precision'},
 {id:'focus_02',name:'Nova',image:focus02,trait:'Calm focus'},
] as const;
export const CHARACTER_IDS=new Set(CHARACTERS.map(c=>c.id));
