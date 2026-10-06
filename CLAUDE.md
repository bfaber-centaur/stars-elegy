# Stars' Elegy

Stars' Elegy is a modern reimplementation of **Stars! J-RC3**.

The immediate objective is a deterministic, well-tested simulation engine whose behavior can be compared experimentally against the original game.

The original game is an oracle.

Our intuition is not.

## Core rule

**Never silently guess a Stars! mechanic.**

When behavior is unknown, preserve it as unknown until documentation, binary evidence, or controlled experiments establish it.

Prefer:

```text
hypothesis
→ discriminating experiment
→ observation
→ preserved evidence
→ inferred rule
→ regression test
```

over implementation-by-memory or implementation-by-plausibility.

## First steps

At the beginning of substantive work:

1. read this file;
2. read `docs/PARITY.md`;
3. inspect relevant existing code/tests;
4. run:

   ```bash
   go test ./...
   ```

Do not reopen established decisions without a concrete defect, contradiction, or new evidence.

## Evidence and parity

`docs/PARITY.md` is the durable record of Stars! J-RC3 behavioral knowledge.

Keep evidence levels explicit.

Useful categories include:

- `CONFIRMED`
- `MEASURED`
- `DOCUMENTED`
- `UNKNOWN`
- `LEGACY BUG`
- `INTENTIONALLY DIFFERENT`

Do not upgrade evidence status without evidence.

Distinguish:

- direct observation;
- binary/state evidence;
- interpretation;
- external documentation;
- hypothesis.

Raw observations and decoded original-game state outrank recollection or assumptions about what Stars!' designers probably intended.

## Experimental oracle

Cloud/reverse-engineering work may have access to external apparatus such as:

- StarsBox;
- DOSBox configuration;
- Windows 3.1;
- Stars! J-RC3;
- registration information;
- known-good oracle drives;
- existing test universes.

These are **experimental apparatus**, not Elegy source.

Exact paths may vary between environments. Discover them rather than hard-coding machine-specific assumptions.

Operational instructions for a working oracle belong in:

```text
docs/ORACLE.md
```

Reusable control scripts belong under something like:

```text
scripts/oracle/
```

## Proprietary material and secrets

Do not commit proprietary oracle material.

This includes, unless clearly established otherwise:

- Stars! binaries/assets;
- Windows binaries/assets;
- proprietary StarsBox payload contents;
- registration names;
- serial numbers;
- license keys.

Secrets must not appear in:

- source;
- documentation;
- committed fixtures;
- committed logs;
- issues;
- commits;
- PR descriptions.

Do not print credentials unnecessarily.

Do not fetch questionable copies of proprietary software merely to unblock an experiment.

Derived scripts, measurements, non-proprietary fixtures, tests, and documentation may be committed.

## Preserve oracle state

Known-good oracle drives and test universes are valuable experimental state.

Never mutate the only known-good copy.

Prefer:

```text
immutable supplied artifact
→ pristine base
→ disposable experimental copy
→ extracted observations
```

Reset-to-known-state should be cheap and reproducible.

## Scientific workflow

Reverse engineering should normally follow:

```text
candidate hypotheses
→ choose inputs where predictions differ
→ run original Stars!
→ preserve output/state
→ decode observation
→ update hypothesis
→ regression test
→ docs/PARITY.md
```

Prefer boundary cases and controlled experiments over large naturalistic games.

When possible:

- vary one factor at a time;
- formulate competing predictions before running the experiment;
- choose cases that distinguish those predictions;
- preserve raw outputs;
- record the exact J-RC3 context;
- separate observation from interpretation.

Contradictions are useful evidence.

Do not massage an experiment until it agrees with the current implementation.

## HST / binary evidence

Where decoding is established, `.HST` and related original-game files are authoritative evidence about game state.

Preserve raw bytes/fixtures when important to an inference.

Do not assign confident semantics to poorly understood fields merely because a name seems plausible.

Names inherited from StarsAPI or other reverse-engineering projects are prior art, not proof.

## Current population result

For the measured PG-001 case:

- population is stored in units of 100 colonists;
- the `.HST` field named `excessPop` by StarsAPI matches a persistent fractional growth remainder;
- for the measured uncrowded 100%-habitability / 10%-growth case, observed behavior is equivalent to:

```go
numerator := populationHundreds*growthPercent + growthCarry
growthHundreds := numerator / 100
growthCarry = numerator % 100
populationHundreds += growthHundreds
```

This behavior is binary-confirmed for that measured scenario.

Do **not** generalize it without evidence to:

- crowding;
- nontrivial habitability scaling;
- hostile-world deaths;
- migration;
- colonization;
- ownership changes;
- other population-changing mechanics.

Consult `docs/PARITY.md` for current evidence.

## Important population unknowns

Unless `docs/PARITY.md` has newer evidence, unresolved questions include:

- exact growth behavior above 25% capacity;
- crowding formula;
- order of operations among growth modifiers;
- fractional carry under additional modifiers;
- behavior at 100% capacity;
- overcrowding deaths;
- `excessPop` lifecycle across migration, colonization, ownership changes, hostile worlds, and other population changes.

Do not treat this list as more current than `docs/PARITY.md`.

## Engine architecture

Prefer a pure deterministic engine.

Conceptually:

```text
GameState
+ Orders
+ Ruleset
+ explicit RNG state where required
        ↓
TurnResult
```

Avoid dependencies on:

- UI state;
- wall-clock time;
- ambient filesystem state;
- hidden global mutable state;
- implicit randomness.

Do not mutate inputs unless an established API explicitly intends mutation.

Keep ruleset differences explicit.

J-RC3-faithful behavior and deliberately modernized/fixed behavior may eventually coexist, but do not silently fix legacy behavior inside the J-RC3 ruleset.

Separate authoritative simulation state from player-visible/intelligence state.

Prefer straightforward, data-oriented Go over speculative abstraction.

## Development workflow

Before substantive work:

```bash
go test ./...
```

After changing Go:

```bash
gofmt -w <changed-files>
go test ./...
```

Keep changes focused.

Do not perform unrelated refactors during reverse-engineering work.

When changing a mechanic:

1. identify the independent evidence;
2. preserve a fixture/measurement where practical;
3. add a focused regression test;
4. update `docs/PARITY.md`;
5. run the full test suite.

A test whose expected value comes only from Elegy's own implementation is not evidence of Stars! parity.

## Product architecture

Engine truth comes before UI parity.

Stars' Elegy does **not** need to reproduce the Windows 3.1 UI.

The engine should support multiple clients.

Current intended directions include:

- a fast keyboard-oriented TUI;
- a bespoke graphical desktop client.

Simulation logic must remain independent from either presentation layer.

Do not make major UI/product decisions opportunistically while doing parity work.

## Git workflow

For substantial work:

- use a dedicated branch;
- do not push directly to `main`;
- prefer one coherent reverse-engineering question or infrastructure task per branch/PR.

Useful branch naming patterns include:

```text
oracle/bootstrap
re/population-crowding
re/excess-pop-lifecycle
re/fuel-consumption
```

Before handing work back:

1. run relevant tests;
2. inspect the complete diff;
3. inspect staged files;
4. exclude secrets, proprietary artifacts, and generated junk;
5. commit intentional changes;
6. push the branch;
7. open/update a PR when appropriate.

Reverse-engineering PRs should make the scientific handoff clear:

- question;
- experiment;
- evidence;
- conclusion/confidence;
- implementation/test changes;
- remaining uncertainty.

## Durable handoffs

Important discoveries must not exist only in a Claude conversation.

Long-running work should leave useful state in some combination of:

- regression tests;
- non-proprietary fixtures;
- experiment scripts;
- `docs/PARITY.md`;
- `docs/ORACLE.md`;
- concise technical documentation.

A fresh worker should be able to determine:

- what is known;
- why we believe it;
- how it was measured;
- how to reproduce it;
- what remains unknown.

Preserve convergence. Revisit established conclusions only when new evidence gives a concrete reason.
