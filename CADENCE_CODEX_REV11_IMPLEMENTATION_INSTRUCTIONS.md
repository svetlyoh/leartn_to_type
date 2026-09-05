# Cadence — Codex Implementation Instructions
## REV11 — Persistent User Progress, Themed Login, Round Hand Reset, Player Detail, Functional Progress/Weak-Key/Settings, and Coach “Build Practice” Fix

**Date:** September 2026  
**Project:** Learn_to_Type / Cadence  
**Purpose:** implementation instructions for the coding agent.  
**Baseline files read before writing this revision:**
- `CURRENT_IMPLEMENTATION.md`
- `LEARN_TO_TYPE_CODEX_BUILD_SPEC_REV9_SIMPLIFIED_USER_ACCESS(1).md`

---

# 0. Mandate and precedence

Implement this revision **on top of the current deployed implementation**. Inspect the repository and production schema before editing.

This revision is additive and targeted. It does **not** authorize a rewrite of the authentication, curriculum, MiniMax, D1, or typing engine.

Use this precedence when requirements conflict:

1. This REV11 document for the features and fixes listed here.
2. The current implementation actually present in the repository and D1.
3. REV9 learner-access rules.
4. Earlier non-conflicting requirements for typing, progress, MiniMax, hand guidance, shortcuts, save/resume, and accessibility.

Preserve the current production baseline:

- Worker: `leartn-to-type`
- D1 database: existing `learn-to-type`, binding `DB`
- React + TypeScript + Vite frontend
- FastAPI on Cloudflare Python Workers
- WebAuthn/passkey identity
- versioned Cadence access PIN
- 48-hour server-side session maximum
- server-side opaque sessions
- MiniMax only through the backend
- curriculum version `2026.10`
- exactly 64 current modules and 64 built-in seed texts
- existing progress/mastery migration history
- existing rate-limit bindings, secrets, Worker name, and production domain
- no normal learner/profile PIN
- no Admin/Test Mode requirement in the normal learner flow

**Do not downgrade the curriculum to an older revision.**  
**Do not create a second D1 database.**  
**Do not create a second user/profile system.**  
**Do not reintroduce a learner/profile PIN.**

Before coding, inspect:

```text
wrangler config
current D1 migrations
current user/account/profile tables
current progress/session/mastery tables
current auth/session routes
current Main Menu / Player Ready / Training screen
current F1 Coach/Training Console implementation
current AI lesson-generation endpoint
current IndexedDB persistence
current settings/preferences implementation
```

Run the current tests before modifications and record the baseline.

---

# 1. Server persistence is authoritative for every user

The current app already associates each passkey account with its player profile and progress. Strengthen that design so a returning user is restored from the **server**, not from a temporary login-session-only name or browser-only state.

## 1.1 Required persistent player information

For each authenticated passkey account, persist and restore, using the existing appropriate tables where possible:

```text
stable user/account ID
display/player name
selected character_id
age, if collected
school_status, if collected
grade_level, if collected
onboarding completion
current curriculum phase
current module ID
current lesson/content ID
current round index
resumable character position when a checkpoint exists
module mastery
key mastery
weak-key evidence
recent completed-session metrics
best valid metrics
settings/preferences
theme
sound enabled/disabled
accessibility preferences
last meaningful training timestamp
```

Do not create duplicate fields if equivalent fields already exist.

## 1.2 Player name must persist across logins

The current implementation must no longer behave as though the player name is merely for the current login session.

Required behavior:

```text
first authorized use
→ collect/save player name once

later login on same or another device
→ passkey identifies account
→ server returns saved player name
→ do not ask for the name again
```

If the current blank-name behavior saves `MCP`, preserve backward compatibility, but save the resulting value persistently and do not re-prompt on each login.

`Edit name` remains available and must update the server record without changing:

- account identity,
- passkeys,
- selected character,
- progress,
- mastery,
- history.

## 1.3 Resume latest progress

After passkey authentication and access-PIN approval:

```text
load account
→ load player profile
→ load authoritative server progress
→ reconcile with newer valid local IndexedDB checkpoint if one exists
→ show Main Menu / Player Ready with latest known progress
```

`Start / Continue` must use the latest resumable state.

If there is an in-progress saved round, show a concise status such as:

```text
Continue · Module 7 · Round 2
```

or:

```text
Resume saved round · 63% complete
```

If no in-progress round exists, continue from the current module/next appropriate round.

## 1.4 Server-first cross-device behavior

IndexedDB remains a resilience layer, not the only history store.

At minimum, server writes must occur:

- at completed round,
- at completed session,
- after explicit Save Session,
- after Exit to Menu save,
- after module advancement,
- after name/character/settings changes,
- after onboarding/profile changes.

Do not send raw per-keystroke streams to D1. Preserve the current aggregate/checkpoint approach.

On login from a different device, the user must still see:

- their name,
- character,
- current module,
- module mastery,
- recent metrics,
- latest server checkpoint/progress.

---

# 2. Public login / account screen must use the Cadence app theme

Redesign the public landing/login presentation so it visually belongs to the same application.

## 2.1 Required layout

Use the same dark design tokens as the main app.

Default composition:

```text
                    CADENCE

        Learn to type. Build your rhythm.

          [ Sign in with passkey ]

               New here?
            [ Create account ]


------------------------------------------------
About · Produced by Noverel · September 2026
```

Requirements:

- black/dark background by default;
- `CADENCE` clearly visible near the top;
- no unrelated white authentication card unless it is intentionally styled as a dark Cadence surface;
- use the same typography, border radii, focus treatment, muted text, and accent system as the app;
- passkey remains the only normal learner login;
- access-PIN version flow remains unchanged;
- do not expose player progress publicly.

## 2.2 About footer

At the bottom of the public/login screen include:

```text
About · Produced by Noverel · September 2026
```

`About` should be a subtle accessible button/link.

Opening it may show a small modal/sheet:

```text
CADENCE
A focused touch-typing trainer built around technique, rhythm, and progress.

Produced by Noverel
September 2026
```

Keep it small. Do not turn it into a marketing page.

---

# 3. Player/profile detail — include school and training level

The prior specification already includes school status and grade in onboarding. Surface useful player details after login.

## 3.1 Player Ready / profile summary

When the data exists, show a compact profile summary such as:

```text
Julian
Freshman · 9
Stride · Steady rhythm

Foundations
Module 7 of 64
```

If school status is not student or was skipped, omit the grade line rather than displaying an awkward placeholder.

Do not show age prominently on the normal menu.

## 3.2 “Level” means training level, not a character power level

Do not invent RPG stats, rarity, bonuses, or a character economy.

Use the current curriculum to derive a learner-facing training level, for example:

```text
Foundations · Module 7 / 64
Fluency Tools · Module 21 / 64
Reading & American Literature · Module 39 / 64
Modern Fluency · Module 53 / 64
```

This is the learner's progress level.

The character remains cosmetic.

---

# 4. Stride / Flux / Vector / Nova tooltips

Preserve the four existing characters exactly:

```text
Stride — Steady rhythm
Flux — Quick recovery
Vector — Clean precision
Nova — Calm focus
```

Preserve their existing names, artwork, cards, and visual style.

Add hover **and keyboard-focus** tooltips/help text explaining what each concept means.

Recommended copy:

### Stride — Steady rhythm

```text
A steady, balanced training style built around smooth, repeatable timing.
Character style only — it does not change your curriculum or scoring.
```

### Flux — Quick recovery

```text
Represents resetting quickly after a mistake and finding your rhythm again.
Character style only — it does not change your curriculum or scoring.
```

### Vector — Clean precision

```text
Represents accurate finger placement and controlled movement before speed.
Character style only — it does not change your curriculum or scoring.
```

### Nova — Calm focus

```text
Represents relaxed concentration and staying composed through longer practice.
Character style only — it does not change your curriculum or scoring.
```

Requirements:

- tooltip works with mouse hover;
- tooltip/help is also available on keyboard focus;
- tooltip is screen-reader accessible;
- tooltip must not imply stat boosts or different lesson difficulty.

---

# 5. Hand/finger guide — new round reset behavior

This section intentionally changes the default visibility behavior from older “only occasionally show hands” wording.

The existing finger-map and actual hand/finger movement requirements remain in force.

## 5.1 Default: show hand placement at the start of every new round

At the beginning of **every new training round**, before active typing begins, show the current hand-placement guide by default.

The guide should visually remind the learner:

- where both hands rest;
- which fingers are currently relevant;
- F/J home anchors;
- any movement being introduced for that round.

Do not make this a long tutorial. A concise 1–3 second placement/reset presentation is sufficient, with a clear way to begin immediately.

## 5.2 Per-round subtle Hide control

While the hand-placement guide is visible, include a small secondary control:

```text
Hide hands
```

or:

```text
Hide guide
```

The control should be:

- visible but subtle;
- a real accessible button;
- not visually dominant;
- usable by mouse, touch, Tab, and Enter/Space.

**Hiding applies only to the current round.**

Do not make `Hide hands` suppress the guide forever.

## 5.3 Every new round resets the guide to visible

Required state model:

```text
round starts
→ guide visible

user clicks Hide hands
→ guide hidden for this round

next round starts
→ guide visible again
```

This is intentional repetition.

## 5.4 Newly added fingers/keys force the guide to reappear

When entering a round/module that introduces additional keyboard reach or a newly used finger/key:

```text
new movement detected
→ reset hand-guide visibility
→ show the hands again
→ play the relevant movement introduction
```

Even if the learner hid the hands in the previous round, the new-key/new-finger round must show the guide again.

The learner may hide it again for that new round.

## 5.5 Any true hand-position reset shows the animation again

Treat these as guide reset events:

- new round,
- new module,
- newly introduced key,
- newly introduced finger/reach,
- explicit tutorial replay,
- explicit training reset,
- return to home-row placement after a lesson mode that changed hand behavior.

Every reset must show the relevant hand-placement animation/instruction.

## 5.6 New-key movement

Preserve the existing canonical finger map.

Examples:

```text
R → left index: F → R → F
U → right index: J → U → J
W → left ring: S → W → S
```

When new keys are introduced:

1. show home position;
2. highlight the owning finger;
3. animate from home to target;
4. pause briefly;
5. return home;
6. let the learner begin.

## 5.7 Repeated errors and manual help

Preserve:

```text
repeated misses
→ subtle target hint
→ finger animation when threshold is met
```

and:

```text
Show finger / Show me
→ replay guide
```

Do not auto-open Coach for a mistake.

## 5.8 Reduce Motion

Reduce Motion does not remove teaching information.

With Reduce Motion enabled:

```text
show hand/finger
+ highlight home key
+ highlight target
+ directional indicator
```

instead of a large animated reach.

## 5.9 Accessibility override

If the existing Accessibility screen contains a persistent `hand animations off` setting, do not silently delete it.

However, distinguish:

```text
Hide hands
= current round only

Reduce Motion
= persistent motion accessibility preference

Hand guidance disabled
= persistent explicit accessibility choice, if already supported
```

If a user explicitly disables hand guidance in Accessibility, honor that persistent choice. Otherwise the new default is **visible at the start of each round**.

---

# 6. Progress button must be fully functional

The `Progress` action must open a real progress view, not a placeholder.

Use authoritative server data.

## 6.1 Required progress content

At minimum show:

### Current position

```text
Phase
Current module name
Module number / 64
Module mastery %
Next recommended focus
```

### Recent performance

Use valid-sample rules.

Show:

```text
Last session WPM
Last session accuracy
Last session cadence
Recent average WPM
Recent average accuracy
Best valid WPM
Total completed sessions or total practice time
```

If cadence does not have enough samples, show:

```text
Cadence — collecting
```

Do not show a misleading zero.

### Key development

Show:

```text
Top 3 current weak keys
Top 3 strongest/most stable keys
```

Use server mastery/error/reaction evidence.

### Recent history

Show a compact list for approximately the last 5–10 completed sessions:

```text
date/time
module
WPM
accuracy
cadence
```

Keep the screen clean. A giant analytics dashboard is not required.

## 6.2 Progress refresh

After a completed round/session/module advancement:

- refresh relevant progress data;
- do not require a full page reload;
- preserve the server as the authority.

---

# 7. Practice Weak Keys must work

The Main Menu/Player Menu `Practice weak keys` action must always produce a meaningful result.

It must not be a dead button.

## 7.1 Selection logic

Use current server key-mastery data.

Choose approximately 1–3 currently unlocked weak keys using a combination of:

```text
low mastery
recent errors
slow reaction time
recent repeated misses
recency balancing
```

Never select a locked/unlearned key.

## 7.2 Practice generation

When weak keys exist:

```text
Practice weak keys
→ derive focus keys
→ build constrained drill
→ show brief preview/description
→ Start practice
```

Prefer deterministic/local/built-in generation first where appropriate.

MiniMax may be used through the existing backend generation path, but the feature must still work if MiniMax is unavailable.

## 7.3 No weak-key evidence yet

Do not do nothing.

If no reliable weak keys exist, show:

```text
I don't have a clear weak-key pattern yet.
Let's run a short diagnostic round.
```

Then offer:

```text
[ Start diagnostic ]
```

or load a balanced current-module drill.

## 7.4 Completion

A completed weak-key practice round must update the normal aggregate evidence/mastery rules just like other valid normal training, unless the current product intentionally marks a specific drill as diagnostic-only.

---

# 8. Settings — themes

Add 2–3 calm visual themes.

The default remains black/dark.

Recommended initial set:

```text
Midnight      — default black/dark Cadence theme
Soft Slate    — muted blue/slate dark theme
Soft Plum     — muted plum/charcoal dark theme
```

Names may be adjusted to match the current product voice.

## 8.1 Theme requirements

Each theme must define the same semantic tokens:

```text
background
surface
surface-raised
text
muted-text
border
accent
accent-soft
focus-ring
success
warning/subtle-error
```

Do not scatter raw theme colors across components.

Themes must preserve readable contrast and visible focus states.

## 8.2 Theme persistence

Theme selection must:

```text
apply immediately
save locally for instant startup
save server-side for the authenticated user
restore on next login/device
```

When server and local values differ after login, the authenticated server preference is authoritative unless the local preference is newer and pending sync.

The public login screen should use the default Midnight theme unless there is a safe anonymous/global preference already supported.

---

# 9. Settings — soft typing sounds

Add a working Sound setting.

Recommended control:

```text
Typing sounds   [ On / Off ]
```

Default may preserve the current product default. If there is no current behavior, use a low-volume, non-intrusive default.

## 9.1 Sound design

Use a small bundled/local sound set or lightweight Web Audio.

The typing sound should be:

- soft;
- short;
- low volume;
- non-metallic;
- not arcade-like;
- not a typewriter gunshot;
- not a negative buzzer;
- consistent with the dark/soft Cadence theme.

A subtle difference for Space is acceptable.

Do not play harsh separate “wrong” sounds.

Do not make correctness depend on sound.

Do not use remote audio assets.

## 9.2 Sound behavior

When enabled:

- printable typing attempts may make the selected soft key sound;
- shortcuts such as F1/F2/F3 should not make the normal typing sound;
- menu clicks may remain silent or use a separate very soft UI tick if one already exists.

When disabled:

```text
no typing sound
```

The setting must persist server-side and locally like other user preferences.

Respect browser autoplay rules; initialize audio only after user interaction.

---

# 10. Inspect and fix F1 → Something Else → Build Practice

There is a current user-visible defect:

```text
F1
→ enter/use Something else
→ type a request for text/practice
→ Build practice
→ nothing visibly happens
```

Treat this as a required bug fix, not a future enhancement.

## 10.1 Reproduce before changing code

Codex must reproduce the current failure in the browser/test environment.

Inspect the complete action chain:

```text
F1 shortcut
→ Coach/Training Console open
→ Something else/custom request state
→ text input value
→ Build practice button handler
→ request classification
→ frontend API client
→ backend AI/training route
→ MiniMax/cache/fallback result
→ validator
→ returned generated lesson
→ staged preview state
→ Start practice action
→ typing engine lesson replacement/start
```

Do not assume the failure is the MiniMax provider.

Find the exact broken link.

## 10.2 Required behavior for text requests

Examples that must work:

```text
Give me text to type.
Give me something about running.
Build me a one-minute practice.
Give me a longer paragraph.
Practice R and T.
Make something less repetitive.
```

When the request is a text/practice-generation intent:

1. classify it as a training-content request;
2. derive the learner's current capability envelope from the server;
3. call the existing lesson/passage generation path;
4. validate against unlocked characters/curriculum;
5. use cache/fallback if MiniMax is unavailable;
6. return a generated drill/passage;
7. show visible success state/preview;
8. require confirmation before replacing active unfinished work;
9. start the generated practice when the learner chooses `Start practice` / `Start passage`.

The UI must never silently stop after the request.

## 10.3 Build Practice button

`Build practice` must:

- be enabled when there is a valid non-empty request;
- invoke the same underlying action regardless of mouse or keyboard activation;
- show a loading state;
- prevent duplicate submissions while in flight;
- show an actionable error state if the request fails;
- on success, present generated practice metadata and next action.

Example:

```text
Building practice…
```

then:

```text
Ready.

1-minute running passage
Focus: current unlocked keys
Source: AI/cache/built-in internally

[ Start practice ]
[ Try another ]
[ Keep current round ]
```

Do not expose provider internals to the learner unless already part of admin diagnostics.

## 10.4 “Something else” must not be a dead submenu

If `Something else…` reveals a freeform input, submitting that input must route into one of these supported intents:

```text
generate practice/text
explain mistake/technique
show finger
change difficulty
weak-key practice
reshuffle
supported Coach response
```

If the request is unrelated to typing/training, respond briefly and keep the user in Cadence.

Never accept input and then provide no visible result.

## 10.5 Active-round protection

If the learner is midway through a round and asks for new text:

```text
generate/stage new practice
→ do not discard current active round automatically
→ show confirmation
```

Example:

```text
Start this practice?
Your current round is still in progress.

[ Save & start new practice ]
[ Keep current round ]
```

Use the existing checkpoint semantics.

## 10.6 Freeform response contract

Every successful Coach request should end with a clear next action.

For generated practice:

```text
Start practice
Try another
Keep current round
```

For explanations:

```text
Practice that key
Show finger
Back to training
```

No conversational dead ends.

---

# 11. Main Menu actions must not be placeholders

Audit the authenticated menu.

At minimum, these actions must have real behavior:

```text
Start / Continue
Practice weak keys
Progress
Settings
Select character
How training works
Accessibility
Exit
```

If a button is present, it must either:

- navigate to a functional screen,
- perform a functional action,
- or clearly explain why it is temporarily unavailable.

Do not leave clickable UI that silently does nothing.

---

# 12. Suggested persistence/API audit

Reuse existing routes where they already provide the required data.

The coding agent may add a small endpoint only if the current APIs cannot cleanly support the UI.

Preferred existing sources:

```text
/auth/me or /me
/progress
/module-progress
/key-mastery
/sessions
/settings/profile update
AI lesson generation
```

If a compact dashboard endpoint is useful, it may return:

```json
{
  "profile": {
    "display_name": "Julian",
    "school_status": "student",
    "grade_level": "9",
    "character_id": "runner_01"
  },
  "curriculum": {
    "phase": "Foundations",
    "module_id": "module_07",
    "module_index": 7,
    "module_count": 64,
    "mastery_percent": 43
  },
  "recent": {
    "wpm": 31.2,
    "accuracy": 96.4,
    "cadence": 78
  },
  "weak_keys": ["r", "t"],
  "resume": {
    "available": true,
    "round_index": 2,
    "char_index": 84
  }
}
```

This is conceptual only. Do not duplicate data models just to match this example.

All learner data must be resolved from the authenticated account/session. Never trust a browser-supplied user ID for ownership.

---

# 13. D1 migration rules

Do not edit already-applied migrations.

First inspect the real schema.

Only create a forward migration if fields needed by this revision are genuinely absent.

Possible additions, only if needed, include:

```text
school_status
grade_level
theme_id
sound_enabled
last_training_at
```

Prefer existing JSON preference columns for theme/sound if that is already the project's pattern.

Do not duplicate:

```text
display_name
character_id
progress
module
mastery
```

if equivalent fields already exist.

Any migration must preserve all current production users and progress.

---

# 14. Frontend implementation guidance

Prefer extending the existing architecture.

Likely areas to inspect:

```text
public landing/auth components
Main Menu / Player Ready
profile/player summary
character catalog/cards
Progress screen
Settings screen
Training screen
HandGuide / HandsOverlay / finger map
Coach/Training Console
AI request client
active session store
user preferences store/context
```

Do not create a second state-management framework just for this revision.

## 14.1 Hand reset state

Use an explicit round-scoped state such as:

```ts
type HandGuideRoundState = {
  roundId: string;
  visible: boolean;
  resetReason:
    | "round_start"
    | "module_start"
    | "new_key"
    | "new_finger"
    | "manual"
    | "training_reset";
};
```

On round ID change:

```text
visible = true
```

unless the user has an explicit persistent accessibility setting disabling hand guidance.

Do not persist the per-round `Hide hands` state across rounds.

---

# 15. Automated tests required

Add/update tests. Do not mark the revision complete without them.

## 15.1 Persistence/login

1. player name persists in D1/server profile;
2. returning passkey user receives the saved name;
3. returning user is not asked to create a name again;
4. Edit name preserves character/progress/history;
5. latest server progress loads after login;
6. cross-device-equivalent login can restore server progress without IndexedDB;
7. server checkpoint resumes the correct module/round/char index;
8. public landing uses Cadence dark theme;
9. public landing shows `CADENCE`;
10. footer shows `About · Produced by Noverel · September 2026`;
11. About control is keyboard accessible.

## 15.2 Player/character detail

12. saved school status/grade appears when applicable;
13. grade is omitted when not applicable/skipped;
14. current training phase/module is displayed;
15. Stride tooltip explains Steady rhythm;
16. Flux tooltip explains Quick recovery;
17. Vector tooltip explains Clean precision;
18. Nova tooltip explains Calm focus;
19. character tooltips work on keyboard focus;
20. character remains cosmetic and does not change curriculum/difficulty.

## 15.3 Hand reset

21. hand placement appears at the start of a new round by default;
22. Hide hands hides it for the current round;
23. next round shows hands again;
24. new key introduction forces guide visible;
25. new finger/reach introduction forces guide visible;
26. true training reset shows the guide again;
27. R maps to left index;
28. U maps to right index;
29. Reduce Motion preserves instructional indication;
30. explicit persistent accessibility disable, if supported, overrides automatic round display;
31. hand overlay does not steal typing focus.

## 15.4 Progress

32. Progress button opens a functional progress screen;
33. current module number out of 64 is correct;
34. mastery percent comes from authoritative data;
35. last-session WPM/accuracy/cadence render correctly;
36. cadence with insufficient sample displays `collecting`, not zero;
37. weak keys render from mastery evidence;
38. recent history loads and updates after a completed session.

## 15.5 Weak-key practice

39. Practice weak keys produces a drill when weak keys exist;
40. weak-key drill includes only unlocked keys;
41. focus keys correspond to server evidence;
42. MiniMax outage still yields fallback practice;
43. no weak-key evidence produces a diagnostic/balanced option instead of a no-op;
44. completing valid weak-key practice updates normal mastery evidence.

## 15.6 Themes/sounds

45. default theme is Midnight/black;
46. each configured theme applies semantic tokens correctly;
47. theme persists after reload/login;
48. sound toggle persists;
49. sound off produces no typing audio;
50. sound on produces only the approved soft typing sound;
51. F1/F2/function-key shortcuts do not trigger typing audio;
52. audio initialization respects browser user-interaction requirements.

## 15.7 F1 / Build Practice regression

53. F1 opens Coach/Training Console;
54. `Something else…` reveals a working input;
55. entering `Give me text to type` and pressing `Build practice` triggers the generation flow;
56. `Give me something about running` produces a generated/cached/fallback practice;
57. Build practice shows a loading state;
58. duplicate clicks do not create duplicate requests;
59. successful generation produces a visible preview/confirmation;
60. Start practice loads the returned validated text into the typing engine;
61. active unfinished round is not silently discarded;
62. AI/provider failure uses cache/fallback or shows a visible error;
63. no successful request ends in a silent no-op;
64. mouse activation and keyboard activation use the same action handler.

---

# 16. Manual acceptance flows

Codex must manually verify these flows in addition to automated tests.

## Flow A — returning user

```text
Sign in with passkey
→ access version already accepted
→ dark Cadence menu
→ saved player name visible
→ school/grade shown if applicable
→ character visible
→ latest module/progress visible
→ Start / Continue resumes correctly
```

## Flow B — new round hand guide

```text
start round
→ hands visible
→ Hide hands
→ hands hidden
→ complete/start next round
→ hands visible again
```

## Flow C — new key

```text
enter round that introduces R
→ hands shown even if prior round was hidden
→ left index F → R → F animation
→ learner may Hide hands for this round
```

## Flow D — weak keys

```text
Player Menu
→ Practice weak keys
→ focus keys selected
→ valid drill preview
→ Start
→ training works
```

## Flow E — Progress

```text
Player Menu
→ Progress
→ current module / 64
→ mastery
→ recent WPM/accuracy/cadence
→ weak keys
→ recent sessions
```

## Flow F — F1 custom practice bug

```text
Training
→ F1
→ Something else
→ type: Give me something about running for one minute
→ Build practice
→ visible loading state
→ validated practice is returned
→ preview appears
→ Start practice
→ generated passage loads
```

There must be no silent no-op at any point.

---

# 17. Implementation order

Do the work in this order:

1. inspect repo, schema, current UI, and reproduce the F1/Build Practice defect;
2. run baseline tests;
3. fix server persistence for name/profile/latest progress without changing account identity;
4. update login/landing visual theme and About footer;
5. surface school/grade + training level and add character tooltips;
6. implement per-round hand-guide reset/show/hide behavior;
7. make Progress functional;
8. make Practice weak keys functional;
9. add theme settings and persistence;
10. add soft typing-sound toggle and persistence;
11. repair the complete F1/Something Else/Build Practice flow;
12. add all relevant tests;
13. run full frontend/backend/typecheck/build tests;
14. apply any required forward D1 migration only after validation;
15. deploy only after tests pass;
16. production smoke-test the flows above.

Keep the app runnable after each step.

---

# 18. Do not regress these existing behaviors

Do not break:

- passkey registration/login;
- versioned access PIN;
- 48-hour session expiry;
- normal learner access without profile PIN/admin;
- character persistence;
- 64-module curriculum;
- current D1 progress history;
- module and key mastery;
- Save Session;
- IndexedDB local resilience;
- Exit/Resume;
- MiniMax backend-only secret boundary;
- AI validation and deterministic fallback;
- typing keystroke path staying local/deterministic;
- F1/F2/Shift+Enter shortcut rules already implemented;
- accessibility/reduced motion;
- security headers;
- same-origin/ownership checks.

---

# 19. Completion report required from Codex

At the end, report:

## Files changed

Group by:

```text
frontend
backend
migrations
tests
docs/config
```

## Defect diagnosis

For the F1 → Something Else → Build Practice issue, state:

```text
exact root cause
files involved
what was changed
test that proves the regression is fixed
```

Do not just say “fixed.”

## Persistence verification

State exactly where these are stored:

```text
display name
school status
grade
character
theme
sound setting
current module/progress
latest checkpoint
session history
key mastery
```

## Commands run

Include exact commands and pass/fail results for:

```text
backend tests
frontend tests
typecheck
production build
E2E/manual smoke checks
D1 migration list/apply, if any
deployment, if performed
```

## Production verification

If deployed, verify:

```text
login theme
About/Noverel footer
returning name/progress
Progress screen
Practice weak keys
round hand reset/hide behavior
F1 custom Build Practice
themes
sound toggle
```

Do not claim production verification for anything not actually tested.

---

# 20. Definition of Done

This revision is complete only when:

- every passkey user has durable server-backed name/profile/progress;
- returning users are recognized by name and resume latest progress;
- login uses the Cadence dark visual language with `CADENCE` at the top;
- the login footer states `About · Produced by Noverel · September 2026`;
- school/grade is stored and surfaced when applicable;
- the learner's training level/module is visible;
- Stride/Flux/Vector/Nova have clear hover/focus explanations;
- hand placement appears by default at every new round;
- `Hide hands` hides only the current round;
- every new round/reset shows the guide again;
- a new key/finger introduction forces the guide to show again;
- Progress is a real metrics screen;
- Practice weak keys produces useful practice;
- Settings offers 2–3 soft themes with black/Midnight as default;
- Settings can turn soft typing sounds on/off;
- theme and sound preferences persist;
- F1 → Something Else → custom text → Build Practice produces a visible, usable practice flow;
- Build Practice never silently does nothing;
- active unfinished work is protected before generated text replaces it;
- all existing auth, curriculum, save/resume, MiniMax, mastery, and security behavior remains intact;
- tests, typecheck, and production build pass.
