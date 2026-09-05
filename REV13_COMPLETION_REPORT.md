# Cadence REV13 Completion Report

Date: 2026-09-05

## Root cause

The normal prompt renderer replaced source spaces with visible middle-dot text inside per-character spans. That removed the actual whitespace break opportunities from the rendered inline stream. Normal drills also lacked the explicit `pre-wrap`, width, and shrink constraints that existed only under `.passage-mode`, so a medium drill behaved as one intrinsic horizontal strip and could force its card/grid child wider than the viewport.

## Implementation

- Added one `getPromptLayoutMode` utility for short, standard, and passage selection using length, lesson kind, and estimated duration.
- Kept every source character in stable DOM order. Space spans now contain their real source space and draw the middle dot with CSS, preserving legal wrapping without changing typing input.
- Added a centered 70ch prompt text block, standard/passage left alignment, short-drill centering, responsive `clamp()` typography, automatic card height, vertical-only passage scrolling, and `min-width: 0` shrink guards.
- Kept the keyboard and SVG hands after the prompt in normal document flow.
- Replaced the old hand binding with a capture-phase `Space + Shift + {` toggle scoped to the mounted training screen. Ordinary Space is applied immediately; if `{` completes the chord, the saved pre-Space typing state is restored before the brace can reach the typing engine. Pressed state clears on keyup, blur, visibility change, and component unmount.
- Updated the Hide/Show controls, tooltip, visible hint, and `aria-keyshortcuts` to `Space+Shift+{`.

## Files changed

- `frontend/src/components/training/promptLayout.ts`
- `frontend/src/components/training/promptLayout.test.ts`
- `frontend/src/screens/TrainingScreen.tsx`
- `frontend/src/styles/rev4.css`
- `frontend/src/config/shortcuts.ts`
- `frontend/src/config/shortcuts.test.ts`
- `frontend/src/hooks/useTrainingShortcuts.ts`
- `frontend/src/components/training/HandGuide.tsx`
- `frontend/src/screens/rev12.test.tsx`
- `frontend/src/screens/rev13.test.tsx`

## Verification

- Frontend unit/component tests: 40 passed (`--maxWorkers=1`). A default parallel run exposed pre-existing cross-file global-mock interference in `rev12.test.tsx`; the same complete suite passes serially and the focused REV12/REV13 run passes.
- Frontend typecheck: passed.
- Production frontend build: passed.
- Backend tests: 26 passed.
- Static regression checks: no remaining production `Shift + {` or `hideHands` binding under `frontend/src`.
- The 80-character component fixture is classified as standard, preserves exact source/visual character order and real spaces, retains completed/current characters, and keeps the physical keyboard after the prompt in DOM flow.

## Browser and production status

The local browser tab opened, but the browser-control layer failed while committing its accessibility snapshot. Therefore viewport pixel geometry, 200% zoom, Coach-open geometry, and production authentication/manual acceptance were not claimed as observed. No deployment was performed.

The implementation and automated DOM/CSS checks are complete; live viewport and production checks remain the final deployment acceptance step.
