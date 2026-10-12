# RM-1 to RM-3: remote-mining refusals

Checks the order of the remote-mining refusal checks that stars-elegy #155
added to `docs/KERNEL.md` "Remote mining" as BINARY-ONLY. Predictions:
`PREDICTIONS.md`, pushed before the runs (bf9518f).

## Setup

`rm.spec` (`combatlab build`) adds four fleets to RG-002's settled 2462
files (apparatus `evidence/rg002`, `s0/settle/raw/after`). They are
start-state edits, not client orders. Every other fleet and planet is as in
those files. Each added fleet is stationary, with one waypoint whose task
is remote mining. Two years were generated (2462 to 2464) at cycles 20000,
with the computer players planning as usual.

| Case | Fleet |
|---|---|
| RM-1a | Player 0 (JOAT) scout with no mining robots, at its own colony 100. |
| RM-1b | Player 0 scout with no mining robots, at Robotoid (HE) planet 52. |
| RM-2 | Macinti (AR) one-ship remote miner (its design slot 14), at player 0's colony 92. |
| RM-3 | Player 0 remote miner (design slot 3) in deep space at (1450, 1450). |

## Results

| Case | Observed, year 1 | Observed, year 2 | Verdict |
|---|---|---|---|
| RM-1a | 0x075, then 0x04e; task none | (no message) | CONFIRMED |
| RM-1b | 0x075, not 0x076; then 0x04e; task none | the scout is lost in a battle with the Robotoid at planet 52 | CONFIRMED (year 1) |
| RM-2 | task still remote mining | task still remote mining (Macinti gave the fleet no new order) | task kept: CONFIRMED; no message: NOT OBSERVABLE |
| RM-3 | 0x077, then 0x04e; task none | (no message) | CONFIRMED |

Notes:

- A computer player's `.M` file has no message block (`MESSAGES.md`). All
  six computer players' files had none here. So RM-2's "no message" cannot
  be observed in this setup. Observing it needs an Alternate Reality player
  that is not a computer player.
- RM-1b's scout was lost in the second year. Player 0's file has a
  2463 battle record at planet 52, between it and the Robotoid. Its year-1
  messages are the case.
- Player 0's message order in year 1 was RM-1a, RM-1b, then RM-3 (fleets 8,
  9 and 10). A 0x04e for fleet 7, which RG-002 also has, came last.

Raw evidence is in the private apparatus `evidence/rm` (start file, both
years, manifests).

## RM-2h: RM-2 with a human Alternate Reality player

RM-2 could not show whether the AR fleet's owner gets a message, because
that owner was a computer player. RM-2h reruns it with two humans. The
start is `rm2h.spec` on the Combat Lab base (sha256 653857de…5fcc5). Player
1 is AR, and its remote miner sits at player 0's colony 15 (no starbase).
One host year was run at cycles 20000 and 30000.

**Prediction.** Elegy main f61e7c4188c627d990dd5a7cedd7288c3ce93b5b was
fetched at 18:39:43Z, before the start was built (18:51:42Z) and before
the runs (output at 18:52:00Z and 18:54:21Z). In `engine/remotemining.go`,
lines 56–59 return no event for an AR fleet at another owner's planet and
leave the task. No branch sends anything to the planet owner.

| Observed (both streams) | Verdict |
|---|---|
| no message to player 1 (the fleet owner), none to player 0 (the planet owner); the remote-mining task is kept; planet 15's surface stays 0/0/0 | CONFIRMED |

**Dropped control.** The first draft also had a JOAT miner at an AR colony
with no starbase, expecting the CONFIRMED 0x076. Neither stream ever
generated that start's year: the host stopped with "integer divide by
0". A start holding only that AR colony did the same. This is the known
divide by zero for an AR planet that is habitable for its owner and has
no starbase (`PARITY.md` KX-001 Z1). It is reproduced here, not a new
finding. The 0x076 refusal itself is already CONFIRMED (TK-111).

Raw evidence: private apparatus, `evidence/rm/rm2h`.

## RM-4: an AR owner's remote miner at its own AR planet in the arrival year

Checks `KERNEL.md` "Remote mining", "When an AR owner's own miners mine":
the BINARY-ONLY claim that such a fleet mines in the year it arrives, with
no did-not-move test, unless it has a further waypoint.

**Prediction.** elegy 7fb6dfe (economy). Elegy's numbers for this exact
start were computed from that commit and pushed to the private apparatus
before the runs: computed 2026-10-12T20:51:34Z, commit time 20:51:50Z.
The runs started at 20:52:03Z.

**Setup.** `rm4.spec` (`combatlab build`) on the Combat Lab base:

- Player 1 is a human Alternate Reality player at tech 26.
- Its miner design is a Mini-Miner with two Robo-Miners, 24 robot points.
- Colonies 4, 5 and 12 are identical: population 500, concentrations
  50/50/50, surface 0, no installations. Each has a Space Station.
- Each miner starts 20 ly out at warp 5, with a remote-mining waypoint.

One pinned year (2400 to 2401) was generated at cycles 20000 and 30000.

| Case | Setup | Elegy (pushed before) | Observed, both streams | Verdict |
|---|---|---|---|---|
| A | Miner 1/1 arrives at AR colony 4, no further waypoint | surface 23/23/23, fractions 231 | 23/23/23, fractions 231 | CONFIRMED: mines in the arrival year (+12 per mineral over D) |
| B | Miner 1/2 arrives at AR colony 5, with a further waypoint | 11/11/11, fractions 244 (= D) | 11/11/11, fractions 244 | CONFIRMED: a further waypoint means no mining |
| D | AR colony 12, no miner | 11/11/11, fractions 244 | 11/11/11, fractions 244 | baseline |
| U | Miner 1/3 arrives at unowned planet 11 | concentrations 50/50/50, fractions 0 | 50/50/50, fractions 0 | CONFIRMED: not mined in the arrival year (as T-35) |

The fleets:

- All three keep the remote-mining task. Fleet 1/2 keeps its waypoint
  onward.
- Player 1's file has no remote-mining message and no 0x04e for any of
  the three fleets. This matches `MESSAGES.md` 0x04e (b), which leaves out
  remote mining. MEASURED: messages were not in the prediction.
- Elegy 7fb6dfe sends its "finished orders" event for 1/1 and 1/3. That
  was not part of the prediction, but it differs from the oracle here.

The two streams agree on every case planet. They differ only at player
1's homeworld, ironium 428 against 427 (the random +1). The case colonies
show no +1 in either stream.

Raw evidence: private apparatus, `evidence/rm4`.
