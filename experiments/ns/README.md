# NS-1: a transport task whose waypoint names a packet or salvage

Questions (from Elegy lane A's load-from-the-named-object rework, where two
edge rules were ASSUMPTION):

- (a) The named packet or salvage sits over a planet, the fleet's own or
  another player's. Does the task load from the named object or from the
  planet?
- (b) The named packet has flown on from the fleet's position. Does the
  fleet load anything, and is 0x04e or 0x11e sent?

**Predictions, pushed before the runs** (private apparatus 4b3ab213,
committed 2026-10-13T00:55:54Z, the push returned by 00:55:56Z; the runs
started 00:56:04Z), for the exact start:

- **H-named:** only the waypoint's task acts, on the object it names,
  whoever owns it, wherever it is (`ORDERS.md` "Salvage and mineral packet
  targets", the BINARY-ONLY "Arrival" reading). Every fleet loads the named
  object's 100 kT boranium, takes no ironium from the planet, and gets
  0x02b at the object, then 0x04e. No 0x11e. The emptied object stays at
  0/0/0.
- **H-planet:** Elegy lane A's ASSUMPTION T5. A planet at the fleet's
  position takes precedence, and a packet counts only at the fleet's
  position. Over an own planet, the fleet loads that planet's 50 kT ironium
  and the object keeps its cargo. Over another player's planet it loads
  nothing. No 0x11e.

**Setup.** `ns1.spec` (`combatlab build` on the Combat Lab base). The spec
uses CombatLab's `target thing`, which aims waypoint 0 at a universe object.

- Every fleet is player 0's single empty Medium Freighter (210 kT) with the
  task "load all ironium, load all boranium".
- Every named object holds 0/100/0 (boranium only).
- Every planet under test has 50/0/0 on its surface (ironium only),
  population 500 and no installations. Player 1 owns planets 9, 14, 19
  and 20.
- One pinned year was generated at cycles 20000 and 30000. The two streams
  are identical in every fleet, object, planet and player-0 message below.

| Case | Setup | Observed (both streams) | Verdict |
|---|---|---|---|
| A1 | The fleet arrives from 20 ly at warp 5. Waypoint 1 names player 0's salvage over player 0's planet. | It loaded 90 kT boranium from the salvage: 0x02b at the salvage, then 0x04e, after the production messages. No ironium; the planet keeps 50/0/0. The salvage remains, empty. | MEASURED. The source is as H-named, but the amount is 90, not 100. |
| A2 | As A1, over player 1's planet | As A1 | MEASURED, as A1 |
| A3 | The fleet orbits player 0's planet. Waypoint 0 names player 0's salvage over that planet. | It loaded 100 kT boranium from the salvage: 0x02b at the salvage, then 0x04e, before the production messages. No ironium; the planet keeps 50/0/0. The salvage is gone at the end of the year. | CONFIRMED by prediction (H-named) for cargo, planet and messages. The removal is MEASURED. |
| A4 | As A3, over player 1's planet | As A3 | As A3 |
| A5 | As A3, with player 0's packet (bound elsewhere at warp 5) over the planet at the start of the year | As A3. The packet is gone at the end of the year. | As A3 |
| A6 | As A5, with player 1's packet over player 1's planet | As A5 | As A3 |
| B1 | The fleet orbits player 0's planet. Waypoint 0, at the planet's coordinates, names player 0's packet, which is 40 ly out toward its destination (as after its launch year). | It loaded 100 kT boranium from that packet: 0x02b at the packet, then 0x04e. No ironium; the planet keeps 50/0/0. The packet is gone at the end of the year. | CONFIRMED by prediction (H-named) for cargo, planet and messages. The removal is MEASURED. |
| B2 | As B1, with player 1's packet launched from player 1's planet | As B1 | As B1 |

In every case the task was cleared and the fleet stayed where it was or
where it arrived. Its waypoint 0 was then aimed at the planet there. No case
got 0x11e. H-planet failed every case.

So a transport task loads from the object its waypoint names, not from a
planet at the same spot. That holds whether the planet is the fleet's own
or another player's. With waypoint 0, the named packet is found wherever it
is: a packet 40 ly away was loaded from, and the fleet did not move.

Interpretation, consistent with `OBJECTS.md`:

- **Waypoint-0 loads.** These ran before movement (their 0x02b came before
  the production messages). The year's decay (`OBJECTS.md` "Salvage", its decay item) then
  removed the emptied objects, and an emptied packet's flight that year did
  not keep it.
- **Arrival loads.** These ran after the decay (`OBJECTS.md` "Turn
  placement", step 5). The arrivals therefore found 100 − ⌊100/10⌋ = 90,
  and the emptied salvage stays until the next year's decay. ET-2's emptied
  packets stayed for the same reason.

Raw evidence: private apparatus, `evidence/ns1`.
