# UG: universe generation corpus

Tests the stars-decomp reading of new-game generation (private
`docs/universe-gen.md`, `docs/universe-gen-predictions.md` UG-1..UG-9, and
`tools/universe.py` on stars-decomp PR #15).

Every game is built from a game definition file with
`tools/fleetlab/new-game` (no UI input; `docs/ORACLE.md` "New games from a
definition file"), and the private model scores the new game field by field:
planet positions, name ids, every planet's environment, concentrations and
artifact flag, owners, homeworlds, starting tech, designs, fleets, logos,
wormholes and the option word.

The definitions, the race files and the model's predicted games are kept
in the private apparatus repository (`evidence/ug/`). This repository
records only behavior-level results.

## Round 1: the decomp's 15 games (UG01..UG15)

Predictions were committed in stars-decomp 1327269 before any run. They
cover two-player and many-player games with the SS race file PG000.R1 and
computer players, every size and density, the max-minerals, BBS, clumping
and no-random-events options, and seed aliasing.

## Round 2: crafted races (UG16..UG21)

Committed (apparatus 80e6c1b, and this file) before running. Race files are
PG000.R1 with only the primary trait and the leftover-points spend changed
(`tools/fleetlab/racelab edit`). All six are legal with more than 50
advantage points left, so each homeworld gets the full 50-point leftover
spend.

| Game | Size | Players | Tests |
|---|---|---|---|
| UG16 | medium | WM (spend: mines), SD (factories), IT (defenses), JOAT (surface minerals) | starting tech, designs and fleets of WM, SD, IT and JOAT; leftover spends on mines, factories and defenses; IT second planet; the shared homeworld minerals with 4 players |
| UG17 | large | the four UG16 races and 4 computer players | the same with 8 players |
| UG18 | small | IT and one computer player | IT second planet and gate starbase on a small map |
| UG19 | tiny | IT and PP | no second planet on a tiny map |
| UG20 | medium | PP (mines), JOAT (concentrations), one computer player | PP second planet for a human race; the concentrations spend |
| UG21 | huge, BBS | the six races and 10 computer players | 16 players; BBS with every PRT above |

Predicted for every game, by the model: the whole game exactly. Behavior
claims under test:

- Starting tech by PRT: WM weapons 6, propulsion 1, energy 1; SD propulsion
  2, biotech 2; IT propulsion 5, construction 5; PP energy 4; JOAT 3 in
  every field.
- Leftover points L = 50: mines +L/2 (25), factories +L/5 (10), defenses
  +(L+5)/10 (5), concentrations +L/2 on the lowest and +⌈L/4⌉ on all,
  surface minerals +10·L kT split as the model says.
- IT and PP on maps larger than tiny get a second planet 15–23% of the
  galaxy width from home with 2/5 of the homeworld's population (the
  homeworld keeps 4/5), and IT's starbases carry a stargate.
- Every homeworld in a game starts with the same surface minerals (one
  draw set, before spends) and with planet 0's concentrations floored at
  30, not its own (UG-9, candidate LEGACY BUG).

## Results

All 21 games matched the model field by field with 0 mismatches, and so
did UG01 rebuilt at cycles 30000. No prediction missed. The behavior is
recorded in `docs/PARITY.md` "Universe generation".

`homeworlds.py` prints each game's homeworld facts from the dump that
`new-game` writes (`OUT/after.dump`):

```sh
python3 experiments/ug/homeworlds.py OUT/after.dump
```

Round 2 observations (UG16..UG21):

- Starting tech by PRT was as listed above in every game.
- Spends with L = 50: mines 10 → 35, factories 10 → 20, defenses 10 → 15,
  surface minerals +500 kT (+250 on the smallest, +125 on the others),
  concentrations +25 on the lowest and +13 on all.
- IT and PP got the second planet (homeworld population 200 of 250,
  second planet 100, 10 mines, 4 factories) on small, medium, large and
  huge maps, and none on the tiny map of UG19.
- UG-9 held in all six games, up to 16 players (UG21): every homeworld
  without a spend had planet 0's concentrations floored at 30 and the
  game's one surface-mineral draw.

Tool note: the model's checker crashed on games with an AR homeworld
(an owned planet with no installations); a one-line local patch was used
for the runs, and the fix was sent to the decomp lane.
