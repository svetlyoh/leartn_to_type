# Typing App — Product Specification & Concept Summary

## 1. Product Vision

Build a modern typing-learning application for a teenager who has not yet learned touch typing and finds existing typing apps boring, childish, ad-heavy, or overly commercial.

The app should feel:

- **Modern**
- **Intelligent**
- **Calm**
- **Purposeful**
- **Personal**
- **Teen-appropriate**
- **Skill-oriented rather than game-oriented**
- **Free of ads and unnecessary monetization pressure**
- **Able to evolve over time without requiring a huge hard-coded library of lessons**

The goal is not to make “another typing game.” The goal is to create a **personal typing training system** that teaches correct technique, adapts to the learner, remembers progress, and uses subtle AI support to keep the content fresh and useful.

A good metaphor is **training**, especially track/running training: consistency, cadence, personal bests, recovery, form, and long-term improvement.

---

## 2. Target User

### Primary learner

The primary learner is a 14-year-old beginner typist.

Relevant traits discussed:

- Studious
- Reflective
- Thoughtful
- Above-average intelligence
- Likes running/track
- Likes video games
- Current on Gen Z culture, language, and trends
- Dislikes existing typing apps because they feel boring, dated, childish, ad-filled, or not meaningful
- Can become strongly frustrated when performance does not meet expectations

The product should respect his intelligence and avoid patronizing language or childish visual design.

### Secondary users

The app should also support:

- Parent testing
- Older sibling / teenager testing
- Advanced-user testing
- Developer/test profiles

These users may want to jump directly into harder lessons instead of starting from beginner mode.

---

## 3. Core Design Philosophy

### 3.1 Progress, not punishment

Mistakes should be treated as **information**, not failure.

Avoid:

- Loud error sounds
- Red “wrong” flashes
- Game-over states
- Shame-based messaging
- Negative score drops
- Angry reactions
- Loss of streaks because of one bad session
- Punitive timers in beginner mode

Instead:

- Gently identify the key or movement that needs attention
- Offer a hint
- Reduce difficulty when useful
- Give the learner another attempt
- Emphasize long-term improvement
- Reward recovery and consistency, not perfection

### 3.2 Meaningful gamification

The app should use **light gamification**, but not feel like a mobile reward machine.

Use:

- Personal bests
- Training checkpoints
- Milestones
- Progress maps
- Skill mastery
- Cadence / rhythm concepts
- Weekly trends
- “Today’s run” or “training session” framing
- Real skill achievements

Avoid:

- Coins
- Loot boxes
- Fake currencies
- Excessive badges
- Confetti after every action
- Constant level-up animations
- Casino-like feedback loops

### 3.3 Calm, grown-up visual language

The app should feel like a **skill dojo, training console, or performance lab**, not an elementary-school learning game.

---

# 4. Theme and Visual Direction

## Recommended overall theme

A **modern training environment** inspired by running, rhythm, cadence, and personal performance.

Possible conceptual names/themes discussed:

- **Cadence**
- Training
- Personal Best
- Flow
- Track / Run / Pace metaphor

“Cadence” is especially appropriate because it connects:

- Typing rhythm
- Running rhythm
- Consistency
- Flow
- Skill development

The final name is still open.

## Visual style

Recommended:

- Dark or muted background
- Minimal interface
- High contrast where needed
- Subtle motion
- Soft transitions
- Clean typography
- No cartoon-heavy design
- No noisy backgrounds
- No ad-like visual clutter

The design should feel closer to:

- A modern coding tool
- A training dashboard
- A game performance screen
- A minimal terminal
- A sports training app

than to a traditional school typing website.

---

# 5. Primary Screen Layout

The primary typing screen should remain focused.

Suggested layout:

1. **Top area**
   - Current training objective
   - Short lesson title
   - Optional pace / session indicator
   - Small progress indicator

2. **Center**
   - Text or typing prompt
   - Current character / word
   - Smooth progression through the exercise

3. **Lower center**
   - Visual keyboard
   - Key hints when needed
   - Optional finger/hand animation

4. **Side or collapsible area**
   - Coach
   - AI training console
   - Hints
   - Session settings

5. **Bottom / subtle status**
   - Current WPM
   - Rhythm / cadence indicator
   - Accuracy
   - Optional session time

The interface should avoid constantly showing too many performance numbers while the learner is actively typing.

---

# 6. Curriculum Structure

## Core principle

The **curriculum should be structured**, but individual exercises do not need to be hard-coded forever.

Do not let an AI invent the pedagogy from scratch.

Instead:

- Define a stable curriculum
- Define required milestones
- Define keys and techniques introduced at each stage
- Let AI generate or reshuffle practice material inside those constraints

## Example curriculum progression

Possible sequence:

1. Keyboard orientation
2. Home row
3. Left-hand home row
4. Right-hand home row
5. Alternating hands
6. Top-row keys
7. Bottom-row keys
8. Common letter combinations
9. Capital letters / Shift
10. Punctuation
11. Numbers
12. Symbols
13. Short words
14. Sentences
15. Paragraphs
16. Realistic writing
17. Speed-building
18. Accuracy-building
19. Long-form typing
20. Advanced challenge mode

The curriculum should also introduce:

- Proper finger assignment
- Hand position
- Returning to home row
- Reach technique
- Relaxed posture
- Rhythm
- Looking at the screen rather than the keyboard
- Consistency before speed

## Adaptive progression

The learner should not advance only because a lesson number is complete.

Progression should consider:

- Accuracy
- Repeated error patterns
- Comfort with newly introduced keys
- Rhythm
- Consistency
- Whether the learner is relying heavily on hints
- Whether performance is stable across more than one short exercise

---

# 7. Lesson Engine

The app should have a **lesson engine** rather than a giant static set of lessons.

The lesson engine can combine:

- Curriculum stage
- Known keys
- Weak keys
- Recent errors
- Current difficulty
- Session goals
- Previously seen content
- User preferences

It can then select or generate the next drill.

This allows the app to evolve without requiring hundreds of manually authored modules.

## Content sources

The app can use a combination of:

### Built-in content
- Starter drills
- Core curriculum exercises
- Carefully validated beginner lessons
- Offline fallback content

### Generated content
AI may generate:

- New word lists
- New sentences
- New short passages
- Variations on existing drills
- Weak-key exercises
- Themed content
- Advanced challenges

AI-generated content must obey the current curriculum constraints.

Example:

> Curriculum says: use only A, S, D, F, J, K, L.

The AI can create new drills using only those allowed keys.

---

# 8. AI Layer

The AI should be a **tool inside the training system**, not the curriculum itself.

## Responsibilities of the AI

The AI may:

- Generate fresh practice material
- Reshuffle exercises
- Create a harder or easier version
- Explain why a specific key is difficult
- Interpret recent error patterns
- Suggest what to practice next
- Generate a targeted drill
- Answer training questions
- Create content around a user-selected topic
- Give short post-session observations

## Examples

The learner could ask:

- “Give me something harder.”
- “Why do I keep missing P?”
- “Make this less repetitive.”
- “Give me a 2-minute challenge.”
- “Practice my weak keys.”
- “Give me a passage about running.”
- “Make the next lesson more competitive.”

## AI should not

- Change the entire curriculum without rules
- Introduce keys the learner has not learned unless explicitly requested
- Overload the learner with explanations
- Act like a generic open-ended chatbot during every session
- Make every keystroke depend on an API call

---

# 9. AI Interface: Avoid a Generic Chatbot

The AI should not necessarily look like a standard chat application.

Preferred concept:

## Training Console / Terminal

A modern terminal-style or training-console panel.

Example options:

1. Practice weak keys
2. Start a new challenge
3. Reshuffle this lesson
4. Explain my mistakes
5. Ask the coach
6. Make it easier
7. Make it harder
8. Type a custom request

The learner can:

- Click an option
- Type a number
- Type a short phrase
- Use freeform input if desired

This gives the AI structure and makes it feel like a tool inside the app rather than “another chatbot.”

---

# 10. Coach System

The **AI** and the **Coach** should be conceptually separate.

## AI

The functional intelligence.

It:

- Generates
- Analyzes
- Explains
- Selects
- Adapts

## Coach

The motivational personality layer.

It:

- Encourages
- Challenges
- Frames progress
- Highlights personal improvement
- Gives short contextual reactions
- Makes the training environment feel alive

The coach may use AI internally, but the user experience should distinguish “the training system” from “the coach personality.”

---

# 11. Coach Character / Visual Presence

A coach character can appear, but should not feel like a childish virtual pet.

Possible visual directions:

- Runner silhouette
- Track athlete
- Slightly older training companion
- Abstract coach avatar
- Minimal animated figure
- Stylized performance mentor

The character should **not remain on screen constantly**.

Recommended behavior:

- Appears before a session
- Appears after a session
- Appears for meaningful milestones
- Appears if the learner requests help
- Appears occasionally with a short challenge
- Can be completely hidden

During active typing, the interface should remain focused.

---

# 12. Coach Personality Modes

The learner should be able to control the coach’s personality and frequency.

Possible modes:

### Silent
No motivational comments unless explicitly requested.

### Calm
Supportive, low-pressure, occasional feedback.

### Focused
Short, practical performance guidance.

### Competitive
Challenges personal bests and asks for small improvements.

Example:

> “Last session: 42 WPM. Want to try for 43 without losing rhythm?”

### High-energy
More frequent encouragement, but still not childish.

## Important rule

Even a competitive coach should **never shame, insult, or become genuinely angry**.

The coach can simulate competitive intensity without making mistakes feel catastrophic.

Good:

> “That round got messy. Reset your rhythm and take another shot.”

Avoid:

> “You failed.”
> “That was terrible.”
> “You keep messing this up.”

---

# 13. Tutorial and Hand/Finger Guidance

The app should visually teach **how to type**, not merely tell the learner which key was wrong.

## Keyboard visualization

Display a keyboard layout at the bottom of the screen.

Use it for:

- New key introduction
- Home-row positioning
- Finger assignment
- Reach direction
- Hints

## Animated hands

A key feature should be **small hand/finger animations**.

Example:

When learning the letter R:

- Show a semi-transparent hand
- Highlight the correct finger
- Animate that finger moving from home row to R
- Return it to home position
- Fade the animation away

This is more instructional than simply turning the R key red.

## When to show animations

Do not animate constantly.

Show them:

- When introducing a new key
- When the learner asks for a hint
- After the same key is missed repeatedly
- During short tutorial moments
- Optionally in “learning mode”

Hide them automatically once the learner demonstrates the movement successfully.

---

# 14. Error Handling

The app should be designed specifically to reduce frustration.

## Avoid

- Red screen flashes
- Buzzers
- “Wrong!”
- Large error counters during active practice
- Sudden game-over
- Harsh resets
- Competitive penalties

## Preferred response

A mistake can cause:

- Slight key glow
- Quiet underline
- Gentle hand hint
- Brief pause
- Small retry
- Adaptive practice after several repeats

Repeated misses should be interpreted as a skill signal.

Example internal logic:

> User misses R three times in 30 seconds.

The app may:

1. Continue without interruption initially
2. Quietly highlight the R reach
3. Offer an optional hand animation
4. Add a short R-focused drill later
5. Mention it gently in the session summary

---

# 15. Difficulty Modes

The app should offer user-controlled difficulty without framing one mode as “bad.”

Possible names:

- Explore
- Practice
- Train
- Challenge

or:

- Relaxed
- Standard
- Focused
- Competitive

Difficulty can affect:

- Typing speed pressure
- Passage length
- Number of unfamiliar keys
- Allowed pauses
- Hint frequency
- Coach frequency
- Challenge targets
- Visibility of live metrics

The learner should be able to adjust difficulty freely.

---

# 16. Test / Developer Mode

A **test mode** should exist from the beginning.

This is important because parents, older teenagers, and developers may need to test advanced behavior without completing beginner lessons.

Test mode should allow:

- Jump to any curriculum stage
- Simulate beginner profile
- Simulate intermediate profile
- Simulate advanced profile
- Unlock all keys
- Set a target WPM
- Set artificial weak keys
- Enable/disable hints
- Trigger coach events
- Trigger hand tutorial animations
- Test AI reshuffling
- Test session summaries
- Reset session state without deleting the profile
- Create temporary test profiles

Test mode should be protected by a parent/admin PIN or clearly separated from the normal learner experience.

---

# 17. Metrics

The app should track more than WPM and raw accuracy.

The goal is to build a richer picture of typing development — a kind of **typing profile / typing DNA**.

## Core speed metrics

- Current WPM
- Average WPM
- Peak WPM
- Best sustained WPM
- Personal-best WPM
- WPM by exercise length
- WPM trend over time

## Accuracy metrics

- Overall accuracy
- Accuracy by session
- Accuracy by key
- Accuracy by finger
- Accuracy by hand
- Accuracy by row
- Accuracy by word length
- Accuracy trend

## Error metrics

- Most frequently missed keys
- Most frequent key substitutions
- Repeated-error patterns
- Error clusters
- Errors after specific letters
- Errors by finger
- Error rate during speed increases
- Error rate when fatigued

## Rhythm / cadence metrics

A signature metric area.

Possible measurements:

- Keystroke interval consistency
- Variation in key-to-key timing
- Pause frequency
- Smoothness
- Rhythm stability
- Burst-and-stall behavior

Potential display names:

- Cadence
- Rhythm
- Flow
- Smoothness
- Consistency

## Recovery metrics

Measure what happens **after a mistake**.

Examples:

- Time to return to normal rhythm
- Number of subsequent errors after one mistake
- Whether mistakes cause a slowdown
- Whether the learner can recover without restarting

This is useful because recovery is a real skill and avoids treating a single error as catastrophic.

## Consistency metrics

- Variation in WPM within a session
- Variation across recent sessions
- Accuracy stability
- Rhythm stability
- Longest sustained clean section
- Performance over 30 sec / 1 min / 3 min / 5 min

## Endurance / focus metrics

- Longest uninterrupted typing duration
- Accuracy over longer passages
- Performance drop over time
- Rhythm over longer sessions
- Session length
- Productive practice time

## Key mastery

For every key, track:

- Introduced / not introduced
- Attempts
- Correct presses
- Error rate
- Average reaction time
- Confidence/mastery
- Recent trend
- Last practiced

## Improvement metrics

- Most improved key
- Most improved finger
- Biggest weekly accuracy gain
- Biggest rhythm improvement
- New personal best
- Weak skill that became stable

## Engagement / practice metrics

Use carefully so they do not become pressure.

- Sessions completed
- Total words typed
- Total characters typed
- Total practice time
- Days practiced
- Recent practice frequency

Avoid punishing missed days.

If a streak is shown, consider a forgiving concept such as:

- Training consistency
- Weekly sessions
- “3 of 4 planned sessions”

instead of an all-or-nothing daily streak.

## Optional contextual insights

If enough history exists:

- Best-performing session length
- Whether shorter or longer drills work better
- Best time of day for performance
- Whether accuracy drops when speed increases

These should be optional insights, not judgments.

---

# 18. Session Summary

Every session should create a saved summary.

The summary can contain:

- Date/time
- Lesson
- Duration
- WPM
- Accuracy
- Rhythm / cadence
- Consistency
- Weak keys
- Strong keys
- Most improved skill
- Best moment
- Difficulty mode
- Hints used
- New keys learned
- Personal bests
- Coach note
- Recommended next step

## Tone of summary

The summary should be reflective and constructive.

Example:

> Strong rhythm today. R and T caused a few pauses, but recovery was much faster than last session. Next time: a short R/T drill before moving on.

This is much better than:

> 7 mistakes. Accuracy 91%. Failed target.

---

# 19. Long-Term Progress

The app should emphasize **change over time**, not a single-session score.

Views may include:

- Weekly trend
- Monthly trend
- Personal-best history
- Key mastery map
- Typing heat map
- Rhythm trend
- Accuracy trend
- WPM trend
- “What got easier”
- “What should we train next”

A single bad day should not make the user feel that progress was lost.

---

# 20. Resume / Continuation Flow

The app should remember exactly where the user stopped.

On return, show something like:

> Welcome back. Last session you were working on R and T.  
> Continue, warm up first, or pick something else?

Possible choices:

1. Continue
2. Warm up
3. Practice weak keys
4. Start a fresh challenge
5. Ask the coach

Saved continuation state should include:

- Current curriculum stage
- Current lesson
- Current exercise position
- Unlocked keys
- Recent weak keys
- Difficulty
- Coach preference
- Hint settings
- Recent performance context

---

# 21. Save System

Progress data should be treated as **sacred**.

The app will evolve, so saved progress must remain compatible across updates.

## Save requirements

Each profile should store:

- Profile ID
- Display name
- Save format version
- Curriculum version
- Current curriculum state
- Lesson state
- Metrics
- Historical sessions
- Key mastery
- Coach settings
- Difficulty settings
- UI preferences
- AI preferences
- Training history
- Recent AI-generated lesson metadata
- Test/admin status if relevant

## Versioning

Every save file should include a schema version.

Example:

```json
{
  "save_version": 3,
  "profile_id": "user_001"
}
```

When the app updates:

- Detect old save version
- Migrate it forward
- Add safe defaults for new fields
- Preserve historical data
- Never silently discard data

## Export / Import

The app should eventually support:

- Export profile
- Import profile
- Backup
- Restore

A single portable file can contain:

- Progress
- Session history
- Preferences
- Metrics
- Coach configuration

---

# 22. Profiles and PIN Login

The app should support multiple local profiles.

## Entry flow

1. Open app
2. See profile selector
3. Prompt: “Who’s training today?”
4. Select profile
5. Enter optional 4–6 digit PIN
6. Resume training

## Profile separation

Each profile must keep separate:

- Progress
- WPM history
- Key mastery
- Session history
- Coach memory
- Settings
- AI recommendations

Parent/testing metrics must never mix with the learner’s progress.

## Parent / admin PIN

A separate parent/admin PIN can unlock:

- Test mode
- Profile management
- Data export
- Data reset
- Advanced settings
- AI configuration
- Curriculum controls
- Developer tools

---

# 23. Technical Direction

## Recommended first version

A **browser-based application with a local Python backend**.

Suggested architecture:

### Front end
Browser UI

Possible implementation options:

- HTML/CSS/JavaScript
- React
- Another lightweight web framework

### Backend
Python

Suggested:

- FastAPI

The backend can run locally on the same computer.

The browser connects to:

```text
localhost
```

This provides the convenience of a web UI without requiring a public internet server.

## Why browser-first

Advantages:

- Easy to build and iterate with Codex
- No installer required during development
- Works across desktop platforms
- Easy to inspect and debug
- Can later become a PWA
- Can later be deployed remotely
- Same UI architecture can survive future hosting changes

## Future option

The local web app can later become:

- Hosted web app
- PWA
- Desktop wrapper
- Electron/Tauri-style desktop application
- Cloud-synced multi-device app

The initial version does **not** need to be a native desktop application.

---

# 24. AI Backend Architecture

Do **not** place a secret API key directly in browser JavaScript.

Recommended flow:

```text
Browser UI
    |
    v
Local Python / FastAPI backend
    |
    v
AI provider API
```

Possible AI provider:

- MiniMax
- Another inexpensive model provider
- OpenAI or other provider later

The backend should make AI calls only when useful.

## AI calls should be event-based

Good triggers:

- User asks a question
- User requests a reshuffle
- User requests harder/easier content
- End-of-session summary
- Weak-key drill generation
- New passage generation

Do not call AI for every keystroke.

Core typing must remain fast and local.

---

# 25. Offline Behavior

The core app should continue to work even if the AI API is unavailable.

Offline-capable features:

- Existing lessons
- Typing engine
- Keyboard visualization
- Hand animation
- Progress tracking
- Metrics
- Saved profiles
- Resume
- Basic recommendations
- Built-in drills

Online AI features can gracefully become unavailable without breaking training.

---

# 26. AI Content Caching

Generated content can be cached locally.

Benefits:

- Lower AI cost
- Faster lesson loading
- Offline reuse
- Less repetition
- Easier debugging

Each generated item can store:

- Curriculum stage
- Allowed keys
- Difficulty
- Topic
- Generation date
- Provider/model
- Whether completed
- User rating / skip state

---

# 27. First-Time User Flow

Suggested onboarding:

## Step 1 — Profile

- Name
- Optional PIN
- Coach preference
- Preferred mode

## Step 2 — Very short introduction

No long tutorial.

Explain:

- F and J bumps
- Home-row position
- Relaxed hands
- Look at the screen

## Step 3 — Animated hand placement

Show hands moving gently to home row.

## Step 4 — First micro-exercise

Very short.

No timer pressure.

## Step 5 — Positive observation

Example:

> Good. You’re learning position first. Speed comes later.

## Step 6 — Choose next action

- Continue
- Repeat
- See hand placement
- Ask the coach

---

# 28. Typical Daily Flow

1. Open app
2. Select profile / enter PIN
3. Resume card appears
4. Optional short warm-up
5. Main lesson
6. Contextual hand hints only when necessary
7. Adaptive mini-drill if a key is repeatedly missed
8. Finish session
9. Session summary
10. Coach gives one short observation
11. Suggested next training step
12. Progress saved automatically

---

# 29. AI Reshuffle Flow

Example:

1. User selects “Reshuffle lesson”
2. App sends:
   - Curriculum stage
   - Allowed keys
   - Weak keys
   - Difficulty
   - Desired length
3. AI generates a replacement
4. Backend validates constraints
5. New lesson appears
6. User can:
   - Start
   - Reshuffle again
   - Make harder
   - Make easier

The app should validate generated content before displaying it.

---

# 30. Weak-Key Coaching Flow

Example:

The system notices repeated problems with R.

1. Do not interrupt immediately
2. Track the pattern
3. After repeated misses:
   - Show subtle R-key hint
4. If needed:
   - Show finger movement animation
5. Later:
   - Insert a 20–30 second R-focused drill
6. At session end:
   - Mention the pattern neutrally
7. Next session:
   - Warm up R briefly
8. Once stable:
   - Stop treating R as weak

---

# 31. Challenge Flow

Challenge mode can be used by the learner or testers.

Possible challenge types:

- Beat your previous WPM by 1
- Maintain 95% accuracy for 60 seconds
- Keep rhythm stable for 45 seconds
- Type a paragraph without looking down
- Complete a weak-key drill
- Sustain a pace for 3 minutes

The app should focus on **personal benchmarks**, not global leaderboards.

---

# 32. Parent / Tester Flow

1. Open profile selector
2. Enter admin PIN
3. Choose Test Mode
4. Select simulated skill level
5. Jump directly to advanced lesson
6. Test:
   - AI generation
   - Coach modes
   - Hand hints
   - Metrics
   - Session summaries
7. Exit test mode
8. Main learner progress remains untouched

---

# 33. Product Tone

The product voice should be:

- Calm
- Smart
- Concise
- Slightly playful
- Modern
- Respectful
- Never patronizing
- Never school-teacher-ish
- Never hyperactive

Good:

> Rhythm is improving. Try one more round at the same pace.

Good:

> Your left hand is stable. Right index reaches are slowing you down.

Good:

> Want a clean run or a harder one?

Avoid:

> Amazing!!! You’re a SUPER TYPER!!! 🎉🎉🎉

Avoid:

> Oops! You made 8 mistakes!

Avoid:

> You failed the lesson.

---

# 34. Content Tone

Generated passages should feel age-appropriate and interesting.

Possible themes:

- Running
- Technology
- Gaming
- Internet culture
- Science
- Interesting facts
- Short fictional scenes
- Music culture without reproducing copyrighted lyrics
- Coding concepts
- Current-feeling but not forced slang
- Thought experiments
- Short stories
- Challenges

Avoid trying too hard to imitate Gen Z slang.

The learner should also be able to ask for a topic.

---

# 35. Accessibility / Comfort

Useful settings:

- Font size
- Contrast
- Keyboard size
- Reduce motion
- Disable hand animations
- Hide live metrics
- Disable coach
- Coach frequency
- Sound on/off
- Difficulty
- Session length

The app should work well without sound.

---

# 36. Data Privacy

For an initial local version:

- Keep profiles local
- Do not require an account
- Do not require email
- Do not collect analytics unless intentionally added
- Store only what the app needs
- Make AI requests narrow and task-specific
- Avoid sending unnecessary personal profile information to the AI provider

---

# 37. Suggested V1 Scope

The first useful version should remain focused.

## V1 — Must Have

- Local browser app
- Python/FastAPI backend
- Profile selector
- PIN
- Multiple profiles
- Beginner curriculum structure
- Typing exercise engine
- Visual keyboard
- Home-row tutorial
- Finger assignment system
- Simple hand/finger animation
- WPM
- Accuracy
- Key-level errors
- Basic rhythm metric
- Session save
- Resume
- Session summaries
- Coach with at least:
  - Silent
  - Calm
  - Competitive
- AI training console
- AI lesson reshuffle
- AI weak-key drill generation
- Test mode
- Save versioning
- Automatic migration support
- Local data persistence

## V1.5

- Key heat map
- Weekly trends
- Better cadence scoring
- Recovery metric
- More coach personalities
- AI-generated topic passages
- Export/import
- PWA installation

## V2

- More advanced curriculum
- Long-term performance insights
- Rich progress dashboard
- Offline generated-content cache
- More sophisticated hand animation
- Optional sync
- Desktop packaging
- Expanded AI coaching memory

---

# 38. Non-Goals for the First Version

Avoid expanding V1 into:

- Social network
- Public leaderboard
- Multiplayer competition
- Massive avatar customization
- Marketplace
- Paid subscription infrastructure
- Advertising
- Full AI agent platform
- Voice assistant
- Complex cloud account system
- Native mobile app
- Huge manually authored lesson library

The central value is:

> **Learn to type well, understand your own progress, and always have a useful next exercise.**

---

# 39. Core Product Differentiators

The app should stand apart from existing typing software through:

1. **Teen-appropriate visual design**
2. **No ads**
3. **No childish reward system**
4. **Calm error handling**
5. **Animated finger guidance**
6. **Adaptive curriculum**
7. **AI-generated fresh practice**
8. **AI as a training tool rather than a generic chatbot**
9. **Coach personality layer**
10. **Running/cadence metaphor**
11. **Rich typing metrics**
12. **Recovery and rhythm measurement**
13. **Long-term progress memory**
14. **Resume exactly where you left off**
15. **Local-first architecture**
16. **Test mode for advanced users**
17. **Save compatibility across app updates**

---

# 40. Product Concept in One Sentence

**A modern, local-first typing trainer that teaches correct technique, adapts to the learner, uses AI to keep practice fresh, and treats typing like personal performance training rather than a school exercise or arcade game.**

---

# 41. Working Product Principles

When future design decisions are unclear, use these principles:

1. **Technique before speed**
2. **Progress before scores**
3. **Personal bests before leaderboards**
4. **Adaptation before repetition**
5. **Hints before penalties**
6. **Calm before hype**
7. **Structure before AI improvisation**
8. **Local functionality before cloud dependency**
9. **User progress must survive every update**
10. **The app should feel intelligent without constantly talking**
11. **The coach should motivate without judging**
12. **Every metric should help answer: “What should I work on next?”**
