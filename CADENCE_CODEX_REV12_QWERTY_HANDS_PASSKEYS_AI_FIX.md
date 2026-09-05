# Cadence — Codex Implementation Instructions
## REV12 — True QWERTY Keyboard, Human Hand Overlay, Styled Public Login, Two-Passkey Management, and Coach/F2 Practice Reliability

**Date:** September 2026  
**Project:** Learn_to_Type / Cadence  
**Production host:** Cloudflare only  
**Purpose:** implementation instructions for the coding agent based on the current deployed implementation and the attached screenshots.

---

# 0. Scope and non-negotiable baseline

Implement this revision **on top of the existing production Cadence application**.

Do not rewrite the project into a new stack.

Preserve:

- Cloudflare as the mandatory production host;
- existing Worker `leartn-to-type`;
- existing Cloudflare D1 database `learn-to-type`, binding `DB`;
- current Cloudflare production origin/domain;
- React + TypeScript + Vite frontend;
- FastAPI / Cloudflare Python Worker backend;
- existing WebAuthn/passkey identity system;
- existing versioned Cadence access PIN;
- 48-hour maximum authenticated session lifetime;
- existing D1 migration history;
- current 64-module curriculum (`2026.10`);
- MiniMax backend-only integration and secret handling;
- deterministic local typing path;
- key/module mastery;
- save/resume;
- IndexedDB active-session resilience;
- no learner/profile PIN;
- no Admin/Test requirement for normal learner use.

If the current passkey implementation already uses a TypeScript auth Worker + SimpleWebAuthn, extend it there. If the current repository has consolidated passkey handling elsewhere, **extend the existing implementation rather than creating a parallel authentication service**.

Before editing, run the existing tests and inspect:

```text
current visual keyboard component
current keyboard/finger map data
current hand-guide component
current public landing HTML
/auth.js and any public auth CSS
CSP/security headers
current passkey registration/authentication routes
current passkeys D1 schema
current Coach/Training Console
F1/F2 shortcut routing
AI lesson generation endpoint
deterministic AI fallback
current module_01 / Anchor Keys constraints
```

---

# 1. Screenshot defect: keyboard is NOT laid out as QWERTY

The screenshot shows the current keyboard in an incorrect order similar to:

```text
q a z   w s x   e d c   r t f
g v b   y u h   j n m   i k ,
o l .   p ; /   space
```

That is not a keyboard.

It appears that the UI is laying keys out by **finger ownership / finger-map grouping** rather than by physical keyboard geometry.

That is a serious teaching defect.

Cadence teaches standard **US QWERTY touch typing**. The visible keyboard must physically resemble the keyboard the learner is using.

## 1.1 Separate keyboard geometry from finger ownership

There must be two independent concepts:

```text
KEYBOARD_LAYOUT
= where a key appears physically

KEY_FINGER_MAP
= which finger owns that key
```

Never derive visual key order by iterating or grouping `KEY_FINGER_MAP`.

Never sort visual keys by:

```text
hand
finger
mastery
introduction order
allowed-character set
```

Create/repair a canonical physical layout such as:

```ts
const QWERTY_ROWS = [
  ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
  ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
  ["CapsLock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "Enter"],
  ["ShiftLeft", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "ShiftRight"],
  ["Space"]
];
```

The production visual may omit or simplify some modifier key labels if that is cleaner for beginner mode, but the letter/punctuation positions must remain faithful to standard US QWERTY.

At an absolute minimum, the visible teaching rows must be:

```text
Q W E R T Y U I O P
 A S D F G H J K L ;
  Z X C V B N M , . /
           SPACE
```

Recommended production layout:

```text
Q  W  E  R  T  Y  U  I  O  P  [  ]
 A  S  D  F  G  H  J  K  L  ;  '
  Z  X  C  V  B  N  M  ,  .  /
                 SPACE
```

Use realistic row offsets.

## 1.2 Show locked/unintroduced keys in place

Do not remove unlearned keys and allow the remaining keys to collapse/reflow.

Instead:

```text
introduced / currently usable key
→ normal muted key

current target
→ active highlight

future/unintroduced key
→ visibly dimmed/disabled-looking key
```

The physical keyboard must remain stable while the curriculum advances.

The learner should be building spatial memory.

## 1.3 F/J home bumps

Display a subtle physical home-row bump/marker on:

```text
F
J
```

This must be part of the keycap itself.

## 1.4 Keyboard tests

Add tests that verify exact visual order:

```text
row 1 letters = q w e r t y u i o p
row 2 letters = a s d f g h j k l ;
row 3 letters = z x c v b n m , . /
```

Also test:

- F and J contain home-position markers;
- filtering by introduced keys does not reorder keys;
- changing current target does not reorder keys;
- finger-map data cannot control DOM order;
- every visual key resolves to its correct finger where a finger mapping exists.

---

# 2. Replace the text-only hand guide with actual HUMAN HANDS

The current screenshot shows a text strip like:

```text
Home anchors F / J · right index for Y · J → Y → J
```

That is helpful as a label but it is **not the hand visualization requested by the product specification**.

The production UI must visibly show **two human hands** positioned over the keyboard.

## 2.1 Technology

Implement the hand layer in the browser using:

```text
React + TypeScript
SVG
CSS transforms/transitions
Web Animations API where sequencing is useful
```

Do not use:

- video;
- GIFs;
- Canvas-only animation;
- Phaser;
- PixiJS;
- a server-rendered animation;
- MiniMax;
- a Cloudflare request per movement.

Cloudflare serves the React/SVG code.

The animation executes locally in the learner's browser.

## 2.2 Human-hand appearance

Create original vector hands.

Required visual direction:

```text
human hand silhouettes / line-art
white
semi-transparent
clean
subtle
modern
not cartoon gloves
not emojis
not abstract dots
```

Suggested base styling:

```text
inactive hand fill: white at approximately 8–15% opacity
inactive outline: white at approximately 18–30%
active finger: white at approximately 45–70%
active fingertip/target highlight: stronger but still soft
```

Adapt actual values to the existing theme.

Do not make the hands opaque enough to hide key labels.

## 2.3 Hand geometry

Use a common coordinate system between:

```text
VisualKeyboard
HandsOverlay
FingerGuide
```

Recommended component structure:

```text
frontend/src/components/keyboard/
  VisualKeyboard.tsx
  KeyCap.tsx
  HandsOverlay.tsx
  HumanHand.tsx
  FingerGuide.tsx
  keyboardGeometry.ts
  qwertyLayout.ts
  fingerMap.ts
```

Each hand must expose independently addressable fingers:

```text
left.pinky
left.ring
left.middle
left.index
left.thumb

right.thumb
right.index
right.middle
right.ring
right.pinky
```

At home position, fingertips visually rest on or just above:

```text
Left:
A S D F

Right:
J K L ;

Thumbs:
near Space
```

The hands should look like hands resting naturally above the keyboard rather than floating far below it.

## 2.4 Active finger movement

The complete hand remains visible and translucent.

When demonstrating a reach, the owning finger becomes more visible and moves.

Examples:

```text
R
left index
F → R → F
```

```text
Y
right index
J → Y → J
```

```text
W
left ring
S → W → S
```

```text
N
right index
J → N → J
```

Sequence:

1. show both hands in home position;
2. highlight the home key;
3. emphasize the responsible finger;
4. animate the finger toward the target;
5. highlight the target key;
6. pause briefly;
7. animate the finger back home;
8. leave both hands in home position until hidden or the round begins.

The animation is instructional, not a biomechanical simulation. It just needs to clearly communicate the correct reach.

## 2.5 Full-hand placement must be visually obvious

At the beginning of a beginner level, the learner should be able to look at the screen and immediately understand:

```text
left pinky  → A
left ring   → S
left middle → D
left index  → F

right index  → J
right middle → K
right ring   → L
right pinky  → ;
```

Retain a short text caption if useful, but the caption is secondary to the hands.

Example:

```text
Find home · Rest your fingers on A S D F and J K L ;
Feel the bumps on F and J.
```

---

# 3. Exact hand visibility/reset behavior

Use the following behavior as the authority for this revision.

## 3.1 Every new level

At the first round of every new curriculum level/module:

```text
force human hands visible
→ show full current hand placement
→ animate newly introduced movement(s)
```

This happens even if the learner had previously hidden the hands.

## 3.2 Every round by default

If the learner has not explicitly hidden the hands for the current placement pattern:

```text
round starts
→ show human hands
```

Do not replace them with text only.

## 3.3 Hide Hands

Provide a subtle real button:

```text
Hide hands
```

When pressed:

```text
hide the overlay
→ remember that the learner hid THIS placement pattern
```

Do not delete the hand feature.

## 3.4 Placement signature

Track a teaching/placement signature for the round.

Conceptually:

```ts
placementSignature = hash({
  homePosition,
  activeFingerSet,
  newlyIntroducedKeys,
  newlyIntroducedReachTypes,
});
```

When the learner presses `Hide hands`:

```text
hiddenPlacementSignature = current placementSignature
```

For another round with the exact same placement signature:

```text
hands may remain hidden
```

This implements the user's explicit “unless I hide them” behavior.

## 3.5 Any changed hand position/reach FORCES the hands back

At the start of a new round:

```text
if placementSignature changed:
    clear prior hidden state
    show hands
    demonstrate the changed/new movement
```

Force reappearance for:

- a new level/module;
- a new key;
- a newly active finger;
- a new row reach;
- Shift introduction;
- number-row introduction;
- punctuation reach introduction;
- any actual teaching reset that changes how the learner is expected to use the keyboard.

The learner must press `Hide hands` again for the new hand-position/reach state.

## 3.6 Manual Show Hands

When hidden, expose a subtle:

```text
Show hands
```

or Coach action:

```text
Show finger placement
```

This restores the overlay and can replay the current movement.

## 3.7 Reduce Motion

With Reduce Motion:

```text
show real hand silhouettes
show responsible finger
show home key
show target key
show a small directional indicator
```

Do not remove the hands just because movement is reduced.

---

# 4. Fix the public landing/login screen design

The attached screenshot shows the public landing as browser-default HTML:

```text
Times/serif-style default text
unstyled native buttons
white page
no Cadence dark theme
```

This is not acceptable.

The page must look like part of Cadence while remaining a small public authentication page.

## 4.1 Diagnose why styling is missing

Inspect:

```text
server-rendered landing HTML
public CSS route
public JS route
Worker static routing
CSP style-src
asset auth gate rules
```

Likely failure classes to investigate:

- stylesheet never linked;
- stylesheet routed behind authenticated `/app/*`;
- wrong production path;
- CSP blocking the CSS;
- public auth HTML was created without the designed CSS;
- build/deploy omitted the public auth stylesheet.

Do not merely add a few inline styles and ignore the routing problem.

## 4.2 Public assets remain public but minimal

Keep the React training application private.

The public page may safely load small same-origin resources such as:

```text
/auth.css
/auth.js
```

These resources contain only landing/passkey UI code and styling.

They must not expose private learner data.

Prefer external same-origin CSS/JS so the current strict CSP can remain strong.

## 4.3 Required design

Target:

```text
full viewport dark Cadence background

top:
  CADENCE
  small "Focused touch typing" / performance-lab treatment

center:
  dark raised authentication panel
  "Learn to type. Build your rhythm."
  short description
  primary "Sign in with passkey"
  secondary "Create account"

bottom:
  About · Produced by Noverel · September 2026
```

Use the main app's design tokens.

Suggested visual structure:

```text
┌─────────────────────────────────────────────────────────────┐
│  CADENCE                                                    │
│  Focused touch typing                                      │
│                                                             │
│                  LEARN TO TYPE                              │
│                  BUILD YOUR RHYTHM                          │
│                                                             │
│        A focused trainer for touch typing, rhythm,           │
│        accuracy, and steady progress.                        │
│                                                             │
│             [ Sign in with passkey ]                         │
│                                                             │
│                 New to Cadence?                              │
│                [ Create account ]                            │
│                                                             │
│  ───────────────────────────────────────────────────────    │
│  About · Produced by Noverel · September 2026               │
└─────────────────────────────────────────────────────────────┘
```

Visual direction:

- black / blue-black background;
- soft blue/teal Cadence accents;
- subtle track/cadence line motif in background;
- high-quality system sans-serif typography;
- rounded dark panel;
- visible keyboard focus rings;
- responsive desktop/mobile layout;
- no giant marketing section;
- no white page flash if avoidable.

## 4.4 Public page tests

Test:

- public page has dark Cadence class/theme;
- CSS is successfully returned in production build;
- no unauthenticated access to private `/app/*` is introduced;
- passkey buttons remain functional;
- CSP remains valid;
- keyboard navigation works.

---

# 5. Add "Login & Passkeys" to the authenticated menu

Add a learner-accessible menu item:

```text
Login & Passkeys
```

This is normal user account security, not Admin/Test Mode.

Suggested menu placement:

```text
Start / Continue
Practice weak keys
Progress
Character
Settings
Login & Passkeys
How training works
Accessibility
Exit
```

A nested Settings → Security screen is also acceptable, but there must be an obvious menu path named around **Login / Passkeys**.

---

# 6. Standard passkey-management flow — maximum TWO passkeys per user

Use the current WebAuthn/passkey implementation and current SimpleWebAuthn package version.

Do not invent custom passkey cryptography.

Official guidance supports multiple passkeys for one account, authenticated management of registered passkeys, and use of `excludeCredentials` to avoid registering an existing credential again.

## 6.1 UI

Screen:

```text
LOGIN & PASSKEYS

Passkeys
Use a passkey to sign in to Cadence.

1 of 2 passkeys

┌───────────────────────────────────────┐
│ My laptop                             │
│ Synced passkey / This device          │
│ Added Sep 5, 2026                     │
│ Last used Sep 5, 2026                 │
│                         [ Remove ]     │
└───────────────────────────────────────┘

[ Add another passkey ]

For best recovery, keep a second passkey on another
device or security key.
```

When there are two:

```text
2 of 2 passkeys

[ Add another passkey ] disabled
Maximum 2. Remove one before adding another.
```

Do not claim a precise device/brand unless the WebAuthn metadata actually provides reliable information.

Allow an optional user-defined nickname such as:

```text
My laptop
My iPhone
Backup security key
```

## 6.2 Maximum count

Enforce on the server:

```text
MAX_PASSKEYS_PER_USER = 2
```

Do not rely only on a disabled frontend button.

If count >= 2:

```text
add/options endpoint
→ reject with a clean application error
```

## 6.3 Add passkey flow

User must already be signed in to the account.

Flow:

```text
Login & Passkeys
→ Add another passkey
→ server verifies current authenticated user
→ server checks passkey count < 2
→ generate new WebAuthn registration options for SAME user
→ store fresh short-lived challenge
→ browser starts registration
→ server verifies response
→ store the new credential on SAME user
→ refresh list
```

Use the user's stable existing WebAuthn user ID.

Do not create a new Cadence user/player.

For SimpleWebAuthn registration, follow the current installed API signatures and use the existing RP configuration.

Conceptually:

```ts
generateRegistrationOptions({
  rpName: "Cadence",
  rpID,
  userName: stableAccountHandle,
  attestationType: "none",
  excludeCredentials: existingPasskeys.map((p) => ({
    id: p.credentialId,
    transports: p.transports,
  })),
  authenticatorSelection: {
    residentKey: "required",
    userVerification: "preferred",
  },
})
```

Use current package signatures rather than blindly copying this pseudocode.

Persist at least the existing credential fields already used by Cadence:

```text
credential ID
public key
counter
transports
credential device type, when available
backup state, when available
created_at
last_used_at
optional user nickname
```

## 6.4 Fresh challenge and verification

For every add-passkey ceremony:

```text
fresh random challenge
short expiration, approximately 5 minutes
bound to current authenticated account/session
single use
```

Verify server-side:

```text
expected challenge
expected production origin
expected RP ID
WebAuthn signature
credential data
```

Invalidate the challenge after verification.

Never trust a browser-supplied user ID.

Never store the private key; the authenticator owns it.

## 6.5 "Change passkey" means replace, not mutate

A WebAuthn passkey cannot be edited into a different cryptographic credential.

Implement the UI concept as:

```text
Replace passkey
= add a new passkey, verify it, then remove the old passkey
```

Do not promise to "change" the cryptographic key in place.

### Safe replacement

If the account has one passkey:

```text
Add another passkey first
→ verify it works
→ then user may remove the old passkey
```

If the account already has two:

```text
remove the passkey being replaced
→ one known-good passkey remains
→ add replacement
```

A guided `Replace` action may walk the user through this sequence.

## 6.6 Never allow normal UI to remove the LAST passkey

Cadence has no password fallback.

Therefore:

```text
passkey count == 1
→ Remove disabled
```

Explain:

```text
Add a second passkey before removing this one.
```

If the last passkey is lost, use the existing controlled recovery mechanism rather than letting the normal settings screen delete the user's final login credential.

## 6.7 Remove passkey

For a user with two passkeys:

```text
Remove
→ confirmation
→ authenticated account ownership check
→ delete only selected server-side credential/public key
→ remaining passkey stays valid
```

Recommended confirmation:

```text
Remove this passkey?

It will no longer be able to sign in to Cadence.
Your other passkey will keep working.

[ Remove passkey ]
[ Cancel ]
```

## 6.8 Recent authentication

For adding/removing a passkey, require a valid active authenticated session.

If the current authentication is considered too old by the existing auth design, trigger passkey re-authentication before the destructive/security-sensitive operation.

Do not request a password or learner PIN.

## 6.9 Passkey list metadata

Show useful but honest information.

Good:

```text
My laptop
Synced passkey
Added Sep 5
Last used today
```

Avoid inventing:

```text
Windows Hello
iPhone
Face ID
```

unless reliably known or user-entered as the nickname.

## 6.10 Passkey-management tests

Add tests for:

1. authenticated user can list only their own passkeys;
2. user with one passkey can add a second;
3. added passkey uses same user ID/player;
4. `excludeCredentials` contains existing credentials;
5. challenge is short-lived and single-use;
6. wrong challenge fails;
7. wrong origin fails;
8. wrong RP ID fails;
9. server rejects a third passkey;
10. UI displays `2 of 2`;
11. last remaining passkey cannot be removed in normal UI;
12. user with two passkeys can remove one;
13. deleting one does not invalidate the other;
14. removing another user's credential is impossible;
15. replace flow preserves the account and all typing progress;
16. no password/profile PIN is introduced;
17. passkey management does not reset access-PIN acceptance;
18. passkey management does not reset the 48-hour session policy.

---

# 7. Fix F1 / F2 / Build Practice failure

The current Coach flow shows:

```text
Training console · AI ready
Anchor Keys · 10% mastery

Continue the plan
Give me another short pattern   F2
Give me text to type
Full text unlocks after you learn more letters.
Practice weak keys
Available after I spot a repeated pattern.

Something else…
Build practice
```

and then returns:

```text
I could not build that practice.
Try another request or keep the current round.
```

At Anchor Keys this is not acceptable.

The current specification already requires deterministic fallback content.

A valid beginner request must **not fail simply because natural-language text is impossible with the current allowed key set**.

## 7.1 First reproduce and diagnose the exact defect

Before changing code, reproduce the failure in the current deployment/local Worker.

Inspect the complete request:

```text
F1
→ Coach opens
→ F2 / short-pattern reshuffle
or
→ Something else
→ Build practice
→ frontend request payload
→ backend route
→ current module constraints
→ allowed characters
→ target length
→ MiniMax/cache/fallback
→ validation
→ HTTP status
→ frontend response parsing
→ generated-content state
```

Report the actual root cause.

Do not assume MiniMax is the problem merely because the UI says AI ready.

Potential classes to test, without assuming one is correct:

```text
client sends wrong stage/module ID
client sends outdated curriculum version
client sends an illegal allowed-key list
backend rejects too-small/too-large target
MiniMax produces forbidden characters
fallback is not invoked after validation failure
fallback text violates validator
frontend discards a successful fallback response
F2 calls the wrong action
Build Practice submits an empty/stale request
request is treated as "full passage" when only a pattern drill is valid
```

## 7.2 F2 is global reshuffle

Preserve:

```text
F2 = reshuffle current/upcoming training content
```

F2 is not a dynamic Coach choice key.

When Coach is open, the UI may visually show a small F2 keycap next to `Give me another short pattern` only if that control invokes the exact same global reshuffle action.

Do not concatenate the label visually as:

```text
Give me another short patternF2
```

Render the shortcut as a distinct subdued keycap/badge.

## 7.3 F2 at Anchor Keys must ALWAYS have a safe result

For a very early stage such as Anchor Keys:

```text
full prose may be impossible
```

Therefore:

```text
F2
→ choose another current-stage constrained pattern
→ validate
→ stage it for use
```

Use priority:

```text
1. valid cached constrained content
2. MiniMax constrained generation, when appropriate
3. deterministic built-in/pattern fallback
```

A valid Anchor Keys reshuffle must not terminate with:

```text
I could not build that practice
```

unless the local curriculum itself is corrupted.

## 7.4 Deterministic early-stage generator

Implement/repair a guaranteed key-safe generator.

Inputs:

```text
allowed characters
focus keys
current module
recently used patterns
target approximate length
```

For example, if allowed characters are only:

```text
f
j
space
```

the fallback can safely create structured patterns such as:

```text
f j f j
ff jj fj jf
j f j f
fj jf fj jf
```

Use the actual current module's allowed set.

Do not force natural English where natural English cannot be represented.

Avoid one-character spam.

Avoid identical fallback every time.

This fallback must be testable without MiniMax.

## 7.5 "Give me text to type" at an early level

If the learner has not unlocked enough letters for natural text:

do not send them into a failing full-passage generation path.

Instead say:

```text
Full sentences unlock after you learn more letters.
I can build a fresh pattern with the keys you know now.
```

Actions:

```text
[ Build short pattern ]
[ Show finger placement ]
[ Keep current round ]
```

If the learner types a custom request such as:

```text
give me something about running
```

at Anchor Keys, do not error.

Respond:

```text
You don't have enough letters unlocked for a running passage yet.
I made a new key-safe practice instead.
```

Then provide the valid constrained drill.

## 7.6 Build Practice must never silently fail

For any valid typing-related custom request:

```text
Build practice
→ loading state
→ valid generated/cached/fallback practice
OR
→ visible precise recoverable error
```

Prefer fallback over error whenever a current-stage drill can be constructed.

The error:

```text
I could not build that practice
```

should be reserved for actual system failure where:

```text
AI failed
AND cache unavailable
AND deterministic fallback failed
```

With a valid curriculum stage, deterministic fallback should make this extraordinarily rare.

## 7.7 Build Practice response handling

On success show:

```text
Practice ready

Short Anchor Keys pattern
Uses only your current keys.

[ Start practice ]
[ Build another ]
[ Keep current round ]
```

Do not make the user guess whether anything happened.

If the current round is active, do not silently discard it.

Offer:

```text
[ Save & start practice ]
[ Keep current round ]
```

## 7.8 F1/F2 reliability tests

Add tests for:

1. F1 opens Coach;
2. F2 with Coach closed reshuffles;
3. F2 with Coach open invokes the same reshuffle action;
4. F2 at Anchor Keys produces valid key-safe content;
5. MiniMax timeout on F2 still produces fallback;
6. MiniMax invalid-character response still produces fallback;
7. generated early-stage content contains no locked character;
8. early `Give me text to type` does not call an impossible full-text path;
9. early custom topic request converts to constrained practice;
10. Build Practice shows loading state;
11. Build Practice success shows preview;
12. Start Practice loads the result;
13. active round is not silently discarded;
14. current curriculum version is included/validated correctly;
15. no valid current-stage request ends in a silent no-op;
16. fallback generator produces multiple valid variants.

---

# 8. Hand guidance + keyboard must share the SAME physical geometry

Do not separately eyeball the hand positions and keyboard positions.

Create one geometry model.

Conceptually:

```ts
type KeyGeometry = {
  code: string;
  label: string;
  row: number;
  x: number;
  y: number;
  width: number;
  height: number;
  centerX: number;
  centerY: number;
};
```

Then:

```text
VisualKeyboard
→ renders key geometry

HandsOverlay
→ uses same key centers

FingerGuide
→ calculates movement from home-key center to target-key center
```

This prevents:

```text
finger pointing at the wrong key
hands drifting when keyboard resizes
animations breaking on responsive layouts
```

Use responsive scaling of one coordinate system rather than separate hard-coded pixel values for every viewport.

---

# 9. Recommended hand-overlay layering

Use:

```text
keyboard container
  z-index 1: keycaps
  z-index 2: key highlights
  z-index 3: translucent hand SVG
  z-index 4: active finger highlight / movement
  z-index 5: optional small instructional caption
```

Set:

```css
pointer-events: none;
```

on the hand overlay itself.

The `Hide hands` / `Show hands` button is outside the SVG overlay and remains clickable.

The hands must never intercept typing input or key buttons.

---

# 10. Cloudflare deployment requirements for these changes

Cloudflare remains the only production target.

The new work should require no special animation server.

Architecture remains:

```text
Cloudflare
  ↓
serves public auth.css/auth.js
  ↓
serves authenticated React/Vite app
  ↓
browser renders QWERTY + SVG human hands locally
```

Passkey management remains server-verified through the existing WebAuthn backend/auth Worker and D1.

MiniMax remains backend only.

Do not:

- move animation to a separate service;
- create a second database;
- create a second user table when one already exists;
- expose WebAuthn private material;
- expose MiniMax credentials;
- bypass Worker auth to make styling easier.

---

# 11. Passkey research basis for the coding agent

Use current official documentation and verify installed package signatures before editing.

Research guidance incorporated into this revision:

### MDN Passkeys

MDN describes passkeys as WebAuthn public/private-key credentials, recommends that relying parties support multiple passkeys for a single account, and describes authenticated passkey management where users can view and delete registered credentials.

MDN also documents `excludeCredentials` as a way to stop an authenticator from registering a credential that is already registered for the account.

Reference:

```text
https://developer.mozilla.org/en-US/docs/Web/Security/Authentication/Passkeys
```

### SimpleWebAuthn Passkeys

Use discoverable credentials and the current SimpleWebAuthn registration/authentication APIs.

For passkey-oriented registration, current guidance includes:

```text
residentKey: required/preferred depending current design
userVerification: preferred
attestationType: none
```

Save credential transports and credential device/backup metadata when provided.

Reference:

```text
https://simplewebauthn.dev/docs/advanced/passkeys
```

### SimpleWebAuthn server package

For adding an authenticator/passkey to an already authenticated user:

```text
retrieve logged-in user
retrieve existing passkeys
generate registration options
include existing credentials in excludeCredentials
remember challenge/options
verify registration response
save verified credential
```

Reference:

```text
https://simplewebauthn.dev/docs/packages/server
```

Use exact signatures from the package version installed in the repository.

---

# 12. Manual acceptance requirements

Codex must manually verify all of these after automated tests pass.

## A. QWERTY

Open training.

Verify visually:

```text
Q W E R T Y U I O P
A S D F G H J K L ;
Z X C V B N M , . /
```

No finger-grouped layout remains.

## B. Human hands

Start Anchor Keys.

Verify:

```text
two translucent white human hands visible
left fingertips aligned A S D F
right fingertips aligned J K L ;
F/J home bumps visible
```

## C. New reach

Enter a round introducing Y.

Verify:

```text
right index visually moves J → Y → J
```

## D. Hide behavior

```text
Hide hands
→ hands disappear

same placement remains hidden where expected

new round with changed placement/reach
→ hands automatically reappear
```

## E. Public page

Sign out.

Verify:

```text
dark Cadence-designed login
CADENCE brand at top
styled passkey buttons
About/Noverel footer
no browser-default serif page
```

## F. Add second passkey

```text
Login & Passkeys
→ 1 of 2
→ Add another passkey
→ complete WebAuthn ceremony
→ 2 of 2
→ both can authenticate account
```

## G. Maximum two

With two passkeys:

```text
Add another passkey disabled
server also rejects third credential registration
```

## H. Remove protection

With one passkey:

```text
Remove disabled
```

With two:

```text
remove one
→ remaining one still logs in
→ profile/progress unchanged
```

## I. F2 at Anchor Keys

```text
open Anchor Keys
→ press F2
→ fresh valid constrained pattern produced
```

No `I could not build that practice` error.

## J. F1 custom practice

```text
F1
→ Something else
→ ask for a new practice
→ Build practice
```

At early level:

```text
key-safe pattern appears
```

At capable later level:

```text
validated passage/drill appears
```

---

# 13. Required completion report

At the end, Codex must report:

## Screenshot defects

For each:

```text
incorrect keyboard order
missing real hands
unstyled public login
F1/F2 practice failure
```

state:

```text
root cause
files changed
tests added
production verification result
```

## Passkeys

Report:

```text
current auth implementation location
SimpleWebAuthn/package version
routes used for list/add/remove
server-side max count enforcement
challenge storage/expiry
last-passkey deletion protection
D1 fields used
```

Never report private/public key material.

## Commands run

Include:

```text
frontend tests
backend tests
typecheck
production build
E2E
D1 migration list/apply if needed
deploy command
production smoke tests
```

Do not claim success for anything not actually tested.

---

# 14. Definition of Done

REV12 is complete only when:

- the visual keyboard is a faithful US QWERTY keyboard;
- no finger-map ordering leaks into visual key order;
- future/unintroduced keys stay physically in place;
- F/J bumps are visible;
- real translucent white human hands are rendered above/on the keyboard;
- the hands visibly place fingers on A S D F and J K L ;
- target fingers actually animate from home key to target and back;
- a new level forces the hands visible;
- normal rounds show hands according to the defined placement-signature behavior;
- Hide Hands works;
- a changed hand/reach state forces hands to reappear;
- Reduce Motion still shows actual instructional hand placement;
- public login is styled in the Cadence dark design instead of default HTML;
- public styling works without exposing the private application;
- authenticated menu includes Login & Passkeys;
- each account can hold at most two passkeys;
- user can add a second passkey through standard WebAuthn registration;
- existing passkeys are excluded from duplicate registration;
- passkey challenges are server-side, short-lived, and non-replayable;
- a third passkey is rejected server-side;
- the last passkey cannot be removed in normal settings;
- replacing a passkey preserves the same account and all progress;
- F2 at Anchor Keys always produces valid current-stage practice through cache/AI/fallback;
- early full-text requests downgrade gracefully to constrained pattern practice;
- Build Practice does not silently fail;
- active work is protected before a generated practice replaces it;
- all existing Cloudflare, access-PIN, 48-hour session, D1 progress, MiniMax, curriculum, and security behavior remains intact.
