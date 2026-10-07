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
