# CB-019: tactics "maximize net damage" (3) vs "maximize damage ratio" (4)

Q-9 (stars-decomp 4a8c82b, old P-11). With the RNG pinned, the same start
can be compared under the two tactics. One player-0 Long Destroyer
(Phaser Bazooka, Colloidal Phaser, 2 Tritanium) attacks player 1's
immobile Laser Station at planet 8; only one token moves, so stack weight
order and jitter do not matter. `cb019-t3.spec` and `cb019-t4.spec`
differ only in the tactic of player 0's plan 3. Each is generated with two
pinned seeds (`fixed 20000`, `fixed 8000`).

## Predictions (committed before the run)

- For each seed, the two tactics give the same move sequence and the same
  hits (identical battle records), since both score squares the same way
  and only ties use the random stream.
