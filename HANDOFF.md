# Handoff

## Objective

Make the oracle reproducible in every cloud session without manual setup. The
repository side is done: `scripts/oracle/bootstrap` plus a SessionStart hook
rebuild a registered oracle from durable inputs. The next research mission,
planned experiment PG-002 (`docs/PARITY.md`), is still not run.

## State

- Branch: `claude/blissful-wozniak-k5958n`, restarted from `main` after PR #2
  merged.
- HEAD: the commit that added this file.
- PR: a new PR for the durable-setup change (see branch).
- Oracle snapshot: none durable. Each session rebuilds `registered` via
  `bootstrap` (about 9 s).
- Universe / turn: pristine `stars_games`, PG001 at turn 7 / 2407.
- Processes running: none.

## Verified

- `go test ./...` and `scripts/oracle/selftest` pass.
- Run by hand as `CLAUDE_CODE_REMOTE=true .claude/hooks/session-start.sh`,
  against a fresh `ORACLE_HOME`, with `STARS_SERIAL` set:
  - archives from a local directory: registered snapshot built, generated
    `wait-for` crops pixel-identical to hand-made ones;
  - the snapshot booted without a serial prompt; `turn PG001.M1` advanced
    turn 7 / 2407 → 8 / 2408;
  - archives cloned via `ORACLE_APPARATUS_GIT` (a local git repo): the
    snapshot was built;
  - a second run only resets;
  - with no inputs, the hook prints one line and exits 0.

## Unresolved

- The project owner still has to create the private apparatus repository
  (e.g. `bfaber-centaur/stars-oracle-apparatus`, holding the two archives)
  and make it reachable from sessions. Either add it as a second repository
  of the session or environment (cloned next to this one), or set
  `ORACLE_APPARATUS_GIT`.
- `STARS_SERIAL` is set in the environment settings but was not visible in
  the session that wrote this. Only new sessions pick it up.
- The hook has not yet been seen running at the start of a real new
  session, or cloning the real private repository.

## Next action

In a new cloud session, with the apparatus repository reachable, confirm the
SessionStart hook reported "Stars! oracle ready" (or read
`~/.stars-oracle/bootstrap.log`). Then record the result in `docs/ORACLE.md`,
Durable setup.

## Do not do

- Do not commit archives, crops, snapshots, `STARS.INI`, or the serial.
- Do not run PG-002 inside the durable-setup task; it is a separate mission.
