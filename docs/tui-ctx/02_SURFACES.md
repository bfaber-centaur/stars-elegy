# Surfaces to Explore

These are prompts, not a checklist. The task should spend the most energy on battle replay.

---

## A. Battle replay — primary surface

### What it should answer at a glance

- Who is fighting?
- Where are the important stacks?
- What is selected?
- What happened this tick / phase?
- What changed because of it?
- What is likely to happen next, if the player keeps playing?
- Can I jump backward and understand causality?

### Interesting regions to combine

A battle study might use some subset of:

1. **Battlefield**
   - coarse spatial grid;
   - compact stack glyphs;
   - selection marker;
   - range / target line;
   - wreck / destroyed marker;
   - movement breadcrumb.

2. **Selected stack inspector**
   - design;
   - count;
   - shields / armor / damage;
   - initiative or movement state if applicable;
   - target / battle plan;
   - recent changes.

3. **Timeline / phase strip**
   - deterministic tick number;
   - event markers;
   - ability to scrub;
   - compact indication of “where we are.”

4. **Event log**
   - terse causal lines;
   - enough numbers to audit what happened;
   - selected event linked back to actors on the board.

5. **Controls**
   - play / pause;
   - single-step;
   - previous/next interesting event;
   - speed;
   - inspect;
   - jump to destruction / first damage / retreat.

### Directions worth deliberately contrasting

Produce battle studies that disagree about at least these questions:

- Is the battlefield the hero, or is the event timeline the hero?
- Are ships represented spatially or primarily as ordered stacks?
- Is the log prose-first or ledger-first?
- Does the screen feel like a tactical plot, a debugger, or a sports replay?
- How much detail appears without selecting something?

Do not assume the final battle model already exists. Presentation concepts can be ahead of mechanics, but uncertain mechanics must not be described as settled facts.

---

## B. Turn report / message center

Try a screen where the new turn arrives as a dense but calm digest:

- battles;
- completed construction;
- research advances;
- scanner discoveries;
- warnings;
- colony changes;
- fleet arrivals;
- messages.

Interesting question: can a player understand “what changed while I was away” without opening ten modal windows?

---

## C. Planet inspector / production

Try a compact planet view with enough simultaneous information to make a real decision:

- population;
- habitability / environment;
- resources;
- factories / mines;
- minerals;
- production queue;
- research contribution;
- local fleets / starbase if relevant.

Interesting question: can the queue feel like an editable ledger rather than a modern card stack?

---

## D. Fleet inspector / waypoint planning

Possible ingredients:

- current position;
- composition;
- cargo / fuel;
- destination;
- waypoints;
- ETA / movement cost;
- orders;
- stale/uncertain enemy observations nearby.

Interesting question: can orders read like a compact flight plan?

---

## E. Research

Six fields invite a text-mode presentation.

Try:
- comparative bars;
- current allocation;
- current level;
- progress;
- estimated next advance if such an estimate is valid;
- recently unlocked items.

Interesting question: can the screen make tradeoffs legible without becoming six progress bars in boxes?

---

## F. Intel / scanner view

This is one place where the architecture matters conceptually: the UI sees **player knowledge**, which may be partial or stale.

Explore visual treatments for:
- known;
- observed this turn;
- stale;
- inferred / uncertain;
- unknown.

Interesting question: can uncertainty be represented naturally in a monospace grammar without turning the display into punctuation soup?

---

## G. Galaxy-map companion panel

Do **not** assume the galaxy map itself must be ASCII.

Instead, explore terminal-like companion panes around a modern/SVG map:
- selected object;
- overlays;
- fleet list;
- scan summary;
- next waypoint;
- message ticker.

A hybrid concept may be more valuable than an all-TUI galaxy.

---

## H. End-turn review

A preflight screen before committing the turn:

- planets with idle resources;
- fleets with no orders;
- risky fuel states;
- research allocation;
- unresolved messages;
- production completion;
- explicit “nothing suspicious here” sections kept quiet.

Interesting question: can this feel like a pilot's checklist rather than a nag screen?
