import {get,put} from './db';
import type{TypingState}from'../typing-core/types';
export type SavedSession={id:string;saveVersion:1;lessonId:string;lessonIndex:number;stageId:string;typingState:TypingState;source:'authored'|'ai'|'cache'|'fallback';updatedAt:string;pendingSync:boolean;localCheckpointId:string};
export const saveActive=(v:SavedSession)=>put('active_sessions',v);
export const loadActive=(id:string)=>get<SavedSession>('active_sessions',id);
