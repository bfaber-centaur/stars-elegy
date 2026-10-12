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
