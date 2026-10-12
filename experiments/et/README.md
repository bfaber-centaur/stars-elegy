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

**When the message is sent.** ET-1 showed the order in player 0's file
(two streams), but it had no fleet whose message is sent at movement.

- S's 0x04e came before the production messages (0x03f).
- C's unload message (0x02e) came after them, then E's 0x04e, then C's.

ET-1b repeats ET-1 with a bracket fleet N. N arrives at colony 12 with no
task and no further waypoint, so its 0x04e is sent at the end of movement
(0x04e (b)). Elegy #193 at 0a1c002 (the same engine code as 84af588)
predicted the message order. The prediction and Elegy's numbers were
pushed before the runs: computed and committed at 21:59:46Z, runs started
21:59:55Z. Start: `et1b.spec`.

| Observed, both streams | Prediction | Verdict |
|---|---|---|
| S 0x04e, N 0x04e, production 0x03f ×4, C 0x02e, E 0x04e, C 0x04e. Every task is cleared. Colonies 575/585/575. | S and N before the production messages; E and C after them and after C's unload | CONFIRMED |

So the empty transport's 0x04e is not sent on arrival. It is sent later in
the same year, in the after-movement transport pass, with the unloads.
The task ends there, and so it is 0x04e (a). The arrival itself sends
nothing for a transport task (0x04e (b)).

Raw evidence: private apparatus, `evidence/et1`.
