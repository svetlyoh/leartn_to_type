import type { ReactNode } from 'react';
import { fingerFor, KEY_GEOMETRY, physicalKey } from './keyboardGeometry';
import './keyboard.css';
export function VisualKeyboard({active,error,allowed,children}:{active?:string;error?:string;allowed?:readonly string[];children?:ReactNode}) {
  const usable=new Set(allowed?.map(physicalKey));
  return <div className="physical-keyboard"><svg viewBox="0 0 680 278" role="img" aria-label="US QWERTY keyboard" className="keyboard-svg">
    {KEY_GEOMETRY.map((row,index)=><g key={index} data-keyboard-row={index}>{row.map(k=>{
      const owner=fingerFor(k.key);
      return <g key={k.key} data-key={k.key} data-finger={owner?`${owner.hand}.${owner.finger}`:undefined} className={`physical-key ${allowed&&!usable.has(k.key)?'locked':''} ${physicalKey(active??'')===k.key?'target':''} ${physicalKey(error??'')===k.key?'mistake':''}`}>
        <title>{k.key===' '?'Space':k.key} · {owner?`${owner.hand} ${owner.finger}`:'modifier'}</title>
        <rect x={k.x} y={k.y} width={k.width} height={k.height} rx="6"/>
        <text x={k.centerX} y={k.centerY+5} textAnchor="middle">{k.key===' '?'SPACE':k.key.startsWith('Shift')?'Shift':k.key.toUpperCase()}</text>
        {(k.key==='f'||k.key==='j')&&<path data-home-bump={k.key} d={`M${k.centerX-5} ${k.y+34}h10`} className="home-bump"/>}
      </g>;
    })}</g>)}{children}
  </svg></div>;
}
