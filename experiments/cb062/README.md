# CB-062: target choice when every primary-type target scores 0

Question, from lane D's target-zero-score spec: `COMBAT.md` "Eligible
targets" used the secondary type only "if no target matches the
primary". RG-003 year 8, the battle at (1571,1434), contradicted that
once. Sapper ships with primary armed and secondary any sapped an
unarmed, shielded minelayer, while the only armed target in reach was a
starbase already stripped of its shields.

- **H-gen** (lane D): when no primary-type target in the slot's reach
  scores above 0, the secondary type is used.
- **H-doc** (`COMBAT.md` as written): a primary-type target in reach
  blocks the secondary type even at score 0, so the slot holds fire.

Pre-run records, never edited after the runs:

| Start | Record | Pushed (activity API) | Runs started |
|---|---|---|---|
| `tz.spec` (Z1, Z1c, Z2) | `PREDICTION.md`, dddec56 | 06:44:56Z | 06:45:07Z |
| `tz2.spec` (Z1b) | `PREDICTION-Z1b.md`, 3ac6b09 | 06:49:14Z | 06:49:25Z |

Each start ran one pinned year at cycles 20000, 30000, 14000, 10000,
7000 and 5000. Raw evidence is in the private apparatus, `evidence/tz`.
Distances are read from each token's square after the round's moves.
For sappers, a **decisive round** has both targets within 3; for the
torpedo, within 4.

## Results

| Case | Setup (player 0's firer; player 1's targets, which never fire) | Observed | Result |
|---|---|---|---|
| Z1b | 2 Pulsed Sappers + 1 Laser. Targets: Laser DD (armed, 0 shields) and Slow Shield BB (unarmed, 4000 shields). | 30 decisive rounds, in 6 of 6 streams: the sapper slot hit the Slow Shield BB every time (147/154/159 at distance 3/2/1, no armor damage). It wrote no record in the 54 rounds with only the Laser DD within 3. It never hit the Laser DD. | H-gen CONFIRMED by prediction for sappers (6 of 6). H-doc fails. |
| Z1c (control) | 2 Pulsed Sappers. Targets: Armed Shield BB (armed, 4000) and Shield BB (unarmed, 4000). | 6 decisive rounds, in 4 of 6 streams: the sapper hit the Armed Shield BB every time. | CONFIRMED by prediction: a primary-type target that scores above 0 is chosen. |
| Z2 | 1 Alpha Torpedo. Targets: Shield FF (armed, armor 45, shields 1000) and Bare FF (unarmed, 0 shields). | 12 decisive shots, in 6 of 6 streams: the torpedo targeted the Shield FF every time. The Bare FF was targeted only on the 7 shots where it alone was within 4. | CONFIRMED by prediction: the torpedo score of `COMBAT.md` stays above 0 when shields far exceed armor. Lane D's premise for Z2 (score 0) fails. |
| Z1 | 2 Pulsed Sappers. Targets: Laser DD and Shield BB (unarmed, 4000; normal speed). | No decisive round in 6 streams. The sapper ship never moved: it stayed 7–8 squares from both. It never fired. The Shield BB left the board in round 5. | Z1's own pre-run question is NOT RUN. Z1b is a second start, whose pre-run (`PREDICTION-Z1b.md`) was pushed after Z1 ran. |

Two consequences:

- **Non-sapper beams, torpedoes and missiles.** By reasoning from the
  CONFIRMED formula, not by measurement, H-gen and H-doc cannot differ
  for them. Their score is at least 1 against any live target: accuracy
  after jamming is at least 1, and `eff > 0` (`PREDICTION.md`). That
  assumes no overflow in the original's arithmetic. Z2 tested one setup
  (Alpha Torpedo, accuracy 35, no jammer or computer), which was not a
  zero-score case.
- **Movement keeps the old rule, in the one setup run** (Z1: a
  sapper-only firer, plan Armed First, one unshielded primary-type
  enemy). In Z1 the sapper ship had no goal and
  did not move, which is MEASURED in 6 streams. Under "Choosing a
  square", its attackable enemies were the primary-type Laser DD alone,
  which it could not damage. If movement fell back to the secondary type
  the way target choice does, the ship would have closed on the Shield
  BB. So the score-0 fallback applies to the choice of target, not to
  the movement goal.

Z1b's Laser slot, as predicted: in all 49 rounds (6 streams) with the
Laser DD within 1, the Laser hit the Laser DD. In two other rounds
(30000 and 5000, round 5), the Laser DD was 2 away, outside the Laser's
reach. The Laser hit the Slow Shield BB at distance 1 instead. That is
the existing "no primary-type target in reach" case.

Scope: the Pulsed Sapper, plan primary armed and secondary any, one
primary-type target, at distance 3 or less. NOT RUN: several
zero-scoring primary-type targets, other plan pairings, other sappers,
and secondary-type targets that also score 0. Nothing is claimed for
bombs.
