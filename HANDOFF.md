# Handoff

## Objective

Close the one open item left on `main`: confirm that the `bootstrap`
SessionStart hook builds the oracle at the start of a real new cloud
session. Done and recorded in `docs/ORACLE.md`, Durable setup. No research
mission is assigned.

## State

- Branch: `claude/project-thread-35fu2u`
- HEAD: the commit recording the hook observation, on top of `main` 45bf908.
- PR: see the branch's PR on `bfaber-centaur/stars-elegy`.
- Oracle snapshots: `registered`, in the ephemeral VM's `~/.stars-oracle`
  only, built by the hook at session start.
- Universe / turn: run copy reset to `registered` (PG001 2407).
- Processes running: none.
- Raw evidence: none new. PG-002 evidence is at `evidence/pg002/` on the
  apparatus repository's `main`.

## Verified

- The hook ran before the session's first command; `bootstrap.log` ends
  with "bootstrap: done" (details in `docs/ORACLE.md`).
- `go test ./...` and `scripts/oracle/selftest` pass.
- From `registered`, `scripts/oracle/turn PG001.M1` went 7 / 2407 →
  8 / 2408 with no serial prompt.

## Unresolved

- PG-002 is one data point: the 2425 carry is inferred as 0, not
  binary-confirmed, and H1 misses by one unit (`docs/PARITY.md`, PG-002).
- Whether registered-copy game files carry registration data is unknown,
  so raw `.HST` stays in the private apparatus repo.

## Next action

None assigned. Wait for the owner to choose the next research mission.

## Do not do

- Do not implement or "fit" a crowding formula from the single PG-002 point.
- Do not decrypt `.HST` bodies or investigate header flags, `BACKUP/`/`.X1`
  semantics, or `.H1` contents without an explicit task.
- Do not commit screenshots, `STARS.INI`, snapshots, archives, the serial,
  or registered-copy game files.
- Do not rewrite or force-push the apparatus repository's archives or evidence.
