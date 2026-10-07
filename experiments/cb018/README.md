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

## Amendment before the second batch

The first batch (research at 15%) is confounded: with every other field
at 26, ordinary research flows into weapons. In all six seeds player 0
reached weapons 4 in 2401 and every accumulator read 0. The second
batch sets player 0's research to 0% (`research 0 0`, a new CombatLab
directive) and adds `cb018-control.spec`, identical except that player
1's frigates are 280 ly away (no battle). Predictions unchanged: the
control stays at weapons 3 with nothing accumulated; the battle runs
gain one weapons level's cost (or the level) in about half the seeds.

## Results

- Batch 1 (research 15%, six seeds): weapons 4 everywhere; confounded.
- Control (research 0%, no battle; two seeds): weapons 3, accumulators 0.
- Battle (research 0%): 14 cycle values gave 6 distinct battle streams.
  Weapons was 4 in the 2401 file for 4 streams (cycles 8000, 12000,
  20000, 25000, 30000–45000) and 3 for 2 streams (16000; 50000–100000).
  Every research accumulator read 0. Player 1 gained nothing.
- The gain is random per stream, as predicted; the level rose within the
  same generation, which the prediction did not expect.
