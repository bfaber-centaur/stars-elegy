# Stars' Elegy

This is the public **behavioral research / parity / oracle** workspace for Stars! J-RC3.

The canonical game implementation lives in `bfaber-centaur/elegy`. Private original-game apparatus and raw experiment evidence live in `bfaber-centaur/stars-oracle-apparatus`. Private binary-analysis work lives in `bfaber-centaur/stars-decomp`.

## Start here

Read what is relevant:

1. `HANDOFF.md` for the current frontier, if present
2. `docs/PARITY.md` for behavioral knowledge and open questions
3. `docs/ORACLE.md` when running the original game
4. relevant code, evidence, and recent commits

Then run:

```sh
go test ./...
```

If oracle tooling matters:

```sh
scripts/oracle/selftest
```

## Research style

The original game is the oracle. Prefer measured behavior over memory, intuition, or a plausible formula.

Do not silently guess mechanics.

A useful loop is:

```text
question
→ candidate explanations
→ discriminating experiment or existing evidence
→ observation
→ interpretation
→ durable record
```

Follow important clues within the current research question far enough to understand the result. Do not stop just because the next useful step was not named explicitly in the prompt.

Conversely, do not wander into a different research program merely because it is interesting.

Before declaring something unknown or unobservable, check:

- prior work in `docs/PARITY.md`
- preserved raw evidence
- existing project tools
- external analysis tools already used by the project, such as StarsAPI

Lack of a native decoder in this repository does not mean a quantity has never been decoded or cannot be inspected.

## Evidence

Keep observation separate from interpretation.

Useful statuses include:

- `CONFIRMED`
- `MEASURED`
- `DOCUMENTED`
- `UNKNOWN`
- `LEGACY BUG`
- `INTENTIONALLY DIFFERENT`

Do not generalize one or two observations into words such as “always”, “every”, or “deterministic”.

If new evidence contradicts prior work, preserve the contradiction and investigate it.

`docs/PARITY.md` is the canonical public record of behavioral knowledge. Put operational oracle knowledge in `docs/ORACLE.md`.

## Raw evidence and private material

Do not commit original Stars!/Windows binaries, registration credentials, or potentially registration-bearing raw oracle output to this public repository.

Raw experiment evidence belongs in the private `bfaber-centaur/stars-oracle-apparatus` repository, normally under:

```text
evidence/<experiment-id>/
```

Preserve enough provenance and hashes there to audit the public result later.

The serial may exist in the private cloud environment, but must not appear in source, docs, logs, PR text, or committed files.

Binary reverse-engineering artifacts belong in private `bfaber-centaur/stars-decomp`. Promote useful white-box discoveries here as behavioral or algorithmic claims, not raw disassembly/decompiler output.

## Repository boundary

This repository may contain:

- oracle control / recording / inspection tools
- parity experiments
- public documentation
- sanitized fixtures and tests supporting research claims

Product/engine implementation belongs in `bfaber-centaur/elegy`.

## Git and handoff

Use a branch/PR for substantial work.

Before handing work back:

```sh
go test ./...
git status
git diff
```

Run `scripts/oracle/selftest` when oracle tooling changed.

Inspect staged files for secrets, proprietary artifacts, screenshots, archives, and generated oracle state.

`HANDOFF.md` is a small rolling snapshot of the current frontier. Rewrite it from scratch when a real context handoff is useful; do not append history and do not checkpoint after every small result.

Before a handoff, move substantive discoveries into `PARITY.md`, `ORACLE.md`, tests, scripts, or private evidence as appropriate.

A handoff only needs:

```markdown
# Handoff

## Current question
...

## State
...

## What we know
...

## What still matters
...

## Best next move
...
```

Git history preserves old handoffs.

## Preserve convergence

Use repository artifacts as durable memory; conversation context is scratch space.

Do not reopen settled choices without a concrete defect, contradiction, or new evidence. But do pursue the evidence far enough to understand the current question before stopping.
