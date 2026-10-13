# CB-062 prediction: target choice when every primary-type target scores 0

Pre-run record. It is written and pushed before any run of this start,
and it is never edited after the runs.

## Question

`COMBAT.md` "Eligible targets" uses the secondary target type only "if
no target matches the primary". RG-003 year 8 (battle at (1571,1434))
contradicts that once. Player 1's sapper ships (plan: primary armed,
secondary any) had one armed enemy in reach, a starbase already stripped
of its shields, and they sapped an unarmed, shielded minelayer instead.
Lane D's spec (target-zero-score) asks which reading holds:

- **H-gen** (lane D, Elegy dea29cc): when no primary-type target in
  reach scores above 0, the secondary type is used.
- **H-doc** (`COMBAT.md` as written): a primary-type target in reach
  blocks the secondary type even when it scores 0. A score of 0 is never
  chosen, so the slot holds fire.

## Torpedoes: why no torpedo case can tell them apart

Under the CONFIRMED scoring of `COMBAT.md` "Target choice", a torpedo
never scores 0 against a live target:

- The accuracy after jamming is at least 1. The lowest torpedo accuracy
  is 20, a ship's jammer is at most 95, and `acc − ⌊95·acc/100⌋ ≥ 1` for
  every `acc ≥ 1`.
- `X = A·200/a ≥ 1` because `A ≥ 1`.
- With `S ≥ 1`, `Y + Z` is at least about `Y/2 > 0`. If `Y·a/200 > A`,
  then `Z` is negative but no larger in size than about `Y/2`. With
  `S = 0`, `Z = A·100/(m·a) > 0`.
- So `eff > 0`, and the score `cost/eff` is at least 1.

Beams also score at least 1. Only a sapper can score 0, when `S < 1`.
H-gen and H-doc therefore predict the same for torpedoes and beams under
the CONFIRMED formula. The only exception would be overflow in the
original's arithmetic, which this record does not assume.

Lane D's torpedo case Z2 is still run. Its premise is that shields far
above armor make a torpedo score 0, and Z2 tests that premise directly.

## Start

Spec: `tz.spec` (Combat Lab base2400). Players 0 and 1 are at tech 26
in every field and are mutual enemies. Each case is its own deep-space
battle.

- Player 1's stacks use a plan that never fires (primary fuel
  transports).
- Player 0's single firer uses plan "Armed First": primary armed ships,
  secondary any, maximize damage.
- No ship has a computer, jammer, capacitor or deflector.

| Case | Firer | Player 1 targets |
|---|---|---|
| Z1 | Battleship, 2 Pulsed Sappers | Laser DD: armed, 0 shields. Shield BB: unarmed, 4000 shields. |
| Z1c (control) | the same | Armed Shield BB: armed, 4000 shields. Shield BB: unarmed, 4000 shields. |
| Z2 | Battleship, 1 Alpha Torpedo (accuracy 35) | Shield FF: Frigate with 1 Laser and 2 Complete Phase Shields (armor 45, shields 1000). Bare FF: unarmed Frigate, 0 shields. |

Hashes (sha256):
- `tz.spec`: ae6d552d5aafc1001e73f09f504378911f5e8fed06b0c48fe82a6f76e8cdb7a0
- start: 53fae0ab0e2dd27b32b1e3d7731affed0b73380e51da4ea320cb46c34daeb7b5

Runs: one pinned year at cycles 20000, 30000, 14000, 10000, 7000 and
5000. Raw evidence will be in the private apparatus, `evidence/tz`.

A **decisive shot** is one where both targets are within the weapon's
reach (Pulsed Sapper 3, Alpha Torpedo 4), read from each token's square
in the battle record. Shots with one target in reach are reported but do
not decide.

## Predictions

Sapper damage, if a record is written: shields only,
`(100 − ⌊10x/3⌋)·164/100` at distance `x`, so 164, 159, 154 and 147 at
distances 0 to 3 (CB-060 S1 rule, 2 × 82).

| Case | Decisive shots, H-gen | Decisive shots, H-doc |
|---|---|---|
| Z1 | sapper record on Shield BB | no sapper record (the Laser DD scores 0 and blocks the secondary type) |
| Z1c | sapper record on Armed Shield BB | the same |

In Z1, with only Shield BB in reach, both readings predict a record on
Shield BB, because no primary-type target is in reach. With only the
Laser DD in reach, both predict no record. The Laser DD never takes a
sapper record in Z1.

Z2, under the CONFIRMED formula with either reading: the torpedo targets
Shield FF on every decisive shot.
- Shield FF: `A` 45, `S` 1000, `a` 35. `X = 257`, `Y = 4000`,
  `Z = (45 − 700)·100/35 = −1871`, `Y + Z = 2129`, `eff = 257`, score at
  least 1.
- Bare FF is not primary-type, and it is not considered while Shield FF
  is in reach.
- Lane D's premise (score 0 for shields ≫ armor, then the secondary
  type): the torpedo targets Bare FF on decisive shots.

If no stream has a decisive shot in a case, that case is NOT RUN for the
decisive question.
