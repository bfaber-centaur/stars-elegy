# CB-043: token cap with a starbase and a three-design fleet (CAP-B)

Round 6 (see `../cb042/README.md`). Two-player Combat Lab base, at player
1's homeworld (planet 8) with an armed Orbital Fort (12 Colloidal Phasers).
Player 0: fleets 0..139, one Laser Frigate each. Player 1: fleets 0..129,
one Laser Frigate each, and fleet 130 with three designs (three stacks).
All in orbit. Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

- 255 tokens including the Fort: player 0 127 stacks, player 1 127 stacks
  (fleet 130's three plus fleets 129..6) plus the Fort.
- Left out: player 0's fleets 1..13, player 1's 0..5.
- If the Fort did not count toward the total, the second pass would add
  player 1's fleet 5 (player 1 128 stacks).

## Results

Both streams: **255 tokens**: player 0 127, player 1 127 ship stacks plus
the Fort (fleet 130's three stacks among them). Left out: player 0's
fleets 1..13, player 1's 0..5. **CONFIRMED**: the Fort counts toward the
total and not toward a quota. All hits replayed (611 and 589, 0
mismatches).
