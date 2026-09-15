# Task for Astra Med — Stars! Elegy TUI Design Studies

You are the visual concept designer for an exploratory pass on **Stars! Elegy**.

Read the other context files first.

## Objective

Create a small corpus of **TUI / text-mode design studies** that the project owner can browse and react to.

This is intentionally speculative design work.

Do not implement frontend code unless a later instruction explicitly asks for it. Do not spend time designing architecture. Your main output is visual mockups.

## Working method

Work autonomously.

Do not ask for routine clarification. Make reasonable choices, record them briefly, and keep producing artifacts.

Do not converge too quickly. We want different answers to the same design problem.

### Round 1 — battle divergence

Create **six battle-replay mocks**.

Each must be a genuinely different composition, not the same layout with renamed boxes.

Across the six, deliberately vary:

- spatial battlefield vs. event/timeline emphasis;
- horizontal vs. vertical chronology;
- sparse vs. dense default information;
- debugger / tactical plot / sports replay / operations-console feel;
- text-heavy vs. glyph-heavy representation.

For each study:
1. give it a short name;
2. render a complete mock in a fenced text block;
3. add at most 5 bullets:
   - what it is testing;
   - what seems strong;
   - what seems risky;
   - one element worth stealing even if the concept is rejected.

Use believable mock data. Do not present speculative combat mechanics as established canon.

### Round 2 — adjacent surfaces

Create **one strong study each** for four of the following:

- turn report;
- planet + production;
- fleet + waypoint planning;
- research;
- intel/scanner;
- galaxy-map companion panel;
- end-turn review.

Choose the four that best reveal whether the battle language generalizes.

### Round 3 — hybridization

After seeing your own studies, create **three hybrid concepts**.

Each hybrid should explicitly steal the strongest pieces from multiple earlier studies.

Do not pick a winner. The goal is to leave us with a few interesting attractors.

## Output structure

Create a folder:

`design/tui-studies/`

with:

```text
README.md
battle/
  01-*.md
  02-*.md
  03-*.md
  04-*.md
  05-*.md
  06-*.md
surfaces/
  01-*.md
  02-*.md
  03-*.md
  04-*.md
hybrids/
  01-*.md
  02-*.md
  03-*.md
```

`README.md` should be a compact gallery/index:
- one-line description of each study;
- the major axes explored;
- a short “things that kept working” section;
- a short “open design questions” section.

## Mock constraints

Default canvas: approximately **120×40 characters**.

You may break this when the concept benefits from a narrower embedded panel or an 80×24 compression test.

Mocks should:
- be legible as plain text;
- use Unicode box drawing if useful;
- remain understandable without color;
- show enough believable data to test hierarchy;
- include key hints only where useful;
- avoid enormous headings and decorative ASCII art.

## Important guardrails

- This is not a request to recreate the original Stars! UI.
- This is not a request to redesign game mechanics.
- This is not a request to make a generic cyberpunk terminal.
- This is not a request to make every future Stars! Elegy screen a TUI.
- Battle replay is the primary surface.
- Hybrid TUI-in-Wails concepts are explicitly encouraged.
- Treat uncertain mechanics as uncertain.
- Prefer a striking, inspectable artifact over a long design essay.

When you have completed the corpus, stop. Leave the owner with artifacts to react to rather than a recommendation to implement one.
