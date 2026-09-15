# Task for Astra Med — Stars! Elegy TUI Design Studies, Pass 2

You are the visual concept designer for a second exploratory pass on **Stars! Elegy**.

Read the existing TUI studies and project context first.

This pass should build on the first corpus rather than restarting from scratch.

## Context from Pass 1

The first pass was successful. Several distinct interface roles emerged.

### Battle surfaces

**B1 / Sounding Table** was the strongest baseline for watching a battle:

* stable whole-battle spatial plot;
* muted dot-matrix field;
* persistent stack/transponder IDs such as `A03`, `B07`;
* selection and actor→target relationships drawn directly on the field;
* chronology subordinate to space.

The transponder-style IDs are especially strong and should remain part of the design language.

**B2 / Open Record** was strong as an expert inspector:

* event history;
* before/after numerical receipts;
* pinned watches;
* explicit unknown/unreported values;
* nearby relevant evidence without falsely asserting causality.

This is not the primary “watch the battle” screen. It is a deeper inspection surface.

**B4 / Track Score** was strong as a power-user profiler:

* stack lanes across event chronology;
* fire/receive relationships;
* quickly reveals participation, inactivity, repeated interactions, and battle rhythm.

Preserve it as a separate analytical mode rather than permanently attaching it to the replay.

**B5 / Action Desk** is mostly a component donor:

* stack register;
* persistent watch;
* `LAST RECORD`;
* explicit `unreported`.

Use these ideas to improve B2/B4 where appropriate.

**B6 / Witness Slip** is a strong compact pattern:

* small event receipt;
* immediate before/after;
* previous/current/next record neighborhood;
* good for report previews, drawers, and GUI side panels.

**B3 / Touchline** was mostly superseded by B1, but one visual detail was notably strong:

* clean centered faction matchup treatment such as `HOMEWARD / SABLE`.

### Most promising battle hybrid

The upper half of **H1 / Plot and Score** is currently the most promising replay composition:

* stable B1-style battlefield;
* compact B2-style event receipt;
* previous relevant event nearby;
* selected spatial object and event receiver clearly distinguished.

The full B4 score underneath made the screen too indecisive.

Treat the H1 upper-half arrangement as the main replay concept to iterate.

### Adjacent surfaces

**S1 / Turn Folio**

* strong turn-as-inbox concept;
* summary counts;
* selected-report preview;
* B6-style embedded receipts;
* important distinction between unread, actionable, dangerous, and changed.
* Bottom strip probably should not carry another analytical axis. It is plausible space for keybind hints, quiet status, ASCII ornament, or setting/flavor.

**S2 / Foundry Book**

* strongest “I could play the game with this UI” response.
* production ledger is highly successful.
* mineral/resource budget visible alongside queue.
* `THIS YEAR / AFTER THIS YEAR` is useful.
* unapplied reorder preview is excellent.
* general principle: preview consequential edits as counterfactual state before committing.

The top planet-information band needs better hierarchy:

* habitability/environment;
* economy/production;
* infrastructure;
* fleets/starbase/local operational context
  should not all read as one flat category.

**S3 / Route Card**

* useful waypoint ledger;
* fuel/cargo state carried through each destination;
* recorded vs planned vs estimated clearly separated;
* explicit diff from saved orders.

But it exposed the hardest TUI problem:

> How do we make the galaxy map itself work in text mode?

A local battle plot is bounded and schematic. A galaxy map must support:

* many stars;
* variable density;
* fleets;
* routes;
* ownership;
* uncertainty/stale intel;
* selection;
* navigation;
* scale/zoom;
* probably overlapping labels and dense regions.

Do not assume this problem has an easy answer.

**S4 / Observation Margin**

* another “I could play with this” success.
* stale observations remain useful without silently becoming current facts;
* `NOW`, `OLD`, and `UNKNOWN` are useful concepts;
* current unknowns are explicit;
* historical markers are distinct from inferred current positions;
* provenance/identity caution is valuable.

### GUI / TUI synthesis

H2 and H3 suggested that combining modern rendered maps with TUI-like textual instruments is promising, but static mocks reached their limits.

Do not spend much of this pass trying to solve GUI/TUI interaction through static ASCII composition.

Assume that question will eventually require a hands-on prototype.

However, compact TUI components intended to sit beside a native map are welcome.

---

# Objective

Create a second corpus of TUI/text-mode studies focused on four things:

1. iterate the likely battle replay core;
2. aggressively explore the unsolved galaxy-map problem;
3. refine the already-successful production and intel surfaces;
4. develop a more distinctive visual language using restrained color and ornament.

Do not implement frontend code.

Do not converge on a single “final UI.”

This is still exploratory design work.

---

# Design language updates

The first pass was monochrome and austere. That was useful, but this pass should explore more visual character.

## Color

Use restrained, semantic color annotations in your mocks.

Because markdown code fences cannot reliably render color, annotate intended color using concise labels or a small palette key.

Examples:

* `[OWN:cyan]`
* `[FOE:amber]`
* `[SEL:white/blue]`
* `[OLD:dim]`
* `[LOSS:red]`

Do not make every value colorful.

Color should primarily communicate:

* faction/ownership;
* selection/focus;
* changed values;
* danger/loss;
* stale/uncertain knowledge;
* draft/uncommitted state.

Every study must still be understandable in monochrome.

Avoid generic green-on-black hacker aesthetics.

## Ornament

Explore modest ASCII ornament and environmental flavor.

Good homes:

* margins;
* headers;
* footer/dead space;
* section separators;
* subtle map texture;
* turn-report ambience.

Do not obscure data.

Do not decorate every box.

The desired feeling is somewhere among:

* 1990s strategy game;
* naval plotting table;
* scientific instrument;
* observatory console;
* modern terminal craft.

Not cyberpunk terminal cosplay.

## Density

Favor compact, legible information.

Aligned numbers, stable regions, small receipts, terse labels, and meaningful whitespace are preferable to dashboard cards.

---

# Round 1 — Replay-core iteration

Create **five battle replay studies** based on the successful H1 upper-half concept.

All five should preserve:

* a stable spatial battlefield as the primary object;
* transponder-style stack IDs;
* a compact event receipt;
* some nearby context for the selected event;
* a clear distinction between spatial selection and event actor/receiver where necessary.

Deliberately vary:

* battlefield-to-receipt width ratio;
* receipt placement: side, bottom, floating inset, narrow margin, etc.;
* chronology placement;
* information density;
* how actor→target fire is rendered;
* selection syntax;
* color treatment;
* ornament;
* whether the receipt emphasizes prose, numeric diff, or both.

Do **not** permanently embed the full B4 score in these studies.

It may appear as an affordance such as:

`[Analyze score]`

or:

`F4 SCORE`

but B4 remains a separate expert surface.

### Specific design questions

Explore several alternatives for the firing relationship currently shown as something like:

`[A03]══════════════B07`

Possible dimensions:

* beam-like vs neutral connector;
* arrow vs line;
* transient overlay vs persistent mark;
* color vs glyph;
* multiple simultaneous interactions;
* overlapping connections.

Avoid implying exact weapon range unless the underlying display actually represents it.

Also experiment with the clean centered matchup treatment:

`HOMEWARD / SABLE`

without reintroducing misleading raw “force score” totals.

For each study:

1. give it a short name;
2. render a complete mock;
3. give at most five bullets:

   * what changed;
   * what it tests;
   * strongest feature;
   * biggest risk;
   * one thing worth stealing independently.

---

# Round 2 — HIC SVNT DRACONES: galaxy-map divergence

Create **six radically different full-TUI galaxy-map studies**.

This is the most important divergent-design task in this pass.

Do not produce six cosmetic variants of one map.

Assume this may be genuinely difficult.

We want to discover failure modes as much as successes.

Each study should show the same small fictional galaxy fixture so they can be compared.

Include approximately:

* 20–30 stars;
* at least three ownership states;
* several own fleets;
* at least two stale enemy contacts;
* one selected planet;
* one selected fleet;
* one multi-waypoint route;
* one dense cluster;
* one sparse outer region;
* at least one current unknown;
* at least one planet label collision or other realistic density problem.

Across the six, deliberately vary the core representation.

Possible directions include, but are not limited to:

* literal coordinate field;
* coarse sector grid;
* zoomed local view + strategic minimap;
* topology/network representation rather than metric space;
* label-forward map;
* glyph-forward map;
* scrolling viewport;
* layered map with aggressive filtering;
* focus+context / fisheye treatment;
* hex-ish or cell-based abstraction;
* star list spatially linked by route/neighbor relationships;
* something stranger.

At least one design should be intentionally ambitious.

At least one should prioritize information density over spatial fidelity.

At least one should prioritize spatial orientation over labels.

At least one should attempt a usable route-editing interaction.

At least one should show how stale intel and unknown positions coexist with current map objects.

### Required map questions

Each study must confront:

* how selection works;
* how routes are drawn;
* how dense labels are handled;
* how stale contacts appear;
* how ownership is represented;
* how the player moves/scrolls/zooms;
* what happens when the galaxy is larger than one screen.

Do not hand-wave these away in prose after the mock.

The mock itself should demonstrate the intended answer.

If a design fails in an interesting way, say so.

Failure is useful here.

---

# Round 3 — Refine playable surfaces

Create **two variants of S2 / Foundry Book** and **two variants of S4 / Observation Margin**.

These should be refinements, not reinventions.

## S2 refinements

Preserve:

* production ledger;
* mineral/resource budget;
* current-year consequences;
* unapplied counterfactual reorder preview.

Focus experimentation on:

* information hierarchy in the planet-summary band;
* grouping environment/habitability separately from economy and infrastructure;
* fleet/starbase context;
* compact semantic color;
* small amounts of ornament;
* how a draft/uncommitted queue looks distinct from committed state.

One version should be comfortable at ~120 columns.

One should test a narrower inset/pane.

## S4 refinements

Preserve:

* old observations without treating them as current;
* explicit unknowns;
* historical position navigation;
* provenance/identity caution.

Experiment with:

* compressing repeated `observed 2441` language;
* age/staleness indicators;
* semantic color;
* glyph vocabulary;
* contact list + detail relationship;
* map-companion width.

One version should remain extremely explicit.

One should test how far the interface can compress after the player understands the vocabulary.

---

# Round 4 — Small reusable components

Create a sheet of **eight small TUI components** that could be embedded in either a full TUI or a modern GUI.

These are not full screens.

Examples:

* battle witness slip;
* production change receipt;
* waypoint leg receipt;
* stale-contact badge;
* selected fleet header;
* turn-summary strip;
* unapplied-draft indicator;
* small watch/pin panel.

Each should fit roughly within 20–50 columns and 3–10 lines.

Treat these as a visual component vocabulary.

Use the same semantic conventions across them.

---

# Final synthesis

End with a short design memo.

Do not choose a single winner.

Instead, record:

## Strong foundations

Which concepts now feel genuinely playable?

## Open dragons

Which design problems remain unresolved?

Galaxy-map representation should probably remain here unless the studies produce an unusually convincing answer.

## Emerging visual grammar

Summarize recurring choices such as:

* transponder IDs;
* semantic color;
* explicit stale/unknown knowledge;
* draft vs committed state;
* before/after receipts;
* stable spatial frames;
* quiet ornament in margins;
* keyboard hints in low-value space.

## Prototype-first questions

List anything that static mocks can no longer answer honestly.

GUI/TUI synthesis is likely one of them.

Interaction-heavy map behavior may be another.

---

# Working method

Work autonomously.

Do not ask for routine clarification.

Use reasonable fictional data consistently.

Do not spend time on architecture or implementation.

Do not write frontend code.

Do not explain every design decision before producing artifacts.

Produce the mocks first and annotate them briefly afterward.

Prefer concrete visual experiments over prose.

Do not converge too quickly.

The goal remains:

> stuff to look at and wonder about.

And for the galaxy-map studies in particular:

> HIC SVNT DRACONES.
