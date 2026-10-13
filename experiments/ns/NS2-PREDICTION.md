# NS-2 prediction (pushed before the runs)

Question (coordinator, from elegy #215's ASSUMPTION T5): T5 says a fleet
whose waypoint names a mineral packet loads from it at any distance, in
both load passes. NS-1 confirmed this only before movement, and only at
40 ly. NS-2 tests two more things:
- the pass after movement, with a packet that flies on in the same year;
- waypoint 0 at two other distances.

Setup: `ns2.spec`, built with `combatlab build` on the Combat Lab base.
- Every fleet is player 0's empty Medium Freighter with "load all
  ironium, load all boranium".
- Every packet is player 0's, class 0 (no decay), with 100 kT of
  boranium and nothing else.
- The planets under test are player 0's, with 50 kT ironium and no
  boranium.

Runs: one pinned year at cycles 20000 and 30000.

| Case | Setup |
|---|---|
| P1 | Packet 0 lies in deep space at Q = (1080,1180), written unmoved (as NS-1 A5's), bound for planet 4 at warp 5. The fleet starts 20 ly south and flies to Q at warp 5; waypoint 1 names the packet. |
| P1-F | Packet 1 is in flight (moved, as NS-1 B1's) at (1000,1300), bound for planet 1 at warp 5. The fleet starts 20 ly south at warp 9; waypoint 1 names the packet. |
| N | The fleet orbits planet 3. Waypoint 0, at the planet, names packet 2, in flight 10 ly away. |
| F | The fleet orbits planet 13. Waypoint 0, at the planet, names packet 3, in flight 150 ly away. |

## Predictions

All predictions follow T5: a named packet is loaded at any distance,
in either pass.

- **N, F (waypoint 0, before movement):** the fleet loads the packet's
  100 kT of boranium and no ironium, with 0x02b at the packet, then
  0x04e. The planet keeps 50/0/0, and the fleet does not move. The
  emptied packet is gone at the end of the year, as in NS-1 B. That last
  part is MEASURED there, not T5.
- **P1 (after movement).** The packet move that happens before fleets
  move (`KERNEL.md` "Turn order" step 3.2) covers packets "already in
  flight". Packets launched this year fly in step 5, after fleet
  movement.
  - Branch L: the unmoved packet flies in step 5, after the fleet has
    reached Q. The fleet then loads 100 kT of boranium in the pass after
    movement, from the packet ⌊25/2⌋ = 12 ly away (`OBJECTS.md` "Flight
    and decay": launch-year move). The packet is empty.
  - Branch E: the packet moves in step 3.2. The waypoint follows it
    (`ORDERS.md` "Tracking"), so the fleet does not reach it this year
    and nothing loads. That would leave the after-movement question
    untested here.
- **P1-F (after movement, tracking).** The packet moves 25 ly in step
  3.2, and the waypoint follows it. The fleet (81 ly) reaches the
  packet's new position and loads all 100 kT after movement, as in
  ET-2. A fleet left at the packet's old position, with the packet 25 ly
  away, is the T5 at-a-distance case: under T5 it also loads 100 kT.

CONFIRMED needs the stated branch and the stated result in the same
stream. Any other outcome is MEASURED.
