import {render,cleanup} from '@testing-library/react';
import {afterEach,describe,it,expect,vi} from 'vitest';
import {VisualKeyboard} from './VisualKeyboard';
import {HandsOverlay} from './HandsOverlay';
import {FINGER_MAP} from '../../generated/finger-map.generated';
import {geometryFor,placementSignature} from './keyboardGeometry';
afterEach(cleanup);
describe('physical keyboard and hands',()=>{
  it('retains QWERTY DOM order across allowed sets and targets',()=>{
    const {container,rerender}=render(<VisualKeyboard allowed={['f','j',' ']} active="f"/>);
    const order=()=>[...container.querySelectorAll('[data-key]')].map(k=>k.getAttribute('data-key'));
    const before=order();
    expect([...container.querySelectorAll('[data-keyboard-row="1"] [data-key]')].slice(0,10).map(k=>k.getAttribute('data-key')).join('')).toBe('qwertyuiop');
    expect([...container.querySelectorAll('[data-keyboard-row="2"] [data-key]')].slice(0,10).map(k=>k.getAttribute('data-key')).join('')).toBe('asdfghjkl;');
    expect([...container.querySelectorAll('[data-keyboard-row="3"] [data-key]')].slice(1,11).map(k=>k.getAttribute('data-key')).join('')).toBe('zxcvbnm,./');
    expect(container.querySelectorAll('[data-home-bump]').length).toBe(2);
    rerender(<VisualKeyboard allowed={['q','w']} active="y"/>);expect(order()).toEqual(before);
    for(const key of FINGER_MAP.keys){const element=[...container.querySelectorAll('[data-key]')].find(k=>k.getAttribute('data-key')===key.key)!;expect(element.getAttribute('data-finger')).toBe(`${key.hand==='either'?'right':key.hand}.${key.finger}`)}
  });
  it('has ten addressable fingers and real silhouettes in reduced motion',()=>{
    const {container}=render(<svg><HandsOverlay target="y" reduceMotion/></svg>);
    expect(container.querySelectorAll('[data-hand]').length).toBe(2);
    expect(container.querySelectorAll('[data-finger]').length).toBe(10);
    expect(container.querySelector('[data-finger="right.index"]')?.classList.contains('active-finger')).toBe(true);
    expect(container.querySelectorAll('.hand-skin').length).toBe(12);
  });
  it('animates J to Y and back using the keyboard centers',()=>{
    const cancel=vi.fn(),animate=vi.fn((_frames:Keyframe[])=>({cancel}));
    Object.defineProperty(Element.prototype,'animate',{configurable:true,value:animate});
    const {unmount}=render(<svg><HandsOverlay target="y" reduceMotion={false}/></svg>);
    const j=geometryFor('j')!,y=geometryFor('y')!;
    expect(animate.mock.calls[0][0][2].transform).toBe(`translate(${y.centerX-j.centerX}px,${y.centerY-j.centerY}px)`);
    expect(animate.mock.calls[0][0].at(-1)!.transform).toBe('translate(0px,0px)');unmount();expect(cancel).toHaveBeenCalled();
  });
  it('keeps the same placement stable and resets for modules, fingers, shifts and reaches',()=>{
    const signature=placementSignature('m1',['f','j'],['f','j']);
    expect(placementSignature('m1',['j','f','f'],['j','f'])).toBe(signature);
    for(const keys of [['f','j','y'],['f','J'],['1','f'],['f',"'"]])expect(placementSignature('m1',keys,['f','j'])).not.toBe(signature);
    expect(placementSignature('m2',['f','j'],['f','j'])).not.toBe(signature);
  });
});
