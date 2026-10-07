# CB-035: the plan-0 value X on the first location of a turn

Round 5. COMBAT.md "LEGACY BUG: plan 0": with plan 0 "player i" at an armed
starbase, the game ORs player i into the attack set of player X instead of
the starbase owner's. X is player 0 after a location with a battle, the
owner of the last fleet of a battle-less location, and not determined for
the first location of a turn (CB-022 "no lone fleet": neither 0 nor 1).
`gen.py` here writes every round-5 spec (CB-035..CB-041).

Sixteen-player game made by `tools/fleetlab/new-game` from `cb16p.def`
(game CB16P; every player set to JOAT). The location is player 0's
homeworld (planet 16) with an armed Laser Station; player 0's plan 0 is
"player 1". Players 1..14 each have one Laser Frigate in orbit there.
Player 1's plan names player 15 (who has nothing there); players 2..14
attack nobody. All relations are neutral. Player 0 has no fleets, so this
ring holds the first fleet in fleet order and is examined first.

Reading X from the record: the record's player list is the starbase owner
plus every player in the battle.

| X | outcome |
|---|---|
| 0 | ordinary battle, players {0, 1}, the station fires |
| 1 | one-player battle (`n` = 1): players {0, 1}, start squares (4,4), (1,4), no actions |
| 2..14 | battle between X and player 1: players {0, 1, X}, `n` = 2, X fires at player 1 |
| 15 | players {0, 1}, `n` = 2, no shots |
| ≥ 16 | no battle |

Variants, each pinned at cycles 8000, 12000, 16000, 20000, 30000, 50000:

- `cb035`: only these fleets.
- `cb035-lone`: plus one lone fleet each for players 2..14 in deep space
  (later locations).
- `cb035-move`: the same lone fleets, each flying to a waypoint this turn.
- `cb035-p0lone`: control. A lone player-0 fleet in deep space is the
  first location, so X = 0 at the station.

## Hypotheses (committed before the run)

- H1: in `cb035`, `cb035-lone` and `cb035-move`, X is not a player of the
  game: **no battle** in any stream (extending CB-022).
- H2: X does not depend on the random stream: for a given start, all six
  cycle counts give the same outcome class.
- H3: X does not depend on the extra fleets or their movement: the three
  variants give the same outcome class.
- `cb035-p0lone`: an ordinary battle with players {0, 1} (X = 0), in
  every stream.

## Added variants: X from the previous location (committed before their run)

Committed after the first four variants ran (no battle in 24 of 24 runs,
results below) and before these two ran. Both put a player-0 fleet and a
player-3 fleet at (1060,1080), which is then the first location; planet
16 comes second.

- `cb035-prev3`: all neutral, so no battle there. The last fleet of that
  location is player 3's, so **X = 3**: at planet 16 player 3's Frigate
  attacks player 1. Record players {0, 1, 3}, `n` = 2, only player 3
  fires; player 1 does not fire back (its plan names player 15).
- `cb035-prevbattle`: players 0 and 3 are enemies and fight there. After
  a battle **X = 0**: at planet 16 the station attacks player 1, players
  {0, 1}, as in `cb035-p0lone`.

## Results

| variant | runs | outcome at planet 16 | X |
|---|---|---|---|
| `cb035` | 12 cycle counts (5000 … 50000) | no battle in 12 of 12 | not a player of the game |
| `cb035-lone` | 6 | no battle in 6 of 6 | not a player |
| `cb035-move` | 6 (the lone fleets moved) | no battle in 6 of 6 | not a player |
| `cb035-p0lone` | 6, 6 distinct records | players 0x3, the station destroys player 1's Frigate | 0 |
| `cb035-prev3` | 6, 4 distinct records | players 0xb {0, 1, 3}; player 3's Frigate attacks player 1 | **3** |
| `cb035-prevbattle` | 6, 5 distinct records | battle at (1060,1080) (0x9), then players 0x3, the station fires | **0** |

All hits replayed by the checker, 0 mismatches.

- **H1, H2, H3 CONFIRMED** (36 runs): at the first location of these
  turns X was never a player of this 16-player game, in every stream and
  with or without extra and moving fleets elsewhere. In this setup X ≥ 16
  (or otherwise not a player); its exact value is not observable this way.
- **Previous-location rule CONFIRMED for X ≠ 0** (`cb035-prev3`): after a
  battle-less location whose last fleet was player 3's, the station's
  "player 1" went into player 3's set. Player 3, which attacks nobody by
  its own plan, attacked player 1 at another player's planet.
- **X = 0 after a battle CONFIRMED** (`cb035-prevbattle`).
- **MISSED (my prediction, not the spec):** in `cb035-prev3` player 1
  fired back at player 3. COMBAT.md step 7 (retaliation) says it should:
  player 1 is attacked, so every player whose set names player 1 joins
  player 1's set. My prediction overlooked that step.
