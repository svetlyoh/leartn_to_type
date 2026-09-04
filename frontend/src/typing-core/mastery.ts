import type {KeyStat} from './types';
export const keyMastery=(s:KeyStat)=>{if(!s.attempts)return 0;const confidence=1-Math.exp(-s.attempts/20);const precision=s.correct/s.attempts;const reaction=s.correct?Math.max(0,Math.min(1,1-(s.totalReactionMs/s.correct-250)/1250)):0;return Math.round(100*confidence*(precision*.8+reaction*.2));};

