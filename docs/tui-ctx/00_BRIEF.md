# Stars! Elegy — TUI Concept Brief

## What this is

This is a visual-design exploration for **Stars! Elegy**, a reimplementation of *Stars! J-RC3*.

The project is engine-first and deterministic. The eventual product shell is expected to be Wails + Svelte, but some surfaces may deliberately use a terminal / text-mode visual language.

**We are not deciding that Stars! Elegy is a TUI.**

We are exploring whether TUI-like presentation can give parts of the game a distinctive, readable, information-dense character. A good concept may ultimately be:

- a real terminal interface;
- a TUI-style panel rendered inside the Wails application;
- a source of visual language for a non-terminal UI;
- or simply an interesting dead end.

The point of this task is to generate things worth looking at and thinking about.

## Primary target

The strongest candidate is the **battle replay**.

Battle replay should feel like a compact tactical instrument: positional, temporal, legible, and replayable. It should make a deterministic battle feel inspectable rather than merely animated.

Other surfaces are fair game, especially when they teach us something about the visual language:

- turn report / message center;
- fleet inspector;
- planet inspector;
- production queue;
- research overview;
- scanner / intel display;
- galaxy-map overlays;
- race / empire summary;
- ship design comparison;
- end-turn review.

Do not force all of these into one coherent terminal application.

## Product/architecture facts to respect

- Simulation logic must not depend on UI.
- UI should consume player-visible state, not unrestricted game truth.
- The engine is deterministic.
- Battle will eventually be a deterministic subsystem with explicit inputs and outputs.
- The likely final desktop shell is Wails + Svelte.
- Original Stars! file compatibility and exact UI parity are not immediate goals.
- Faithful mechanics matter more than faithful chrome.

## Exploration posture

Prefer **design studies** over implementation.

We want:
- artifacts, not essays;
- multiple directions, not premature convergence;
- concrete screens with believable data;
- small annotations explaining what each study is testing;
- useful disagreement between studies.

Avoid:
- generic cyberpunk terminal aesthetics;
- green-on-black CRT cosplay as the default;
- giant ASCII logos;
- fake command prompts everywhere;
- dense decoration that reduces information density;
- inventing game mechanics and presenting them as canon;
- solving frontend architecture unless a mock reveals a real architectural requirement.

If a mechanic is uncertain, use plausible mock data and label the mechanic as speculative rather than silently asserting it.

## Tone

Think less “retro hacker terminal” and more:

**1990s strategy game + scientific instrument + naval plotting table + modern terminal craft.**

The interface should feel like something a player can stare at for hours.
