# Handoff

## Objective

PG-002 (first crowded turn) is done: one turn of PG001 from 2425 to 2426
was run on the real oracle and recorded in `docs/PARITY.md`. No formula was
inferred or implemented. The next bounded mission has not been assigned.

## State

- Branch: `re/population-crowding`
- HEAD: the commit that added this file (on top of `main` at `f232ae0`).
- PR: opened from this branch; see the branch on GitHub.
- Oracle snapshots: `registered` and `pg001-2425`, in the ephemeral VM's
  `~/.stars-oracle` only. Recreate with `docs/ORACLE.md` (archives from
  `bfaber-centaur/stars-oracle-apparatus`, serial from `STARS_SERIAL`).
- Universe / turn: run copy left at PG001 2426.
- Processes running: none.
- Evidence outside Git: `oracle-evidence/pg002/` in the project files
  folder (`.HST` for 2407–2426, `observations.jsonl`, UI screenshots).

## Verified

- `go test ./...` and `scripts/oracle/selftest` pass.
- Fresh registration from the apparatus repo + `STARS_SERIAL` worked; the
  2408 check read 53,500.
- 18 empty-order turns from 2407 reached 2425 with Endeavor at 270,400
  (UI), matching the PG-001 table.
- 2425 → 2426: Endeavor 270,400 → **295,800** (UI, one run). H0 (297,400),
  H1 (295,900) and H2 (296,700) as written are all rejected. Details and
  SHA-256 of the 2425/2426 `.HST`: `docs/PARITY.md`, PG-002.

## Unresolved

- The 2425 carry is inferred as 0, not binary-confirmed.
- One data point; H1 misses by one unit. Whether a variant (carry,
  rounding, order of operations) fits is untested.
- Whether registered-copy game files carry registration data is unknown,
  so the raw `.HST` files were kept out of this public repo. The owner may
  decide otherwise.

## Next action

None assigned. Wait for the owner to choose the next mission.

## Do not do

- Do not implement or "fit" a crowding formula from the single PG-002 point.
- Do not decrypt `.HST` bodies or investigate header flags, `BACKUP/`/`.X1`
  semantics, or `.H1` contents without an explicit task.
- Do not commit screenshots, `STARS.INI`, snapshots, archives, the serial,
  or registered-copy game files without the owner's say-so.
