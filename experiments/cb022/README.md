# CB-022: the plan-0 "player i" degenerate battle

R-10 (stars-decomp 134256d). Player 0 (A) owns planet 18 with a Laser
Station. Player 1 (B) sees A as neutral and A sees B as an enemy. B's fleet 0
is a lone hauler far away (a ring with no battle, examined before A's
planet). B's fleet 1, five Laser Frigates attacking "enemies", sits at
planet 18. Player 0 has no fleets.

| spec | A's plan 0 attack-who |
|---|---|
| `cb022.spec` | player 1 |
| `cb022-enemies.spec` | enemies |
| `cb022-everyone.spec` | everyone |
| `cb022-nolone.spec` | player 1, without B's lone hauler |

Each is generated with `tools/fleetlab/pinned-turn` at cycles 20000 and
30000.

## Predictions (committed before the run)

- `cb022`: a battle record with one player (`cplr` = 1) and no fire
  actions; the station drops out after the first movement phase. The
  decomp's reason: plan 0's attack mask is read from a stale slot, which here
  holds player 1 from the lone hauler's ring. Token-to-square assignment is
  not predicted; the token list is reported as recorded.
- `cb022-enemies`, `cb022-everyone`: an ordinary two-player battle in which
  the station fires.
- `cb022-nolone`: no prediction (the slot's value on the turn's first ring
  is unknown). Reported for information.
