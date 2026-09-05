import { useEffect,useRef,useState } from 'react';
import { fingerFor,geometryFor,physicalKey } from './keyboardGeometry';
export function HandsOverlay({target: currentTarget,reduceMotion,introduced=[]}:{target:string;reduceMotion:boolean;introduced?:readonly string[]}) {
  const [step,setStep]=useState(0);
  const introduction=introduced.join('');
  useEffect(()=>{setStep(0);if(reduceMotion||!introduction)return;let count=0;const timer=setInterval(()=>{count++;setStep(count);if(count>=introduction.length)clearInterval(timer)},2400);return()=>clearInterval(timer)},[introduction,reduceMotion]);
  const target=introduced[step]??currentTarget;
  const root=useRef<SVGGElement>(null),owner=fingerFor(target),destination=geometryFor(physicalKey(target)),home=geometryFor(owner?.home??' ');
  const needsShift=target.length===1&&physicalKey(target)!==target;
  const shiftHome=geometryFor(owner?.hand==='left'?';':'a');
  const shiftKey=geometryFor(owner?.hand==='left'?'ShiftRight':'ShiftLeft');
  useEffect(()=>{
    if(reduceMotion||!destination||!home||!owner)return;
    const finger=root.current?.querySelector(`[data-finger="${owner.hand}.${owner.finger}"]`);
    if(!finger||typeof finger.animate!=='function')return;
    const reach=`translate(${destination.centerX-home.centerX}px,${destination.centerY-home.centerY}px)`;
    const animation=finger.animate([{transform:'translate(0px,0px)',offset:0},{transform:'translate(0px,0px)',offset:.2},{transform:reach,offset:.45},{transform:reach,offset:.65},{transform:'translate(0px,0px)',offset:1}],{duration:2200,easing:'ease-in-out',fill:'none'});
    return ()=>animation.cancel();
  },[target,reduceMotion,destination,home,owner?.hand,owner?.finger]);
  return <g ref={root} className="hands-overlay" aria-label="Two human hands at home position">
    {(['left','right'] as const).map(hand=>{
      const keys=hand==='left'?['a','s','d','f']:['j','k','l',';'],fingers=hand==='left'?['pinky','ring','middle','index']:['index','middle','ring','pinky'];
      const start=geometryFor(keys[0])!.centerX,end=geometryFor(keys[3])!.centerX,inner=hand==='left'?end:start,thumbX=hand==='left'?inner+62:inner-62;
      return <g key={hand} data-hand={hand}>
        <path className="hand-skin" d={`M${start-12} 173 Q${start-19} 197 ${start+9} 218 L${start+27} 257 Q${(start+end)/2} 270 ${end-19} 257 L${end-4} 220 Q${end+20} 201 ${end+12} 173 Z`}/>
        {keys.map((key,i)=>{const k=geometryFor(key)!;return <g key={key} data-finger={`${hand}.${fingers[i]}`} className={owner?.hand===hand&&owner.finger===fingers[i]?'active-finger':''}>
          <path className="hand-skin" d={`M${k.centerX-12} 184 L${k.centerX-10} ${k.centerY+3} Q${k.centerX} ${k.centerY-18} ${k.centerX+10} ${k.centerY+3} L${k.centerX+13} 184 Z`}/>
          <path className="hand-crease" d={`M${k.centerX-6} 150q6 -3 12 0 M${k.centerX-6} 163q6 -3 12 0`}/>
        </g>})}
        <g data-finger={`${hand}.thumb`} className={owner?.finger==='thumb'&&hand==='right'?'active-finger':''}><path className="hand-skin" d={hand==='left'?`M${inner+7} 201 Q${inner+23} 193 ${thumbX-8} 198 Q${thumbX+12} 204 ${thumbX-3} 215 L${inner+17} 244 L${inner-8} 238 Q${inner+12} 219 ${inner+7} 201 Z`:`M${inner-7} 201 Q${inner-23} 193 ${thumbX+8} 198 Q${thumbX-12} 204 ${thumbX+3} 215 L${inner-17} 244 L${inner+8} 238 Q${inner-12} 219 ${inner-7} 201 Z`}/></g>
        <path className="hand-crease" d={`M${start+23} 208 Q${(start+end)/2} 224 ${end-19} 206`}/>
      </g>;
    })}
    {home&&destination&&owner&&<g className="reach-indicator"><circle cx={home.centerX} cy={home.centerY} r="18"/>{home!==destination&&<><path d={`M${home.centerX} ${home.centerY}L${destination.centerX} ${destination.centerY}`}/><circle cx={destination.centerX} cy={destination.centerY} r="17"/><text x={destination.centerX+16} y={destination.centerY-12}>↗</text></>}</g>}
    {needsShift&&shiftHome&&shiftKey&&<g className="reach-indicator" aria-label="Hold Shift with the opposite pinky"><circle cx={shiftKey.centerX} cy={shiftKey.centerY} r="19"/><path d={`M${shiftHome.centerX} ${shiftHome.centerY}L${shiftKey.centerX} ${shiftKey.centerY}`}/></g>}
  </g>;
}
