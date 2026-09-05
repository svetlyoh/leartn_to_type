import { useEffect, useRef } from "react";
import { isHandsToggleChord, shortcutFor } from "../config/shortcuts";

type Options = { canNext:boolean; consoleOpen:boolean; onNext:()=>void; onToggleConsole:()=>void; onReshuffle:()=>void; onReturn:()=>void; onToggleHands:()=>void; onHandsChord:()=>void; onSpaceReleased:()=>void };

export function useTrainingShortcuts(options: Options) {
  const latest = useRef(options);
  latest.current = options;
  useEffect(() => {
    const pressed = new Set<string>();
    const handler = (event: KeyboardEvent) => {
      const target = event.target;
      if (target instanceof Element && target.matches('input,button,select,textarea,[contenteditable="true"]')) return;
      if (isHandsToggleChord(event, pressed)) {
        event.preventDefault();
        event.stopImmediatePropagation();
        latest.current.onHandsChord();
        latest.current.onToggleHands();
        return;
      }
      pressed.add(event.code);
      const action = shortcutFor(event);
      if (action === "toggleAI") { event.preventDefault(); latest.current.onToggleConsole(); }
      else if (action === "returnToTraining" && latest.current.consoleOpen) { event.preventDefault(); latest.current.onReturn(); }
      else if (action === "reshuffle") { event.preventDefault(); latest.current.onReshuffle(); }
      else if (action === "nextRound" && latest.current.canNext) { event.preventDefault(); latest.current.onNext(); }
    };
    const release = (event: KeyboardEvent) => { pressed.delete(event.code); if (event.code === "Space") latest.current.onSpaceReleased(); };
    const clear = () => { pressed.clear(); latest.current.onSpaceReleased(); };
    const visibility = () => { if (document.visibilityState === "hidden") clear(); };
    addEventListener("keydown", handler, true);
    addEventListener("keyup", release, true);
    addEventListener("blur", clear);
    document.addEventListener("visibilitychange", visibility);
    return () => {
      removeEventListener("keydown", handler, true);
      removeEventListener("keyup", release, true);
      removeEventListener("blur", clear);
      document.removeEventListener("visibilitychange", visibility);
    };
  }, []);
}
