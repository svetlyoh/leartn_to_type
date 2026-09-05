import { FINGER_MAP } from '../../generated/finger-map.generated';
// Geometry must never be derived from the finger map.
export const QWERTY_ROWS = [
  ['`','1','2','3','4','5','6','7','8','9','0','-','='],
  ['q','w','e','r','t','y','u','i','o','p','[',']','\\'],
  ['a','s','d','f','g','h','j','k','l',';',"'",'Enter'],
  ['ShiftLeft','z','x','c','v','b','n','m',',','.','/','ShiftRight'], [' '],
] as const;
export const KEY_GEOMETRY = QWERTY_ROWS.map((row, r) => {
  let x = [0,24,36,0,192][r];
  return row.map(key => {
    const width = key === ' ' ? 336 : key.startsWith('Shift') || key === 'Enter' ? 66 : 48;
    const k = {key,x,y:r*48,width:width-4,height:42,centerX:x+(width-4)/2,centerY:r*48+21};
    x += width; return k;
  });
});
export const geometryFor = (key:string) => KEY_GEOMETRY.flat().find(k=>k.key===key);
const shifted = '~!@#$%^&*()_+{}|:"<>?';
const unshifted = '`1234567890-=[]\\;\',./';
export const physicalKey = (key:string) => shifted.includes(key) && key.length===1 ? unshifted[shifted.indexOf(key)] : key.toLowerCase();
export function fingerFor(target:string) {
  if(target==='ShiftLeft')return {hand:'left',finger:'pinky',home:'a'};
  if(target==='ShiftRight'||target==='Enter')return {hand:'right',finger:'pinky',home:';'};
  const key=physicalKey(target), mapped=FINGER_MAP.keys.find(k=>k.key===key);
  if(mapped) return {hand:mapped.hand==='either'?'right':mapped.hand,finger:mapped.finger,home:mapped.home==='space'?' ':mapped.home};
  const group=[['left','pinky','a','`1'],['left','ring','s','2'],['left','middle','d','3'],['left','index','f','45'],['right','index','j','67'],['right','middle','k','8'],['right','ring','l','9'],['right','pinky',';','0-=[]\\\'']].find(g=>key.length===1&&g[3].includes(key));
  return group?{hand:group[0],finger:group[1],home:group[2]}:undefined;
}
export function placementSignature(moduleId:string,keys:readonly string[],introduced:readonly string[]) {
  return JSON.stringify([moduleId,'asdf jkl;',[...new Set(keys)].sort(),[...introduced].sort()]);
}
