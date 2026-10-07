# CB-039: the token cap

Round 5 (COMBAT.md "Who is in the battle", token cap: at most 256 tokens;
each player gets `255 / players` stacks, then left-out fleets are added
back while room remains; BINARY-ONLY). Two-player Combat Lab base. Each
player has 140 one-ship Laser Frigate fleets (plan "enemies") at the same
deep-space point: 280 stacks. Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

- The battle has **256** tokens (the record's token count may show it
  modulo 256).
- Each player has at least 127 tokens. Reading the re-add as fleet-list
  order (player 0 first): player 0 has 129 and player 1 has 127 (lower
  confidence than the total).
- The 24 left-out fleets take no part: no damage, and they are not in the
  record.

## Results

Both streams: **255 tokens**, player 0 **127**, player 1 **128**. All
hits replayed (738 and 769, 0 mismatches).

- **Total MISSED:** 255, not 256.
- **Split MISSED:** player 1 got the extra token, not player 0.
- **Left-out fleets CONFIRMED:** they took no part and survived. The same
  fleets were left out in both streams: player 0's fleets 1..13 (13) and
  player 1's fleets 0..11 (12). Player 0's fleet 0 fought; player 1's did
  not. Every other survivor was a battle survivor (different ids per
  stream).

A reading consistent with this (inferred, not tested): each player first
gets `255 / 2` = 127 stacks, taking fleets from the end of the fleet list
backwards apart from the fleet whose location this is (player 0's fleet
0); one stack of room remains, and the re-add pass gives it to player 1's
fleet 12.
