# A waypoint aimed at another player's fleet (WF-01..WF-03)

Shrinks the RG-001 mismatch on waypoints aimed at another player's fleet
(`docs/PARITY.md`, "Representative game (RG-001)"). In RG-001 year 5,
player 2's fleet 14 and player 5's fleet 33 got waypoint 1 aimed at a fleet
of player 1. The host file after the year still named the fleet, with the
fleet's end-of-year position, and year 6 kept tracking it. `ORDERS.md`
says the **owner's file** saves such a waypoint as deep space
(BINARY-ONLY, WU-A); Elegy also rewrites its game state (its W5
assumption).

Combat Lab base (game CB), `gen.py OUTDIR`. Unarmed Scouts in deep space.
Player 0's fleet 0 has waypoint 1 aimed at player 1's fleet 0 (100 ly
east), which flies south at warp 5. Player 0's fleet 1 has waypoint 1
aimed at its own fleet 2 (control), which flies south-east at warp 5.
`wf-enemy` sets both relations to enemy, `wf-friend` to friend. Two years:
year 2 runs on year 1's host file. Pinned at cycles 20000. Raw evidence:
stars-oracle-apparatus `evidence/wf/`.

## Predictions (committed before the runs)

- **WF-01 (host file).** After each year, player 0's fleet 0 still has a
  waypoint aimed at player 1's fleet 0 (target type fleet), at that
  fleet's end-of-year position. The same for the own-fleet control. Both
  relations.
- **WF-02 (owner's file).** In player 0's `.M` file after each year, the
  waypoint aimed at player 1's fleet is a deep-space waypoint at the same
  position. The own-fleet waypoint is still a fleet target.
- **WF-03 (year 2).** In year 2 fleet 0 moves toward player 1's fleet 0's
  position at the start of year 2 and the waypoint again ends at its
  end-of-year position: the host file's fleet target is used again, not a
  plain position.

## Follow-ups (committed before their own runs)

Added after the coordinator's question on the RG-001 diff: what happens
when the target fleet is destroyed or out of sight. One year each, pinned
at cycles 20000.

- **WF-04 `wf-gone`.** Player 1's fleet 0 is scrapped in deep space at
  waypoint 0 (step 2, before movement), so player 0's fleet 0 aims at a
  fleet that is gone. Prediction (`ORDERS.md` "Target gone", CONFIRMED for
  a fleet id that did not exist): the waypoint becomes deep space at
  (1200,1230), fleet 0 flies 25 ly toward it, and nothing names player 1's
  fleet 0 after the year. The own-fleet control is unchanged from WF-01.
- **WF-05 `wf-unseen`.** Player 1's fleet 0 starts 150 ly from player 0's
  only fleet and flies away; no scanner of player 0's reaches it. Open,
  two candidates:
  - **track:** the host file keeps the fleet target and its end-of-year
    position (as in WF-01), and only the owner's file shows deep space;
  - **lose:** the target is turned into deep space at the last position
    player 0 saw (its start) in the host file too, with a lost-target
    message (0x28–0x2a) in player 0's `.M` file.
  Either way player 0's fleet 0 is recorded where it ends.

## Results

One pinned stream (cycles 20000). Year 2 for `wf-enemy` and `wf-friend`
ran on year 1's host file.

| case | player 0's fleet 0, waypoint 1, host file | same waypoint in player 0's `.M1` | message to player 0 |
|---|---|---|---|
| `wf-enemy` year 1 | fleet 1/0 at (1200,1255), its end position | fleet 1/0 at (1200,1255) | none |
| `wf-enemy` year 2 | fleet 1/0 at (1200,1280) | fleet 1/0 at (1200,1280) | none |
| `wf-friend` years 1, 2 | as `wf-enemy` | as `wf-enemy` | none |
| `wf-gone` | deep space at (1200,1230) | deep space at (1200,1230) | 0x028 (fleet 0, target 1/0) |
| `wf-unseen` | deep space at (1210,1323) | deep space at (1210,1323) | 0x02a (fleet 0) |

Player 0's own-fleet waypoint (fleet 1 → fleet 2) stayed a fleet target
at fleet 2's end position in every case.

- **WF-01 held, MEASURED:** while player 0 sees the target, the host file
  keeps a waypoint aimed at another player's fleet as a fleet target,
  with the target's end-of-year position, for an enemy and for a friend.
  This is the RG-001 year 5 observation.
- **WF-02 failed:** the owner's `.M1` also kept the fleet target while the
  target was seen (player 1's fleet was in player 0's view in both
  years). The `ORDERS.md` claim that the owner's file always saves it as
  deep space (WU-A) does not hold in this form.
- **WF-03:** year 2 kept chasing the fleet target. In both years fleet 0
  moved 25 ly toward the target's **end-of-year** position, as a chaser
  (it moves after the target, `KERNEL.md` "Chasing another fleet"), not
  toward its start-of-year position as written in the prediction.
- **WF-04 held:** a target gone before movement (scrapped) leaves deep
  space at its last position, (1200,1230), in both files, with 0x028
  naming fleet 0 and the target. Fleet 0 flew 25 ly toward that point.
- **WF-05: neither candidate.** For a target no scanner of player 0's
  saw, both files hold deep space at the target's **actual end-of-year
  position** (1210,1323), not the last position player 0 saw, with
  0x02a. So "lose", but at the current position.

So the rewrite to deep space (Elegy's W5) happens only when the target is
gone or out of the owner's sight, and then in the host file too.

## WK-1: a waypoint aimed at a fleet destroyed in battle

Question (coordinator, from the RG-003 ledger): in RG-003 year 8, five of
player 1's fleets (81, 82, 84, 86 and 91) had waypoint 1 aimed at player
5's fleet 71. That fleet flew onto planet 94 and died in the battle there.
After the year each waypoint named planet 94. Year 7's fleet 5/45 did the
same with planet 83. Elegy kept the fleet target.

Predictions: `WK1-PREDICTION.md`, pushed in 30ebc36. The activity API
shows the push at 2026-10-13T06:02:20Z, and the runs started at
06:02:31Z. Spec: `wk1.spec`. Raw evidence: private apparatus
`evidence/wk1`. One pinned year at cycles 20000 and 30000. The two
streams are identical, and every victim fleet died in both.

| Case | Victims | Follower's waypoint 1 after the year (2 of 2 streams) | Result |
|---|---|---|---|
| A | Orbit unowned planet 7 (1166,1382) all year | Planet 7 at (1166,1382) | CONFIRMED by prediction |
| D | Deep space at (1227,1363), 5 ly from planet 10 | Deep space at (1227,1363), not planet 10 | CONFIRMED by prediction |
| M | Fly 20 ly from (1045,1311) onto unowned planet 0 (1045,1291) and die there | Planet 0 at (1045,1291) | CONFIRMED by prediction |

The host file and player 0's file agree. Player 0 got 0x028 once per
follower, as predicted. Its parameters, the follower and the target's
object id, are MEASURED, since they were not predicted. No follower
arrived. Each follower moved 16 ly toward its waypoint, as predicted:
fleet 11 from y 1282 to 1298, fleet 12 from 1263 to 1279 and fleet 13
from 1211 to 1227.

So waypoint 1 aimed at a fleet destroyed in battle becomes deep space at
the fleet's last position, which is where it died, after this year's
movement. If a planet stands exactly there, the planet is used instead.
It is not the nearest object (D), not the position the waypoint held
before movement (M), and the waypoint does not keep the fleet target.

Other ways a target can be lost remain BINARY-ONLY: scrapped, merged,
out of fuel, a minefield, a wormhole. Waypoint index 2 and up, waypoint
0, a kill by a third player, and targets other than fleets are NOT RUN.

## WK-2: several followers, and waypoints 2 and up, aimed at a fleet destroyed in battle

Question (coordinator, from two ASSUMPTIONs in Elegy's WK-1 code): (a) when two or
more fleets have waypoint 1 aimed at the same fleet and it dies in
battle, does each follower get its own 0x028? (b) when one fleet has
gone-fleet targets at waypoint 1 and at waypoint 2 or later, how many
0x028 does it get, and what do waypoints 2 and up become?

Predictions: `WK2-PREDICTION.md`, pushed alone in 7862a21. The activity
API shows the push at 2026-10-13T13:49:00Z, and the runs started at
13:49:30Z. Spec: `wk2.spec` (a state edit, as WK-1). Raw evidence:
private apparatus `evidence/wk2`. One pinned year at cycles 20000, 30000
and 14000. The three streams are identical, and every victim fleet died
in all three. Each victim pair flew 20 ly due south before it died, so
its death point differs from its start.

| Case | Follower's waypoints after the year (3 of 3 streams) | 0x028 to player 0 | Result |
|---|---|---|---|
| A: 0/11, 0/12, 0/13, waypoint 1 aimed at 1/1 | Each waypoint 1: deep space at (1100,1340), where 1/1 died | 3: (11,513), (12,513), (13,513) | CONFIRMED by prediction |
| B1: 0/14, waypoints 1 and 3 aimed at 1/2, waypoint 2 deep space | Waypoints 1 and 3: deep space at (1300,1240); waypoint 2 unchanged | 2: (14,514) twice | CONFIRMED by prediction |
| B2: 0/15, waypoint 1 aimed at 1/3, waypoint 2 at 1/4 | Waypoint 1: (1200,1220); waypoint 2: (1380,1200); both deep space | 2: (15,515), (15,516) | CONFIRMED by prediction |
| B3: 0/16, waypoint 1 deep space, waypoint 2 aimed at 1/5 | Waypoint 1 unchanged; waypoint 2: deep space at (1060,1180) | 1: (16,517) | CONFIRMED by prediction |

The host file and player 0's file agree. No follower arrived. Each moved
about 16 ly toward waypoint 1.

So each waypoint aimed at a fleet destroyed in battle is handled on its
own: one 0x028 per such waypoint, and the waypoint becomes deep space
where the fleet died. That holds whatever its index (1 to 3 here) and
however many fleets follow the same victim. The alternatives in the
pre-run record (one message per victim, one per follower fleet, only
waypoint 1 checked, the coordinates before movement, the waypoint
removed) did not occur.

MEASURED, not predicted:
- The 0x028 messages come in follower order and, within a follower, in
  waypoint order.
- Each rewritten deep-space waypoint carries its own waypoint index in
  its object field (1, 2 or 3). WK-1's case D showed 1 at waypoint 1.
  Deep-space waypoints written by the builder carry 0.

Scope: victims destroyed in battle by the waypoint owner, at deep-space
points, waypoint indexes 1 to 3. Waypoint 0, a kill by a third player,
and targets other than fleets are NOT RUN. So is the planet substitution
at waypoints 2 and up, though B's deep-space results follow the same
rule as waypoint 1.
