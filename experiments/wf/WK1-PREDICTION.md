# WK-1 prediction: a waypoint aimed at a fleet destroyed in battle

Pre-run record. It is written and pushed before any run of this start,
and it is never edited after the runs.

## Question

In RG-003 year 8, player 1's fleets 81, 82, 84, 86 and 91 had waypoint 1
aimed at player 5's fleet 71. That fleet flew from (1574,1445) onto planet
94 at (1571,1434) and died there in a battle. After the year, each of
those waypoints named planet 94 at (1571,1434). Year 7 has one more
instance of the same pattern: player 5's fleet 45, waypoint 1 aimed at
fleet 5/15, which died at planet 83 in the battle there. Afterwards the
waypoint named planet 83. Elegy keeps a fleet target in these cases.
`ORDERS.md` ("A waypoint aimed at a fleet, in the owner's saved file")
has, as BINARY-ONLY: when the target is gone, the owner gets 0x028 and
the waypoint becomes deep space at its coordinates, or the planet
instead if one stands exactly there.

WK-1 separates these readings:
- **H-planet** (`ORDERS.md`): deep space at the target's last position,
  replaced by a planet that stands exactly there.
- **H-near**: the nearest object to that position (the 0x029 open
  question in `MESSAGES.md`).
- **H-old**: the coordinates the waypoint held before this year's
  movement.
- **H-keep**: the waypoint keeps naming the dead fleet.

## Start

Spec: `wk1.spec` (Combat Lab base2400). Player 0 is the human JOAT, and
player 1 is the enemy. At each of three places, player 0's HB Battleship
(as in E-8, which killed every Laser Destroyer pair in 4 of 4 streams)
meets two of player 1's Laser Destroyers on a plan that never fires.

Each victim fleet is followed by one of player 0's Medium Freighters,
100 ly away at warp 4. Its waypoint 1 is aimed at the victim fleet, and
no follower can arrive.

| Case | Victims | Where they die | Follower |
|---|---|---|---|
| A | 1/4 | Orbiting unowned planet 7 (1166,1382) all year | 0/11 from (1166,1282) |
| D | 1/1 | Deep space at (1227,1363), 5 ly from planet 10 (1224,1359) | 0/12 from (1227,1263) |
| M | 1/2 | Start in deep space at (1045,1311), fly 20 ly at warp 5 onto unowned planet 0 (1045,1291), and die there | 0/13 from (1045,1211) |

Runs: one pinned year at cycles 20000 and 30000. Record the host file
and player 0's file.

## Predictions (H-planet)

If a victim fleet survives its battle in a stream, that case is not
exercised in that stream. It is reported and not scored.

- **A:** follower 0/11's waypoint 1 names planet 7 at (1166,1382).
- **D:** follower 0/12's waypoint 1 is deep space at (1227,1363). It does
  not name planet 10.
- **M:** follower 0/13's waypoint 1 names planet 0 at (1045,1291), the
  victims' position when they died, not (1045,1311).
- The same in the host file and in player 0's file.
- Player 0 gets one 0x028 per follower: three in all.
- No follower reaches its waypoint. Each moves about 16 ly toward it.

Alternatives, per case:
- **H-near:** D names planet 10.
- **H-old:** M is deep space at (1045,1311).
- **H-keep:** any case still names fleet 1/4, 1/1 or 1/2.

A and M follow RG-003 year 8. D is the case that tells H-planet from
H-near.
