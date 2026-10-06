# Handoff

## Objective

Oracle bootstrap is complete: a headless Stars! J-RC3 oracle (Xvfb → DOSBox
→ Windows 3.1 → Stars!) that a fresh worker can set up, register, drive for
one turn, inspect from Linux, and reset. No game mechanic has been
investigated. The next bounded mission is the first crowded-growth
observation (PG-002), which is designed but not run.

## State

- Branch: `claude/blissful-wozniak-k5958n`
- HEAD: the commit that added this file (on top of `899f358`).
- PR: https://github.com/bfaber-centaur/stars-elegy/pull/2 (open). The
  first oracle commit was already merged to `main` via PR #3.
- Oracle snapshot: none in the repository. The `registered` snapshot lived
  in an ephemeral VM's `~/.stars-oracle`. Recreate it with the Registration
  procedure in `docs/ORACLE.md`; this needs the apparatus archives and the
  serial from the project owner.
- Universe / turn: pristine `stars_games`, PG001 at turn 7 / 2407.
- Processes running: none.

## Verified

- `go test ./...` and `scripts/oracle/selftest` pass.
- With the real apparatus, observed on 2026-10-06:
  - Windows 3.1 and Stars! boot unattended.
  - The serial is accepted via `scripts/oracle/register`.
  - PG001 loads from D:.
  - `scripts/oracle/turn PG001.M1` moves the `.HST`/`.M1` headers from turn
    7 / 2407 to turn 8 / 2408 (3 runs).
  - Endeavor's population read in the UI went 48,600 → 53,500 (2 runs),
    not the 51,100 that the halved-growth penalty predicts.
  - `reset` restores the starting files.
- Evidence levels and exact commands: `docs/ORACLE.md`. Re-measurement
  note: `docs/PARITY.md`, Sources.

## Unresolved

- "Normal registered behavior" is inferred from the accepted serial plus
  one matching growth value. The About dialog is inconclusive.
- Where the registration is stored is a hypothesis (likely `STARS.INI`).
- The `.HST` header flags byte varied across runs (`0xa0`, `0x80`, `0x20`).
  Its meaning is unknown.
- Population can only be read from the UI. Elegy decodes headers only.
- `MouseSpeed=0` in the run copy is assumed not to affect Stars!; untested.

## Next action

Run planned experiment PG-002 exactly as written in `docs/PARITY.md`
("Planned experiment — PG-002"), on a new branch `re/population-crowding`.
Record the 2426 population against the predictions written there, and
preserve the 2426 `.HST`.

## Do not do

- Do not decrypt `.HST` bodies or investigate header flags, `BACKUP/`/`.X1`
  semantics, or `.H1` contents as part of PG-002.
- Do not implement any crowding formula in the engine from a single data
  point.
- Do not commit screenshots, `STARS.INI`, snapshots, archives, or the serial.
