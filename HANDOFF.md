# Handoff

## Objective

Make the oracle reproducible in every cloud session without manual setup.
Done on the repository side: `scripts/oracle/bootstrap` plus a SessionStart
hook rebuild a registered oracle from the private apparatus repository and
`STARS_SERIAL`. What remains is to see it happen at the start of a real new
session. Research experiment PG-002 (`docs/PARITY.md`) is still not run.

## State

- Branch: `claude/blissful-wozniak-k5958n` (PR #3, open).
- HEAD: the commit that added this file.
- Apparatus: private repo `bfaber-centaur/stars-oracle-apparatus` (`main`,
  `b6d8c38`), holding the two archives, `NOTES.txt` and `README.md`. The
  project owner is adding it to the cloud environment so sessions clone it
  to `/home/user/stars-oracle-apparatus`.
- Oracle snapshot: built per session by the hook; none durable.
- Universe / turn: pristine `stars_games`, PG001 at turn 7 / 2407.
- Processes running: none.

## Verified

- `go test ./...` and `scripts/oracle/selftest` pass.
- A fresh clone of the apparatus repo has archives with the same SHA-256 as
  the originally supplied ones.
- `CLAUDE_CODE_REMOTE=true .claude/hooks/session-start.sh`, with an empty
  `ORACLE_HOME` and the apparatus repo checked out next to this one (no
  `ORACLE_APPARATUS_*` variables): prints "Stars! oracle ready" and builds
  the `registered` snapshot.
- Earlier runs (`docs/ORACLE.md`, Durable setup): the bootstrapped snapshot
  boots without a serial prompt, `turn PG001.M1` advances turn 7 → 8, a
  rerun only resets, and missing inputs are reported without failing.

## Unresolved

- The hook has not yet been seen running at the start of a real new
  session. All tests ran it by hand.
- `STARS_SERIAL` was not visible in the session that wrote this; tests set
  it inside the test process.

## Next action

In a new cloud session (apparatus repo in the environment), check that
`~/.stars-oracle/bootstrap.log` ends with "bootstrap: done" or "already
done", and that `scripts/oracle/status` lists a `registered` snapshot.
Record the result in `docs/ORACLE.md`, Durable setup.

## Do not do

- Do not commit archives, crops, snapshots, `STARS.INI`, or the serial to
  stars-elegy.
- Do not rewrite or force-push the apparatus repository's archives; add new
  versions under new names.
- Do not run PG-002 as part of this task.
