export const TRAINING_SHORTCUTS={nextRound:'Shift+Enter',toggleAI:'F1',reshuffle:'F2',returnToTraining:'Escape'} as const;
export type ShortcutAction=keyof typeof TRAINING_SHORTCUTS;
export function shortcutFor(event:Pick<KeyboardEvent,'key'|'shiftKey'|'ctrlKey'|'metaKey'|'altKey'>):ShortcutAction|null{
 if(event.ctrlKey||event.metaKey||event.altKey)return null;
 if(event.key==='F1')return'toggleAI';if(event.key==='F2')return'reshuffle';if(event.key==='Escape')return'returnToTraining';if(event.key==='Enter'&&event.shiftKey)return'nextRound';return null;
}
