# CB-057: Regenerating Shields armor per slot, a computer-99 torpedo salvo, the target-cost cap

Lane D's three questions after RG-002. Predictions were pushed first: elegy
#185 head 89cbc6a (`TestPredictionCB057RegeneratingShieldsTwoSlots`,
`TestPredictionCB057NexusTorpedoes`, `TestPredictionCB057TargetCostCap`),
fetched at 19:09:49Z on 2026-10-12. The runs began at 19:16:35Z. The run
designs differ a little from the tests' designs, for the reasons given below.
Elegy's numbers for the run designs were computed from the same commit, but
first pushed (apparatus `evidence/cb057/PREDICTION.md`) after the runs began.
So the results are MEASURED (oracle) and consistent with Elegy 89cbc6a, not
CONFIRMED by prediction. The steward reran 89cbc6a on the exact run designs
and got the same numbers, and the added parts do not enter the predicted
quantities.

Two Combat Lab starts on base2400 (`tools/fleetlab/combatlab build`), each
generated once per cycles value 20000, 30000, 14000, 10000, 7000 and 5000
(`tools/fleetlab/pinned-turn`). That gives 6 different battle streams per start.
Raw evidence is in stars-oracle-apparatus `evidence/cb057`.

## Setups

- `cb057q1.spec` (Q1). Player 1 is JOAT with Regenerating Shields, at
  tech 26.
  - Split DD: a Destroyer with one Organic Armor in its general-purpose slot
    and one in its armor slot.
  - Pair DD: a Destroyer with both Organic Armor in its armor slot.
  - There are three one-ship fleets of each. Each ship carries one Laser and
    uses a plan whose targets miss the attacker, so it stays on the board
    without firing.
  - Player 0's two Laser Battleships fire at them in deep space.
  - The Laser keeps the Destroyers on the board (unarmed tokens disengage).
    It does not change their armor.
  - The armor is read from the damage units the Laser hits leave.
- `cb057q23.spec` (Q2 and Q3). Both players are JOAT with no cost LRT, at
  tech 26.
  - Q2 is at player 0's planet.
    - Torp Star: a Death Star starbase with 32 Delta Torpedoes and 16 Battle
      Nexus (computer 99).
    - Probe BB: a computer-0 Battleship with 6 Beta Torpedoes.
    - Targets: 20 Battleships with 4 Mole-skin Shields, 1 Laser and 6
      Superlatanium.
    - The shields make a salvo's hit count readable as shield damage, 13 per
      hit.
  - Q3 is in deep space.
    - Firer: one Heavy Blaster Destroyer, primary target any.
    - S2: 16000 Battleships with 12 Omega Torpedoes, cost 640, armor 2000,
      on a plan that never fires.
    - S1: 10000 unarmed Destroyers with a Long Hump 6, cost 11, armor 200.

## Results

| Q | Prediction (89cbc6a) | Observed | Status |
|---|---|---|---|
| 1 | Split DD armor 374 (halved per slot); Pair DD 375 | Every hit was at distance 1 (dp 9). Split DD fits 372–374 in all 6 streams, and only 374 in the 24-hit run. Pair DD fits 375–376 (3 streams). The parts' total halved once, 375, is excluded for the Split DD. | MEASURED |
| 2 | One record per salvo: 32 hits, 0 misses, no kill, no draw | In every stream, rounds 0–3: shield damage exactly 416 (32 × 26/2), no miss record, no kill. That is 24 salvos and 768 torpedoes, all hits. The battle replays from the pinned stream only when these salvos draw nothing: exactly one start fits, at the draw offset expected when nothing earlier in the year draws. With 32 draws per salvo, no start fits. | MEASURED |
| 3 | The beam picks S1 (both capped at 10^7, lower toughness) | In 4 streams, 14 shots had both stacks within the Blaster's 3 squares, and all 14 hit S1. In 2 streams S1 was never in reach together with S2. Shots with one stack in reach hit that stack. Both stacks share one capped cost, reached at or below 10,240,000; the value 10^7 is not shown. | MEASURED |

Q3's capped scores are 10^9/(A + 1): 499 for S1 and 31 for S2. Uncapped
(110,000 and 10,240,000 × 100/(A + 1)) they would be 5 and 32, so S2 would
be chosen.
