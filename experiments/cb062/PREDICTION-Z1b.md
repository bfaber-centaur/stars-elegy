# CB-062 Z1b prediction: a sapper beside an unshielded armed target

Pre-run record for a second start. It is written and pushed before any
run of `tz2.spec`, and it is never edited after the runs. The first
record, `PREDICTION.md`, stays as pushed.

## Why a second start

In the first start's Z1, no stream had a decisive shot. The sapper ship
never moved and never fired, and the unarmed Shield BB left the board in
round 5. That is what `COMBAT.md` "Choosing a square" gives. The sapper
ship's only attackable enemy was the Laser DD, because it matches the
primary type. A sapper cannot damage it, so the ship had no goal. So
Z1 did not answer the question. Z1b brings both targets within reach:

- The firer also carries 1 Laser. That gives it a goal, the Laser DD,
  which it can now damage, so it closes to the Laser's range 1.
- The unarmed target is slow, with 1 Quick Jump 5 (speed code 0, so one
  move in even rounds only). It leaves on its 8th move, in round 14 at
  the earliest, and until then it random-walks near its start square,
  which is the Laser DD's square.

## Start

Spec: `tz2.spec` (Combat Lab base2400), with the same players, tech,
relations and plans as `tz.spec`.

| Token | Design | Plan |
|---|---|---|
| Player 0 firer | Battleship, 4 Trans-Galactic Drive, 2 Pulsed Sapper, 1 Laser, 6 Neutronium | Armed First (primary armed, secondary any, maximize damage) |
| Laser DD | Destroyer, 1 Laser, 2 Tritanium: armed, 0 shields | Hold (never fires) |
| Slow Shield BB | Battleship, 1 Quick Jump 5, 8 Complete Phase Shield, 6 Neutronium: unarmed, 4000 shields | Hold (as unarmed, tactic 0) |

Hashes (sha256):
- `tz2.spec`: e45a08a35d112bac2dfbabdf9795352584b4d9091b6191e1c9037d15f6754c75
- start: 40105212be3a2255ec8fa727e00993bb2f916b8010960128afce7ea583f0212a

Runs: one pinned year at cycles 20000, 30000, 14000, 10000, 7000 and
5000.

A **decisive sapper shot** is a round in which both the Laser DD and the
Slow Shield BB are within 3 of the firer after the round's moves.

## Predictions

| | H-gen (lane D, Elegy dea29cc) | H-doc (`COMBAT.md` as written) |
|---|---|---|
| Sapper slot, decisive rounds | a record on the Slow Shield BB | no sapper record |
| Sapper slot, only the Slow Shield BB within 3 | a record on it | a record on it |
| Sapper slot, only the Laser DD within 3 | no record | no record |
| Laser slot | the Laser DD whenever it is within 1 | the same |

Sapper shield damage on the Slow Shield BB: 164, 159, 154 or 147 at
distance 0 to 3, with no armor damage.

The Laser DD never takes a sapper record under either reading, because
its sapper score is 0. If no stream has a decisive round, Z1b is NOT RUN
for the decisive question.
