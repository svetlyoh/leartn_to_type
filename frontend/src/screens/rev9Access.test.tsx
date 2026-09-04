import{render,screen}from'@testing-library/react';
import{describe,expect,it}from'vitest';
import{MainMenuScreen}from'./MainMenuScreen';
import{CreatePlayerScreen}from'./CreatePlayerScreen';

const noop=()=>undefined;
describe('simplified learner access',()=>{
 it('keeps Start / Continue available and removes Admin / Test mode',()=>{render(<MainMenuScreen onStart={noop} onCharacter={noop} onHow={noop} onAccessibility={noop} onExit={noop}/>);expect(screen.getByRole('button',{name:'Start / Continue'})).toBeTruthy();expect(screen.queryByText('Admin / Test mode')).toBeNull()});
 it('creates a player without an optional profile PIN and preserves all four characters',()=>{render(<CreatePlayerScreen onBack={noop} onCreated={noop}/>);expect(screen.queryByText(/profile pin/i)).toBeNull();for(const text of['Stride','Flux','Vector','Nova'])expect(screen.getByText(text)).toBeTruthy()});
});
