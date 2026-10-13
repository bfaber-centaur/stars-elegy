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
  whoever owns it, wherever it is (this is the hypothesis as pushed; only
  40 ly was run) (`ORDERS.md` "Salvage and mineral packet
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
or another player's. With waypoint 0, a named packet 40 ly away was loaded
from, and the fleet did not move (CONFIRMED by prediction). Other distances
are NOT RUN.

Interpretation, consistent with `OBJECTS.md`:

- **Waypoint-0 loads.** These ran before movement (their 0x02b came before
  the production messages). The year's decay (`OBJECTS.md` "Salvage", its decay item) then
  removed the emptied objects, and an emptied packet's flight that year did
  not keep it.
- **Arrival loads.** These ran after the decay (`OBJECTS.md` "Turn
  placement", step 5). The arrivals therefore found 100 − ⌊100/10⌋ = 90,
  and the emptied salvage stays until the next year's decay. ET-2's emptied
  packets stayed for the same reason. **Clarified 2026-10-13 (NS-2 P1-F):**
  a packet emptied after movement stays (MEASURED).

Raw evidence: private apparatus, `evidence/ns1`.

## NS-2: a named packet at 10 and 150 ly, and after movement

Question (coordinator, from elegy lane A's ASSUMPTION T5): T5 says a named
packet is a source at any distance, in both load passes. NS-1 ran only
waypoint 0 at 40 ly. Predictions: `NS2-PREDICTION.md`, pushed in 950c64c.
The activity API shows the push at 2026-10-13T05:16:03Z, and the runs
started at 05:17:07Z. Spec: `ns2.spec`. Raw evidence: private apparatus
`evidence/ns2`. One pinned year at cycles 20000 and 30000. The two streams
are identical in every value below.

| Case | Setup | Observed (2 of 2 streams) | Result |
|---|---|---|---|
| N | Waypoint 0 at player 0's planet 3 names an in-flight packet 10 ly away | Loaded 100 kT boranium before movement: 0x02b at the packet, then 0x04e. No ironium; the planet keeps 50/0/0. The fleet did not move. The packet is gone at the end of the year. | CONFIRMED by prediction (the removal included: the pre-run record predicted it from NS-1 B) |
| F | As N, with the packet 150 ly away | As N | CONFIRMED by prediction (the removal included) |
| P1 | A packet written unmoved lies in deep space at (1080,1180). A fleet 20 ly away flies there at warp 5 with waypoint 1 naming it. | The packet moved a full 25 ly before fleet movement, to (1096,1161), and is now marked moved. Waypoint 1 followed it. The fleet stopped about 17 ly short, at (1089,1177), and loaded nothing. | Branch E (MEASURED). The after-movement load from a distance was not reached. |
| P1-F | An in-flight packet at (1000,1300). A fleet 20 ly away at warp 9 with waypoint 1 naming it. | The packet moved 25 ly and waypoint 1 followed it. The fleet reached the packet's new position, (1008,1276), and loaded 100 kT boranium after movement: 0x02b then 0x04e, after the production messages. The emptied packet stays. | MEASURED (the tracking branch, as predicted); load at distance 0, as ET-2 |

So waypoint 0 loads from a named packet at 10, 40 and 150 ly (NS-1, NS-2)
before movement. For arrival, the waypoint followed the packet's move, so
the fleet loaded where the packet was or did not arrive at all. A load
after movement from a packet some distance away was not produced: no
crafted start made a packet move after the fleets, so it stays UNRESOLVED.
P1 is a crafted state: the packet was written with bit 14 ("has moved")
clear (see the bit-14 note in `docs/ORACLE.md`).
