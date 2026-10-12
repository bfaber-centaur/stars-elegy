# ET-1: an empty transport task at the last waypoint and 0x04e

Question: a fleet's transport task has no action for any cargo (no load
and no unload). When it reaches its last waypoint, does the original send
0x04e ("fleet has finished its orders") on arrival, only when the task
ends, or never? This is the edge of `MESSAGES.md` 0x04e (a) and (b) that
elegy #193 left untested.

**Prediction.** elegy #193 head 84af588. Elegy's numbers for this exact
start were pushed to the private apparatus before the runs: computed
2026-10-12T21:57:16Z, commit time 21:57:17Z. The runs started at 21:57:26Z.

**Setup.** `et1.spec` (`combatlab build`) on the Combat Lab base.
Player 0 is human, so its file has a message block. Colonies 4, 5 and 12
are player 0's: population 500, no installations, empty queues. Each fleet
is one Medium Freighter. One pinned year (2400 to 2401) was generated at
cycles 20000 and 30000.

| Case | Setup | Elegy (pushed before) | Observed, both streams | Verdict |
|---|---|---|---|---|
| E | Arrives at colony 4 from 20 ly at warp 5. Its transport task has no action for any cargo. No further waypoint. | task cleared; 0x04e | task cleared; 0x04e; colony 4 population 575 (no change from the cargo) | CONFIRMED |
| C | Control. Arrives at colony 5 the same way, with "unload all colonists" and 10 carried. | task cleared; 0x04e; colony 5 585 | task cleared; 0x02e (10 colonists), then 0x04e; colony 5 585 | CONFIRMED |
| S | Stationary at colony 12. The empty transport task is on its only waypoint. | task cleared; 0x04e | task cleared; 0x04e | CONFIRMED |

So an empty transport task counts as a task that is done. It ends in the
waypoint tasks, and its owner gets 0x04e. That holds for a fleet already
there (S) and for one that has just arrived (E).

**When the message is sent: MEASURED** (message order in player 0's
file, two streams; this was not part of the prediction):

- S's 0x04e comes first, before the production messages (0x03f).
- After them comes C's unload message (0x02e), then E's 0x04e, then C's.

So E's message is sent in the same after-movement pass as C's unload, and
not at movement. A message order sent at movement itself was not observed
here. The reading, which is an inference, is that the pre-movement and
after-movement transport passes end the task and send 0x04e (0x04e (a)),
and that arrival sends nothing for a transport task (0x04e (b)).

Raw evidence: private apparatus, `evidence/et1`.
