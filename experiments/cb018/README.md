# CB-018: tech from battle (Q-11)

Player 0 has weapons tech 3 (every other field 26); player 1 has 26
everywhere. In deep space 20 player-0 Laser Frigates destroy 3 player-1
Frigates armed with Colloidal Phasers (a weapon above weapons 3).
Player 0's research goes to energy (15%), so its weapons accumulator is
otherwise untouched. The same start is generated with six pinned seeds
(`cycles=fixed` 20000, 25000, 30000, 35000, 40000, 45000).

## Predictions (committed before the run)

stars-decomp Q-11 (4a8c82b):

- In each run, with probability ½ (fixed per seed), player 0's weapons
  research accumulator rises by exactly the cost of its next weapons
  level; otherwise it stays 0. No other field gains.
- The weapons level itself stays 3 in the 2401 file.
- Player 1, which lost only its own ships to a lower-tech enemy, gains
  nothing.
