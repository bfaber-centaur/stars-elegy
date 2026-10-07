# BP: battle plans given through the original client

Battle-plan orders written by the original client itself
(`tools/fleetlab/client-orders`), then one pinned host year
(`tools/fleetlab/pinned-turn`). Only orders a player can give in the
client. Raw files (client order files, screenshots, game files) are in the
private apparatus, `evidence/bp/`.

Predictions come from the decomp lane's battle-plan rules (COMBAT.md
"Battle plans", private stars-decomp `docs/combat.md` "Battle plans
(lifecycle)" and `docs/combat-predictions.md` BP-1, BP-2). They were
committed here before the runs.

## Setup

`bp.spec` on the Combat Lab base: player 0 has four one-ship fleets (ids
0–3, "Armed Probe #1"–"#4") at its homeworld, planet 17. One pinned year
(2400 → 2401, cycles 20000) gives a consistent `CB.M1` to open in the
client. All five starting plans have attack-who 2.

## Predictions

| Case | Orders (client) | Prediction |
|---|---|---|
| BP-1 | Copy Default twice (P5 with tactic item 1, P6 with attack-who item 3), so plans 0..6. Fleet 0 → plan 3 (Sniper), fleet 3 → plan 5, fleet 2 → plan 2, fleet 1 → plan 6. Delete plan 3 and OK the alert. | After the year: six plans, Default, Kill Starbase, Max-Defense, Chicken, P5, P6 (P5 and P6 keep their fields). Fleet 0 on plan 2, fleet 3 on plan 4 (still P5), fleet 2 on plan 2, fleet 1 on plan 5 (still P6). Alternative "users of the deleted plan go to plan 0": fleet 0 reads 0. |
| BP-L | Copy Default eleven times (16 plans asked). | Host rule: an append is refused when the player already has 16 plans. Client: in exploration (2026-10-07, one session) the Copy button did nothing at 15 plans, and the host year kept the 15. Prediction for this run: the client again stops at 15 (one copy refused), and the host keeps plans 0..14. A 16th plan cannot be reached from the client, so the host limit stays untested by legal orders. |
| BP-2 | In one client session, create a single-human game, then a second game. | The second game's players all have Default (plan 0) attack-who 3 ("everyone"); every other plan, and every plan of the first game, attack-who 2. The same second game created first in a fresh session: Default 2. LEGACY BUG if seen (Elegy's rule: always 2). |

## Results

Pending.
