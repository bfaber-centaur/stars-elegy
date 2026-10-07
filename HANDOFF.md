# Handoff

## Objective

PG-003 is done: PG001 was run from the registered base to 2436 on the real
oracle, and Endeavor's population was read every year 2426–2436. Results are
in `docs/PARITY.md`, PG-003. No formula was inferred or implemented.

## State

- Branch: `claude/project-thread-35fu2u` (stars-elegy and apparatus).
- PR: the stars-elegy PR for this branch, and the apparatus PR adding
  `evidence/pg003/`.
- Oracle snapshots: `registered`, in the ephemeral VM's `~/.stars-oracle`
  only (built by the SessionStart hook).
- Universe / turn: run copy left at PG001 2436.
- Processes running: none.

## Verified

- `go test ./...` and `scripts/oracle/selftest` pass.
- 2426 read 295,800 again, repeating PG-002 on an independent run.
- 2427–2436 read 321,800 … 540,200; table and `.HST` SHA-256 in
  `docs/PARITY.md`, PG-003. Raw files in apparatus `evidence/pg003/`.
- 16/9 × (1 − x)² truncated is 0–4 units above observed growth at 10 of 11
  crowded points and matches at one; (1 − x) / 0.75 is far off.

## Unresolved

- `excessPop` for 2407–2436 has not been extracted from the preserved
  PG-003 `.HST` files. It is an existing observable: PG-001 decoded it with
  StarsAPI's `PartialPlanetBlock` and found it tracked the growth carry
  exactly (uncrowded case). Its meaning under crowding is open.
- The PG-001 decoding was done outside this repository; no decoder script
  is committed here.
- Whether a carry, factor rounding, or order-of-operations variant of the
  quadratic explains the 0–4 unit shortfall is untested.
- 2431's second message was not read.

## Next action

Owner-chosen next bounded task (2026-10-06): extract `excessPop` and
population from the PG-003 `.HST` files (apparatus `evidence/pg003/raw/`,
2407–2436) with the same StarsAPI decoder used for PG-001, and record the
values alongside the UI table in `docs/PARITY.md`, PG-003. No more Stars!
turns are needed. Check the decoder first against PG-001 2400–2407
(`excessPop` 0, 0, 50, 70, 90, 40, 60, 80) and against the UI populations.

## Do not do

- Do not implement or "fit" a crowding formula without a discriminating
  experiment chosen for it.
- Do not decode `.HST` bodies beyond the planet population / `excessPop`
  extraction above, and do not investigate header flags, `BACKUP/`/`.X1`
  semantics, or `.H1` contents without an explicit task.
- Do not run more oracle turns for crowding before `excessPop` is extracted.
- Do not commit screenshots, `STARS.INI`, snapshots, archives, the serial,
  or registered-copy game files to this repository.
- Do not rewrite the apparatus repository's archives or evidence.
