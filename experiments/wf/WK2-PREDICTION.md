# WK-2 prediction: several followers, and later waypoints, aimed at a fleet destroyed in battle

Pre-run record. It is written and pushed before any run of this start,
and it is never edited after the runs.

## Question

WK-1 (`PARITY.md` "A waypoint aimed at a fleet destroyed in battle
(WK-1)") had one follower per victim fleet, each with waypoint 1 aimed
at it. Its result was 0x028 once per follower, and waypoint 1 became
deep space at the victim's position after movement (or the planet
standing there). Lane A's elegy #232 implements two cases WK-1 did not
run, as ASSUMPTIONs:

- (a) Two or more fleets have waypoint 1 aimed at the same fleet, and it
  dies in battle. Does each follower get its own 0x028?
- (b) One fleet has gone-fleet targets at waypoint 1 and at waypoint 2
  or later. How many 0x028 does it get, and what do waypoints 2 and up
  become?

RG-003 year 8 had five computer-player followers of one victim. Computer
players' `.M` files there carry no messages at all, so they cannot
answer (a).

## Start

Spec: `wk2.spec` (Combat Lab base2400). This is a state edit: the
builder writes every fleet, waypoint and target directly into the host
file. Each waypoint is one the client can give: a fleet target the
player sees, or a deep-space point.

As in WK-1, player 0's HB Battleship kills a pair of player 1's Laser
Destroyers (plan Hold, never fires) at each battle point. Every victim
pair starts in deep space and flies 20 ly due south at warp 5 to a
deep-space point where the battleship waits. So the place it dies
differs from the place it started, and no planet is within 40 ly of
any battle point. Followers are player 0 Medium Freighters at warp 4,
100 ly or more from their targets, so none arrives.

| Case | Victims (start → death point) | Follower and its waypoints |
|---|---|---|
| A | 1/1, (1100,1320) → (1100,1340) | 0/11 from (1100,1220), 0/12 from (1200,1320), 0/13 from (1029,1249): waypoint 1 aimed at 1/1 |
| B1 | 1/2, (1300,1220) → (1300,1240) | 0/14 from (1300,1120): waypoint 1 aimed at 1/2, waypoint 2 deep space (1220,1080), waypoint 3 aimed at 1/2 |
| B2 | 1/3, (1200,1200) → (1200,1220); 1/4, (1380,1180) → (1380,1200) | 0/15 from (1100,1200): waypoint 1 aimed at 1/3, waypoint 2 aimed at 1/4 |
| B3 | 1/5, (1060,1160) → (1060,1180) | 0/16 from (1060,1280): waypoint 1 deep space (1060,1380), waypoint 2 aimed at 1/5 |

Object ids of the victims: 1/1 = 513, 1/2 = 514, 1/3 = 515, 1/4 = 516,
1/5 = 517.

Runs: one pinned year at cycles 20000, 30000 and 14000. Record the host
file and player 0's file.

## Predictions (H-each: every gone-fleet waypoint is handled on its own)

If a victim pair survives its battle in a stream, the waypoints aimed at
it are not exercised in that stream. They are reported and not scored.

- **A:** waypoint 1 of each of 0/11, 0/12 and 0/13 is deep space at
  (1100,1340). Player 0 gets 0x028 three times, once per follower, with
  params (11,513), (12,513) and (13,513).
- **B1:** 0/14's waypoint 1 and waypoint 3 are both deep space at
  (1300,1240). Waypoint 2 is unchanged. Player 0 gets 0x028 twice for
  fleet 14, both with params (14,514).
- **B2:** 0/15's waypoint 1 is deep space at (1200,1220) and waypoint 2
  is deep space at (1380,1200). Player 0 gets 0x028 twice for fleet 15:
  (15,515) and (15,516).
- **B3:** 0/16's waypoint 1 is unchanged. Waypoint 2 is deep space at
  (1060,1180). Player 0 gets 0x028 once: (16,517).
- 8 messages 0x028 in all. The host file and player 0's file agree.
  Every follower moves 16 ly toward its waypoint 1 and none arrives.

## Alternatives

- **A, H-victim:** one 0x028 per victim fleet, not per follower (one
  message for 1/1). Waypoints as predicted.
- **B, H-fleet:** one 0x028 per follower fleet, whatever the number of
  gone waypoints (B1 one, B2 one). Waypoints as predicted.
- **B, H-first:** only waypoint 1 is checked. B1's waypoint 3 and B2's
  and B3's waypoint 2 keep naming the dead fleet (or keep their old
  coordinates, (1300,1220), (1380,1180) and (1060,1160)), with no
  0x028 for them; B3 then has none at all.
- **B, H-old:** waypoints 2 and up become deep space at the coordinates
  they held before movement ((1300,1220), (1380,1180), (1060,1160)),
  not where the victims died.
- **B, H-drop:** waypoints 2 and up aimed at a gone fleet are removed
  from the list.

Each case is scored on its own observation. If a prediction fails, the
observed outcome is recorded as MEASURED.
