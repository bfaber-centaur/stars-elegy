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

## Scope discipline

Work on **one bounded mission at a time**.

Do not continue into an adjacent task merely because it is interesting, useful, or newly visible.

When the current mission is complete:

1. make the result durable;
2. update `HANDOFF.md`;
3. test and commit;
4. stop and hand back.

Do not start the next research question unless it was part of the assigned mission.

In particular, reverse-engineering work often reveals tempting adjacent questions. Record them under `UNRESOLVED` or in the appropriate canonical document, but do not pursue them without an explicit new task.

## First steps

At the beginning of substantive work:

1. read this file completely;
2. read `HANDOFF.md` if it exists;
3. read `docs/PARITY.md`;
4. read `docs/ORACLE.md` when oracle work is relevant;
5. inspect relevant existing code/tests;
6. inspect recent commits/diff for the active branch;
7. run:

   ```bash
   go test ./...
   ```

If oracle tooling is relevant, also run:

```bash
scripts/oracle/selftest
```

Verify important handoff claims against repository state rather than assuming the prose is correct.

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

Do not generalize beyond the observed cases without evidence.

If two observations conflict, preserve the contradiction and resolve it before promoting either into a general rule.

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

Reusable control scripts belong under:

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
- PR descriptions;
- `HANDOFF.md`.

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

## Preserving raw experiment evidence

Raw experiment state and evidence go in the private repository `bfaber-centaur/stars-oracle-apparatus`, never in this public repository and never only in project files or an ephemeral VM.

This includes `.HST` and other game files written by the oracle, screenshots, recorder logs (such as `observations.jsonl`), and manifests.

Use one directory per experiment:

```text
evidence/<experiment-id>/
├── README.md         provenance: experiment, date, J-RC3 version, source universe,
│                     start/result observations, public Elegy PR/commit, procedure
├── manifest.sha256   SHA-256 of every preserved file
├── raw/              game files and recorder logs
└── screenshots/      UI captures
```

Follow the precedent at `evidence/pg002/` on the apparatus repository's `main`.

Commit evidence on a branch, open a PR in the apparatus repository, and link it from the Elegy PR. Never rewrite existing evidence; add a new experiment directory instead.

This repository records only derived results: observations and conclusions in `docs/PARITY.md`, non-proprietary fixtures and tests, and a pointer to the evidence directory.

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

A repeated observation is evidence for that repeated case; it is not automatically evidence for words such as "always", "every", or "deterministic".

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
4. exclude secrets, proprietary artifacts, screenshots, archives, and generated junk unless explicitly intended;
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

## Context is scratch; Git is memory

Do not rely on conversation context, hidden summaries, or compaction to preserve important project state.

Anything consequential must be promoted into a durable artifact before context is compacted, reset, or handed to another worker.

Canonical destinations:

- Stars! behavioral knowledge → `docs/PARITY.md`
- oracle operation / apparatus knowledge → `docs/ORACLE.md`
- reproducible behavior → tests / fixtures / scripts
- raw experiment evidence → `evidence/<experiment-id>/` in the private apparatus repository
- architectural decisions → appropriate project docs
- current frontier only → `HANDOFF.md`

Never say or assume "the context summary will remember this."

Before compaction or handoff, ask:

> If the next worker saw only the repository, would anything important be lost?

If yes, make it durable first.

## Handoff ritual

Checkpoint and hand off when any of these is true:

- roughly half of the available context has been consumed;
- you are about to begin a substantially different subtask;
- you are about to compact/reset context;
- the environment restarted or behaved unexpectedly;
- you reached a useful experimental milestone;
- you are about to do risky or difficult-to-reproduce work;
- the assigned mission is complete;
- you are preparing to stop or hand work to another worker.

Do not wait until context is nearly exhausted.

### 1. Stop expanding scope

Finish or safely suspend the current smallest unit of work.

Do not begin another adjacent investigation during the checkpoint.

### 2. Promote durable knowledge

Move important results into their canonical locations before writing the handoff.

The handoff is not a substitute for:

- `docs/PARITY.md`
- `docs/ORACLE.md`
- tests
- fixtures
- scripts
- architectural documentation

### 3. Rewrite `HANDOFF.md` from scratch

`HANDOFF.md` is a **rolling snapshot of the current frontier**.

**Do not append to it. Replace its contents at every handoff.**

Git history preserves previous handoffs. The current file should contain only what a fresh worker needs now.

Use this shape:

```markdown
# Handoff

## Objective

One short paragraph describing the current bounded task.

## State

- Branch:
- HEAD:
- PR:
- Oracle snapshot:
- Universe / turn:
- Processes running:

## Verified

- Facts actually demonstrated.
- Commands/tests that demonstrate them.

## Unresolved

- Current uncertainties or contradictions.
- Failed approaches only when they materially affect the next worker.

## Next action

Exactly one concrete next step.

## Do not do

- Tempting adjacent work explicitly outside the current mission.
```

Keep it concise.

Do not turn `HANDOFF.md` into:

- a diary;
- a complete session transcript;
- a backlog;
- a research roadmap;
- a second copy of canonical docs.

If something is historical but no longer affects the next action, omit it.

### 4. Verify repository state

Run applicable checks, normally:

```bash
go test ./...
scripts/oracle/selftest
git status
git diff
```

Inspect staged files for:

- credentials;
- `serial.txt`;
- Stars!/Windows binaries;
- proprietary apparatus;
- tar/zip archives;
- screenshots;
- generated oracle state;
- accidental logs.

Resolve factual contradictions before handoff where practical.

### 5. Commit and push

Prefer handing off a clean committed branch over leaving important uncommitted state in an ephemeral VM.

Update/open the PR when appropriate.

### 6. Stop

Once the checkpoint is committed and pushed, stop.

Do not use remaining context as an excuse to start the next task.

The next worker should begin from the durable repository state.

## Fresh-worker ritual

A fresh worker should:

1. read `CLAUDE.md`;
2. read the current `HANDOFF.md`;
3. read relevant canonical docs;
4. inspect branch/HEAD/diff;
5. verify the most important handoff claims;
6. execute the single `Next action`.

If `HANDOFF.md` disagrees with canonical docs or executable evidence, the canonical docs/evidence win and `HANDOFF.md` should be corrected.

## Durable handoffs

Important discoveries must not exist only in a Claude conversation.

A fresh worker should be able to determine:

- what is known;
- why we believe it;
- how it was measured;
- how to reproduce it;
- what remains unknown;
- exactly what to do next.

Preserve convergence. Revisit established conclusions only when new evidence gives a concrete reason.
