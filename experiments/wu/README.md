# WU — waypoint upkeep and patrol target choice

Oracle batch for `docs/ORDERS.md` "Waypoint upkeep and the remaining tasks"
(coverage-audit gap 3) and the direct measurement of **patrol target choice**.

Every scenario is built with `tools/fleetlab/combatlab build` on the
two-player Combat Lab base and run with `tools/fleetlab/pinned-turn` (one host
year, DOSBox `cycles=fixed 20000`, `stars.exe -g`). Nothing here needs a
crafted order file or the registered serial — the starts edit host state
directly (fleet waypoints and the repeat flag, planet routes, patrol ranges,
player relations). Raw run output is registered-copy evidence and lives in the
private `stars-oracle-apparatus` repository under `evidence/wu/`, not here.

## Reproduce

```sh
python3 experiments/wu/gen.py OUT                      # writes the waypoint-upkeep specs
base=…/stars-oracle-apparatus/evidence/cb/base2400
tools/fleetlab/combatlab build "$base/CB.HST" OUT/wuA.spec OUT/wuA.HST
tools/fleetlab/pinned-turn OUT/wuA.HST "$base" RUN/wuA 20000 CB
python3 experiments/wu/check.py RUN/wuA                # summarise before/after
```

The patrol distance/selection/warp starts use a patrol fleet re-designed with a
long-range scanner (so enemies are visible well past the engage radius) and
player relations set to war; they were written directly (see the private
evidence README for the exact specs and the per-run notes).

## CombatLab directives added for this batch

- `fleet … repeat` — set the fleet's repeat-orders flag.
- `task route` — waypoint task 8 (follow the planet's route).
- `task patrol RANGE` — waypoint task 7 (patrol within RANGE).
- `route N DEST` — set planet N's route destination to planet DEST.

(`relation P Q REL` already existed.)

## What was measured

Waypoint upkeep (all CONFIRMED):

- **Repeat off** drops the reached waypoint; **repeat on** moves it to the end
  (cycle).
- Reaching the **last** waypoint with nothing left idles the fleet and sends
  the completion message.
- A waypoint targeting a **live** fleet tracks its moving position; a waypoint
  targeting a **gone** fleet clears to a plain go-to at the last position (not
  dropped).
- The **route** task re-dispatches an owned fleet to the planet's route
  destination at the ideal warp (measured warp 6 over a ~161 ly hop).
- **Transfer fleet** is refused to an enemy recipient and when carrying
  colonists; an empty fleet to a willing non-enemy transfers.

Patrol target choice (CONFIRMED):

- The patrol fleet intercepts the **nearest** enemy fleet within an engage
  radius of about **50 ly** (50 engaged, 55 not) — a fixed radius, not the
  scanner range (unchanged with a 300 ly scanner) nor the patrol range word.
- Ties among equidistant enemies go to the **lowest-numbered / first** fleet,
  not the strongest.
- Intercept **warp = min(10, range / 5)** (range 20 → warp 4, 40 → 8, 90 and
  250 → 10).

The repeat fall-backs (`wuFALLBACK`) and the follower chain/cycle linkage
(`wuFOLLOW`) have since been run and are CONFIRMED (folded into `docs/ORDERS.md`;
raw evidence in private `stars-oracle-apparatus` `evidence/wu/`).

The **computer-player transfer refusal** is now CONFIRMED. It runs on the
AI-player base (`stars-oracle-apparatus` `evidence/ai/ai01`) built with the
`keepfleets-ordered` CombatLab directive, which preserves the base's own
fleets (all seven players') and adds the gift fleet in owner/id order. A non-colonist
fleet gifted by the human to an expert computer is refused and keeps its owner,
even with the computer's stored relation to the giver forced neutral both ways
(the computer is hostile when the gift is evaluated, so the gift fails the
recipient-relation check — the same refusal as an enemy human, not a separate
computer-only path; a live computer is not the vacant-slot case). See
`docs/ORDERS.md` "Transfer fleet".

Earlier diagnosis (recorded for the tooling): a plain full-replacement rewrite
of this 7-player registered base left the host unable to advance, because the
added fleet was appended out of owner/id order and desynced a player's fleet
group from its fleet count; `keepfleets-ordered` merges base and added fleets
and emits them in owner/id order, which the host accepts. (It is distinct from
the Objects lane's `keepfleets`, which keeps base fleets but forbids adding
new ones.)

Still open (see `docs/ORDERS.md` Open experiments, WU prefix): patrol
no-repeat, captured-target tracking, and the route stargate case.
