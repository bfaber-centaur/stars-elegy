# PD-1: mass-driver packet settings when a starbase is replaced

Question: when a starbase item completes, what happens to the planet's
packet destination, its packet speed and its queued packet items? The
rule in `PRODUCTION-LAUNCH.md` "Starbases" (mass driver item; lane G,
BINARY-ONLY) compares the driver before the replacement with the new one.
The economy lane asked four questions, and lane G predicted their answers.

**Setup.** `pd1.spec` and `pd1b.spec` on Combat Lab base2400, player 0
JOAT at tech 26, one planet per case, with the starbase item first in the
queue at 99% and ample resources. A packet setting is stored with the
starbase, so it can only be preset where a starbase already stands; where
set, the destination is the homeworld. Fort = Orbital Fort, no driver;
Catcher 7 = Orbital Fort with one Mass Driver 7; Twin 7 = Space Station
with two Mass Driver 7s; Ultra 10 = Orbital Fort with one Ultra Driver 10.

**Predictions** (private apparatus). PD-1's was pushed at 22:55:26Z,
before its runs started at 22:55:35Z. PD-1b's was committed at 22:58:28Z
and pushed at 22:58:30Z, the same second as its run start, so the record
cannot show the push came first: PD-1b's rows are MEASURED, consistent with
the pre-committed prediction.

- lane G gave the numbers for a, b, c and d; lane F derived the other cases
  from the same rule before the runs;
- elegy 8426a6a has no replacement rule: every setting unchanged.

One pinned year at cycles 20000 and 30000 per start; the two streams agree
on everything below.

| Case | Before → built | Setting before | Queue after the starbase | Observed | Verdict |
|---|---|---|---|---|---|
| a0 | none → Fort | none | ironium packet, auto packets | ironium item removed, auto item kept, no message | CONFIRMED by prediction (derived) |
| a | Fort → Fort | home, warp 6 | ironium packet, auto packets | destination and speed cleared; ironium item removed, auto item kept; no message | CONFIRMED by prediction (lane G) |
| b | Catcher 7 → Fort | home, 6 | ironium packet | home, 6 kept; the ironium item cancelled with 0x129 that year | CONFIRMED by prediction (lane G) |
| c0 | none → Catcher 7 | none | — | speed 7, no destination | CONFIRMED by prediction (derived) |
| c | Fort → Catcher 7 | home, 6 | — | home, speed 7 | CONFIRMED by prediction (lane G) |
| d (PD-1b) | Catcher 7 → Twin 7 | home, 6 | — | home, 6 kept | MEASURED, consistent with the prediction (lane G) |
| d2 (PD-1b) | Catcher 7 → Ultra 10 | home, 9 | — | home, 9 kept | MEASURED, consistent with the prediction (derived) |
| e (PD-1b) | Fort → Twin 7 | home, 9 | — | home, speed 8 (7 + 1) | MEASURED, consistent with the prediction (derived) |
| k | Catcher 7, nothing built (control) | home, 6 | — | unchanged | consistent |

Elegy 8426a6a differs in a0 (it sent the 0x129 cancel), a, c0, c and e.

**Setup defect, and what it showed.** PD-1's first d and e used a Space
Station with two Mass Driver 5s. Mass Driver 5 is Packet Physics only, so
this JOAT race may not build it. Neither starbase was built. The item
left the queue with no starbase message, the old starbase and its setting
stayed, and only 0x03e was sent. Two diagnostic runs, made without a
prediction, found the same for every design holding a Mass Driver 5 (a
Space Station or an Orbital Fort, at 99% or 0% done; at 0% some minerals
had been spent). Designs with Mass Driver 7s were built. Elegy built the
Mass Driver 5 starbases. MEASURED, one stream each.

Raw evidence: private apparatus, `evidence/pd1`.
