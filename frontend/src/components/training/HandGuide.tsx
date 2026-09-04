export function HandGuide({target,show,reduceMotion}:{target:string;show:boolean;reduceMotion:boolean}){if(!show)return null;return <div className={`hand-guide ${reduceMotion?'still':''}`} role="status"><span aria-hidden="true">⌁</span> Use the assigned finger for <strong>{target===' '?'space':target}</strong>, then return to home row.</div>}

