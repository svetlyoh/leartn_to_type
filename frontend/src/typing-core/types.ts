export type KeyStat={attempts:number;correct:number;errors:number;totalReactionMs:number};
export type TypingState={prompt:string;position:number;attempts:number;correctChars:number;errors:number;startedAt:number|null;lastCorrectAt:number|null;activeMs:number;intervals:number[];stalls:number;pausedAt:number|null;complete:boolean;keyStats:Record<string,KeyStat>;lastErrorKey:string|null;repeatErrors:number};
export type InputEvent={key:string;code:string;time:number;repeat?:boolean;ctrlKey?:boolean;metaKey?:boolean;altKey?:boolean};

