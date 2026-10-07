# CB-044: the second pass skips a fleet that does not fit (CAP-C)

Round 6 (see `../cb042/README.md`). CB-039 (140 one-ship Laser Frigate
fleets per player in deep space), except player 1's fleet 12 holds two
designs (two stacks). Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

- First pass: player 0's fleet 0, player 1's 139..13, player 0's 139..14
  = 254 stacks. The second pass skips player 1's fleet 12 (it would make
  256) and adds player 1's fleet 11.
- 255 tokens: player 0 127, player 1 128.
- Left out: player 0's fleets 1..13, player 1's 0..10 and 12.
- If the second pass stopped at the first fleet that does not fit: 254.
