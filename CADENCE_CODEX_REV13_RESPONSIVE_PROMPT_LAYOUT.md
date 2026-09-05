# Cadence — Codex Implementation Instructions
## REV13 — Responsive Typing Prompt Layout and Zero Horizontal Overflow

**Date:** September 2026  
**Project:** Learn_to_Type / Cadence  
**Production host:** existing Cloudflare deployment  
**Baseline:** REV12 implementation and verification report

---

# 0. Purpose

This is a focused follow-up to REV12.

REV12 is already deployed and verified for:

- true QWERTY keyboard order;
- translucent human hand overlay;
- hand hide/show behavior;
- dark public login styling;
- Login & Passkeys management;
- F1/F2/custom-practice reliability;
- existing Cloudflare/D1/passkey/MiniMax architecture.

Do **not** rewrite or regress those features.

The remaining visible defect is the typing prompt itself.

The attached production screenshot shows an approximately 80-character drill rendered as one oversized horizontal line. The line leaves the typing card and continues far beyond the viewport on the right.

That must never happen.

Cadence must have **zero horizontal text overflow** in normal typing, passage mode, mobile, tablet, or desktop layouts.

---

# 1. Root UI problem to inspect

Before changing CSS, inspect the current implementation and determine the exact source of the overflow.

Likely areas:

```text
TypingPrompt
PromptLine
TypingSurface
PassageTypingSurface
training.css / prompt CSS
per-character span rendering
current-character highlight
white-space / nowrap declarations
display:flex behavior
min-width / width:max-content
overflow-x
font-size rules
```

Do not assume this is only a parent-container width issue.

The likely failure is that the prompt renderer is preserving every character in one non-wrapping inline/flex row.

Inspect the DOM in the browser.

Report the exact cause in the completion report.

---

# 2. Required layout model

Use three presentation bands.

The text-length thresholds may be tuned slightly after inspection, but the behavior must follow this model.

## A. Short drill

Typical:

```text
1–45 characters
```

Behavior:

- one line when it naturally fits;
- centered horizontally;
- larger typing font;
- no forced wrapping when unnecessary.

Suggested typography:

```text
font-size: clamp(2rem, 1.5rem + 1.5vw, 3rem)
line-height: 1.35
```

## B. Standard / medium drill

Typical:

```text
46–220 characters
```

This is the situation visible in the current screenshot.

Behavior:

- wrap naturally into approximately 2–5 lines;
- never exceed the prompt card width;
- use a slightly smaller font than a tiny drill;
- left-align the text block for readability;
- keep the whole block centered inside the card;
- preserve generous line height;
- keep the current character obvious;
- never introduce a horizontal scrollbar.

Suggested desktop typography:

```text
font-size: clamp(1.65rem, 1.25rem + 1vw, 2.35rem)
line-height: 1.55
```

Suggested line width:

```text
max-width: 62ch–72ch
```

Do not make the prompt tiny just to keep it on one line.

## C. Passage Mode

Use the existing long-passage behavior when:

```text
text.length > 220
OR estimated_duration_seconds > 45
OR lesson.kind == "passage"
```

Preserve:

- multiline wrapped text;
- active-line visibility;
- passage auto-scroll;
- readable smaller typography;
- Coach flyout behavior;
- Save/Resume behavior.

Do not regress existing Passage Mode.

---

# 3. The most important rule: NEVER render practice text as one unbreakable horizontal strip

The browser must always be allowed to wrap the practice content.

At the prompt-text container level, ensure behavior equivalent to:

```css
.typingPromptText {
  width: 100%;
  max-width: 100%;
  white-space: pre-wrap;
  overflow-wrap: break-word;
  word-break: normal;
  overflow-x: hidden;
}
```

This is conceptual.

Use the actual project class names and preserve exact spaces in the lesson content.

Do **not** use:

```css
white-space: nowrap;
width: max-content;
min-width: max-content;
flex-wrap: nowrap;
overflow-x: auto;
```

for the normal typing prompt.

There must be no horizontal scrolling during typing.

---

# 4. Per-character rendering must still wrap

Cadence likely renders each character as an individual span so it can style:

```text
completed characters
current character
future characters
errors
spaces
```

Keep that functionality.

However, individual character spans must participate in normal inline text flow.

Preferred conceptual DOM:

```html
<div class="typingPromptText">
  <span class="char done">a</span>
  <span class="char done">;</span>
  <span class="char space"> </span>
  <span class="char current">l</span>
  <span class="char future">;</span>
  ...
</div>
```

Do not make each character a flex child of a `flex-wrap: nowrap` row.

Preferred:

```text
container = block
character spans = inline / inline-block only where needed
```

If a highlighted current character requires `inline-block`, that is fine, but the surrounding text must still wrap.

---

# 5. Spaces must wrap correctly

The screenshot displays spaces as visible middle dots, which is useful.

Preserve the visible-space visualization.

But make sure the representation does not prevent line wrapping.

If the current implementation converts a space to `·` inside a fixed inline element, ensure the browser still has legal line-break opportunities.

Recommended approach:

- preserve an actual wrapping opportunity at each space;
- visually display the space marker with CSS/pseudo-content or a span that can wrap after it.

Do not insert formatting characters into the actual lesson text used by the typing engine.

Visual formatting and source text must remain separate.

---

# 6. Optimal alignment

Do not center every wrapped line independently.

For medium and long content:

```text
prompt block → centered in card
text inside block → left aligned
```

This is easier for the eye to follow.

Short drills may remain centered.

---

# 7. Prompt card sizing

The card must use the available width without becoming an ultra-wide reading strip.

Desktop:

```text
width: min(100%, approximately 1100px)
```

or use the existing training column's full width.

Prompt text itself:

```text
max-width: approximately 70ch
margin-inline: auto
```

For medium drills, a prompt card may become modestly taller.

Do not force a fixed short height if it clips wrapped content.

Prefer:

```text
min-height
height: auto
```

with reasonable vertical padding.

The card should expand to fit the wrapped drill.

---

# 8. Do not let the Coach column create overflow

The screenshot has a large unused area to the right and a Training Console launcher area.

Inspect the actual parent layout.

The main training column must never calculate its content width from the text.

Use a robust grid/flex layout:

```text
main training area:
min-width: 0
width: 100%
```

This is especially important for CSS Grid/Flexbox children.

If the typing column is a grid/flex child, explicitly set:

```css
min-width: 0;
```

because the default `min-width: auto` can allow long inline content to force the column beyond its assigned width.

Apply the fix at the correct container level rather than hiding the problem with `body { overflow-x: hidden; }`.

It is acceptable to keep a final page-level overflow guard, but the inner layout itself must be correct.

---

# 9. Current character must remain visible

When text wraps, the active/current character must stay obvious.

For standard drills under 220 characters:

- render the whole wrapped drill;
- no scrolling should normally be necessary;
- the current character remains highlighted wherever it falls.

If the medium drill becomes taller than the available training viewport:

- keep the active line visible;
- scroll the prompt container vertically only;
- never scroll horizontally.

For Passage Mode, preserve existing active-line auto-scroll.

---

# 10. Avoid layout jump while typing

Character completion must not cause the remaining text to reflow unpredictably.

Do not remove completed characters from layout.

Instead keep all characters in place and change their styling:

```text
future
→ current
→ completed
```

The text geometry should remain stable throughout the round.

---

# 11. Responsive behavior

## Wide desktop

Target:

```text
prompt card width uses training column
text max ~70ch
2–4 lines for an 80-character practice where appropriate
```

Do not let the text stretch across a 1500–2000 px viewport.

## Laptop

Wrap naturally inside the card.

No horizontal overflow.

## Tablet

Reduce font size through `clamp()`.

Allow additional lines.

## Mobile / narrow viewport

Use approximately:

```text
font-size: 1.25rem–1.65rem
line-height: 1.5–1.65
```

Allow the prompt to wrap through as many lines as necessary.

Do not shrink below readable size simply to reduce line count.

No horizontal page scroll.

---

# 12. Keyboard and hands stay below the prompt

The new responsive prompt must not overlap:

- round progress;
- visual keyboard;
- human hands;
- hand instruction strip;
- Coach launcher.

Natural vertical order remains:

```text
module title / instruction
metrics
typing prompt
round progress
QWERTY keyboard
human hand overlay
hand guidance controls
```

When the prompt gains another line, allow the page/training area to become taller.

Do not absolutely position the keyboard at a hardcoded Y-coordinate under the previous one-line prompt.

Use normal document/layout flow.

---

# 13. The screenshot's 80-character drill acceptance target

Use a regression fixture approximately equivalent to the screenshot.

At a typical desktop training width, verify:

```text
text remains fully inside the prompt card
text wraps to multiple lines
no part leaves the viewport
no horizontal scrollbar appears
current target highlight remains visible
keyboard remains below the card
hands remain aligned to the keyboard
```

---

# 14. CSS implementation guidance

Use semantic classes or the current styling system.

Conceptual implementation:

```css
.trainingColumn {
  width: 100%;
  min-width: 0;
}

.typingPromptCard {
  width: 100%;
  min-width: 0;
  height: auto;
  overflow: hidden;
}

.typingPromptText {
  width: min(100%, 70ch);
  max-width: 100%;
  margin-inline: auto;

  white-space: pre-wrap;
  overflow-wrap: break-word;
  word-break: normal;

  line-height: 1.55;
}

.typingPromptText[data-size="short"] {
  text-align: center;
}

.typingPromptText[data-size="standard"],
.typingPromptText[data-size="passage"] {
  text-align: left;
}
```

Do not blindly copy names/values if the current project architecture uses different tokens.

Preserve Cadence theme variables.

---

# 15. Add a prompt-layout utility instead of scattered length checks

Create one centralized function.

Conceptually:

```ts
type PromptLayoutMode = "short" | "standard" | "passage";

function getPromptLayoutMode(
  textLength: number,
  lessonKind?: string,
  estimatedDurationSeconds?: number
): PromptLayoutMode
```

Suggested rules:

```ts
if (lessonKind === "passage" ||
    textLength > 220 ||
    estimatedDurationSeconds > 45) {
  return "passage";
}

if (textLength > 45) {
  return "standard";
}

return "short";
```

Components and CSS should use this shared result.

Do not implement different thresholds independently in multiple components.

---

# 16. Accessibility

The visual wrapping must not alter the lesson text announced to assistive technology.

Requirements:

- preserve source character order;
- preserve actual spaces semantically;
- current-character styling does not reorder DOM content;
- no horizontal-scroll-only interaction;
- zoom to 200% must still wrap;
- large-text accessibility setting takes precedence over automatic typography;
- if larger font creates more lines, accept the added height.

Do not reduce the user-selected font size merely to force content into the old card.

---

# 17. Automated tests

Add at least:

1. short prompt receives `short` layout mode;
2. 80-character drill receives `standard` layout mode;
3. >220-character text receives `passage` mode;
4. passage-kind lesson receives passage mode regardless of length;
5. standard prompt does not use `white-space: nowrap`;
6. visual character order is unchanged by wrapping;
7. completed characters remain in the DOM/layout;
8. current-character highlight survives wrapping;
9. visible-space markers preserve legal line-break opportunities;
10. prompt card height is not hard-fixed in a way that clips wrapped text;
11. training grid/flex child has `min-width: 0`;
12. standard prompt has no horizontal scrolling;
13. responsive narrow layout has no horizontal page overflow;
14. 200% zoom remains usable without horizontal prompt overflow;
15. keyboard remains after/below prompt in document layout;
16. hand overlay alignment is unchanged by prompt height;
17. Coach open/closed state does not cause prompt overflow;
18. generated 80-character drill fits inside the training card;
19. active round state/char index is unchanged by layout-mode calculation;
20. wrapping has no effect on typing scoring.

If browser E2E infrastructure is available, add viewport checks for:

```text
1920×1080
1366×768
1024×768
768×1024
390×844
```

At each viewport assert:

```text
document.documentElement.scrollWidth
<= document.documentElement.clientWidth
```

within normal rounding tolerance.

---

# 18. Manual production acceptance

After deploying, authenticate into the existing user and verify:

## Standard 80-character round

- prompt wraps inside card;
- no right-side escape;
- no page horizontal scroll;
- current character remains highlighted;
- WPM/accuracy/cadence still work;
- keyboard remains proper QWERTY;
- human hands remain aligned.

## F2 generated practice

Generate a medium-length F2/custom practice.

Verify the generated text uses the same responsive layout.

The fix must apply to:

```text
built-in lessons
F2 reshuffles
custom Coach practice
weak-key practice
cached AI content
fallback content
```

not just one built-in fixture.

## Coach open

Open F1.

Verify the narrower available training space still causes clean wrapping rather than overflow.

Close Coach.

Verify layout expands naturally with no state reset.

## Narrow screen

Use responsive device emulation.

Verify:

```text
no horizontal page scrollbar
prompt wraps
keyboard/hand area remains usable
```

---

# 19. Do not regress REV12

Preserve all verified REV12 behavior, including:

- QWERTY physical order;
- F/J home bumps;
- human hand SVG overlay;
- Shift + { hide-hands shortcut currently implemented;
- Show hands;
- module/placement reset behavior;
- Login & Passkeys;
- max two passkeys;
- last-passkey protection;
- F1/F2 behavior;
- generated-content validation;
- checkpoint synchronization;
- constrained fallback;
- dark public login;
- strict CSP;
- D1 migration history;
- 64-module curriculum;
- current user progress.

Do not modify production learner progress while testing generated content.

---

# 20. Completion report

Report:

## Root cause

State exactly why the text was escaping the screen, for example:

```text
PromptLine used nowrap
character row used flex without wrapping
grid child lacked min-width: 0
fixed card height/width
```

Report the actual inspected cause, not a guess.

## Files changed

List frontend/style/test files.

## Tests

Report:

```text
frontend unit tests
backend tests if touched
typecheck
production build
viewport/E2E checks
```

## Production verification

Confirm that an ~80-character round:

```text
wraps
does not overflow horizontally
keeps current character visible
does not disturb QWERTY/hands
```

Do not claim verification if not actually observed.

---

# 21. Definition of Done

REV13 is complete only when:

- no typing prompt can extend beyond its card horizontally;
- no typing prompt can extend beyond the browser viewport horizontally;
- short drills remain large and centered;
- medium drills wrap into readable multiline text;
- medium wrapped text is left-aligned inside a centered reading block;
- long passages still use Passage Mode;
- the current character remains clearly highlighted;
- completed/future characters stay spatially stable;
- no horizontal scrollbar is introduced;
- prompt card height grows naturally;
- keyboard and hands move down in normal flow rather than being overlapped;
- generated/custom/fallback drills use the same responsive renderer;
- Coach open/close does not create overflow;
- mobile/tablet/desktop layouts all remain readable;
- QWERTY keyboard, human hands, passkeys, F1/F2, Cloudflare hosting, D1 progress, and authentication behavior are not regressed.


---

# 22. Shortcut change — `Space + {` toggles human hands

REV13 also changes the hand-visibility shortcut introduced by REV12.

## 22.1 Replace the old shortcut

Remove:

```text
Shift + {
```

as the hand hide/show shortcut.

Replace it with:

```text
Space + {
```

The same shortcut is a **toggle**:

```text
hands visible
→ Space + {
→ hide hands

hands hidden
→ Space + {
→ show hands
```

Do not assign separate shortcuts for Hide and Show.

The visible control may continue to say:

```text
Hide hands
```

or:

```text
Show hands
```

depending on current state, but its shortcut hint must always show:

```text
Space + {
```

## 22.2 Physical-key interpretation

On a standard US QWERTY keyboard, `{` is typed with:

```text
Shift + [
```

Therefore the intended physical chord is:

```text
hold Space
+
press Shift + [
```

The app should display the learner-facing shortcut as:

```text
Space + {
```

not as the lower-level physical key sequence.

## 22.3 Do not let the shortcut affect typing metrics

This shortcut must be handled by the centralized training shortcut layer **before it can be counted as lesson input**.

When Cadence recognizes the exact `Space + {` chord:

- toggle the hands;
- call `preventDefault()` as appropriate;
- do not advance the lesson;
- do not count Space as a typing attempt;
- do not count `{` as a typing attempt;
- do not change WPM;
- do not change accuracy;
- do not change cadence;
- do not change the current character index;
- do not insert characters into Coach/freeform text fields.

The shortcut is available only on the authenticated training screen where hand guidance exists.

Do not install it on:

```text
public login
passkey registration
access-PIN screen
main menu
Progress
Login & Passkeys
normal text-entry forms
```

## 22.4 Chord handling must not make normal Space typing laggy

Because Space is also a normal lesson character, do **not** implement this by globally delaying every Space keystroke by a noticeable amount.

Use the existing centralized shortcut/input architecture to recognize the chord with minimal impact on normal typing.

The coding agent must inspect the current event-dispatch order and implement the safest approach so that:

```text
ordinary Space
→ remains immediate normal typing input

Space + {
→ becomes hand-toggle command only
```

If a transient pressed-key state is used, clear it on:

```text
keyup
blur
visibilitychange
route change
```

so a stuck Space state cannot accidentally trigger the shortcut later.

## 22.5 Shortcut registry

If Cadence has a centralized shortcut registry, update it there.

Conceptually:

```ts
handsToggle: "Space+{"
```

Remove the old:

```ts
handsToggle: "Shift+{"
```

Do not leave both shortcuts active.

Shortcut collision validation must include the new chord.

## 22.6 Accessibility

The Hide/Show Hands button must expose:

```html
aria-keyshortcuts="Space+{"
```

or the standards-compliant equivalent supported by the current implementation.

The visible tooltip/focus hint should read:

```text
Hide hands · Space + {
```

or:

```text
Show hands · Space + {
```

depending on state.

Mouse, touch, Tab + Enter/Space, and the shortcut must invoke the same underlying toggle action.

## 22.7 Tests

Add/update tests for:

1. old `Shift + {` no longer toggles hands;
2. `Space + {` hides visible hands;
3. pressing `Space + {` again shows hidden hands;
4. the shortcut calls the same action as the visible Hide/Show Hands button;
5. the shortcut does not increment typing attempts;
6. the shortcut does not change accuracy;
7. the shortcut does not change WPM;
8. the shortcut does not change cadence;
9. the shortcut does not change the current character index;
10. an ordinary Space keypress still types immediately;
11. the shortcut is inactive outside the training screen;
12. pressed-key state clears on blur/visibility change;
13. `aria-keyshortcuts` and tooltip/focus text show `Space + {`;
14. the centralized shortcut collision validator accepts the new mapping;
15. there is no remaining production binding for `Shift + {`.

## 22.8 Manual production acceptance

After deployment:

```text
start training
→ hands visible
→ press Space + {
→ hands hide
→ current character and metrics do not change
→ press Space + {
→ hands show
→ current character and metrics still do not change
```

Then verify:

```text
press normal Space while typing
→ Space is entered normally with no noticeable delay
```

Also verify:

```text
Shift + {
→ no longer controls the hand overlay
```

---

# 23. Updated REV13 Definition of Done addition

In addition to all responsive-prompt requirements above, REV13 is not complete until:

- `Space + {` is the only hand-visibility keyboard shortcut;
- the shortcut toggles both Hide Hands and Show Hands;
- the old `Shift + {` binding is removed;
- the hand-toggle chord never changes typing metrics or lesson position;
- ordinary Space typing remains immediate;
- the visible button/tooltip/accessibility metadata all show `Space + {`.
