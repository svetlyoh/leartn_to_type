import {FINGER_MAP} from '../../generated/finger-map.generated';
export function VisualKeyboard({active,error}:{active?:string;error?:string}){return <div className="keyboard" aria-label="US QWERTY home row">{FINGER_MAP.keys.map(k=><span key={k.code} className={`key ${active===k.key?'active':''} ${error===k.key?'error':''}`} title={`${k.hand} ${k.finger}`}>{k.key===' '?'space':k.key}</span>)}</div>}

