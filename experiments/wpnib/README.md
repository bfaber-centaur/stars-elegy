# WP-NIB: the high nibble of a waypoint's target-type byte

Question: a waypoint carries a target-type byte. Its low nibble is the target
kind: 1 planet, 2 fleet, 4 deep space, 8 a universe object. The client orders
and Combat Lab starts seen so far write the high nibble as 1 (0x11, 0x12,
0x14). RG-002's
computer players also sent waypoints with 0x31 and 0x51 (23 waypoint orders: 6 with 0x31 and 17 with 0x51),
and the saved files carry 0x51 and 0x54. Elegy's vectors drop the high
nibble. Does the nibble change what the host does?

**Prediction, pushed before the runs** (private apparatus 5222299, committed
2026-10-13T03:17:30Z; runs started 03:17:38Z): H0, the nibble has no effect,
from Elegy, which ignores it. The storage rules S1–S4 came from RG-002's saved
waypoints.

**Setup.** `wpnib.spec` (`combatlab build` on Combat Lab base2400, using the
`hi N` fleet token). Every player-0 fleet is one Medium Freighter at warp 5
(25 ly a year). Each group differs only in the nibble:

| Group | Fleets | What happens in the year | Nibbles |
|---|---|---|---|
| M | 1–4 | deep space to planet 9, 47.7 ly: mid-route | 0x11 0x31 0x51 0x91 |
| A | 5–8 | deep space to planet 9, 10.6 ly: arrives | 0x11 0x31 0x51 0x91 |
| D | 9/10, 11/12 | deep space to deep space: mid-route, arrives | 0x14 0x54 |
| W | 13–15 | stationary; nibble on waypoint 0 only | 0x51 (orbit), 0x54, 0x04 |
| T | 16/17 | arrives at an own colony, "unload all colonists" (10) | 0x11 0x51 |
| F | 18/19 | chases a stationary fleet, 50 ly: mid-route | 0x12 0x52 |
| O | 21/22 | leaves orbit of planet 13 for planet 16, 45.5 ly: mid-route | 0x11 0x51 |

One pinned year at cycles 20000 and 30000; both streams were identical.

**Results.**

| Claim | Result | Status |
|---|---|---|
| H0: each variant matches its nibble-1 twin in position, fuel, cargo, waypoints (apart from the byte), task outcome and messages | Holds in every group. T: both fleets unloaded (0x02e) and got 0x04e, and both colonies ended at 585. Player 0's messages differ only in the fleet named. | CONFIRMED by prediction (2 of 2 streams) |
| S1: a waypoint not yet reached keeps its byte | 0x51, 0x91, 0x54 and 0x52 were kept, but 0x31 became 0x11 | Fails for 0x31 (MEASURED) |
| S2: a reached waypoint becomes waypoint 0 with its byte | 0x51, 0x91 and 0x54 were kept, but 0x31 became 0x11 | Fails for 0x31 (MEASURED) |
| S3: a stationary fleet's waypoint 0 keeps its byte | 0x51, 0x54 and 0x04 were kept | CONFIRMED by prediction |
| S4: a fleet that left deep space and is mid-route has waypoint 0 at 0x14 | Holds (M, D, F) | CONFIRMED by prediction |
| O: the waypoint 0 of a fleet that left orbit | 0x14 | MEASURED (not predicted) |

Interpretation (not pushed before the runs): bit 0x20 of the target-type
byte is cleared within the year. Bits 0x40 and 0x80 are carried unchanged.
Bit 0x10 is carried as given (0x04 stayed 0x04). None of these bits changed
movement, fuel, arrival, transport unloading, chasing a fleet or leaving
orbit in this run.

**Not tested:** colonize, merge, lay-mines, patrol and remote-mining tasks
with the nibble set; more than one year; a nibble on a waypoint that the
host itself rewrites when following a fleet that moves.

Raw evidence: private apparatus, `evidence/wpnib`.
