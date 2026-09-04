import {get,put} from './db';
export type SavedSession={id:string;saveVersion:1;prompt:string;position:number;updatedAt:string};
export const saveActive=(v:SavedSession)=>put('activeSessions',v);
export const loadActive=(id:string)=>get<SavedSession>('activeSessions',id);

