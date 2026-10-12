# CB-053: which tech prices a ship destroyed in a year its owner levels up? (CB-Q3)

Question from the engine sprint (coordinator's CB-Q3): battle salvage and
target choice use the design's cost for its owner (`COMBAT.md` "Design
cost", `COMPONENTS.md` "Cost for an owner"), which depends on the owner's
tech through miniaturization. When research raises a level in the same
year, before the battle (`KERNEL.md` "Turn order": research checks in
steps 2 and 4, battles after production), is the cost at the tech from
before or after the level? RG-001 year 5 has one MEASURED observation for
the old tech (player 1's Mini-Colony Ship, lane D).

Two players, enemies, Combat Lab base, deep space at (1020,1230).

- Player 0 (the victim's owner): tech 6 in every field but biotech 5, so
  its lowest level is 5. Current field biotech. Planet 17 has no queue, so
  all its resources go to research. Level 6 costs `550 + 10·35 = 900`.
- Victim: 100 "Victim" ships, Small Freighter hull, Long Hump 6, Tritanium.
  The hull and the armor require nothing, so their miniaturization uses the
  owner's lowest level: **20% at level 5 and
  24% at level 6**. Long Hump 6 uses propulsion (6 − 3 = 3, 12%) either way.
  Mineral cost per ship (ironium, boranium, germanium):
  - at the old tech (lowest level 5): hull 10/0/14, engine 4/0/1, armor
    4/0/0 → **18/0/15**;
  - at the new tech (lowest level 6): hull 9/0/13 → **17/0/14**.
- Player 1: 40 Phaser destroyers at tech 26, plan "Enemies" (tactic 5).

Variants (one spec each, `combatlab build` on the Combat Lab base):

| case | player 0's stored biotech research | biotech after the year |
|---|---|---|
| `cb053-ctl` | 0 | 5 (no level) |
| `cb053-up` | 899 (one short, levels in production) | 6 |
| `cb053-pre` | 900 (already enough when the year starts) | 6 |

Pinned at cycles 20000 and 30000.

## Predictions (committed before the runs)

- All 100 Victims are destroyed (each has 75 armor). The battle record
  gives each kill event's ship count `k`.
- Salvage per kill event, per mineral: `S = trunc(k·c/3)`, of which a
  quarter is lost in deep space (`S − trunc(S/4)`); the salvage object
  holds the sum over events.
- **Old tech:** `c` = 18/0/15 in every variant. **New tech:** 17/0/14 in
  `cb053-up` and `cb053-pre`. The control is 18/0/15 in any case, and
  fixes the per-event arithmetic.
- Expected from RG-001 (one observation): the old tech in `cb053-up`.
  `cb053-pre` is open: a level taken in step 2 may already apply.
- Biotech ends at 6 in `cb053-up` and `cb053-pre`, 5 in the control; if
  not, the setup failed and the case is not read.
- The kill events are random (samples); the salvage given the events is
  not.

## BET arm (added before any run, after stars-elegy #141)

#141 reads the design cost as fixed when the file loads, at the tech from
before research, except that a Bleeding Edge Technology owner's salvage
recomputes the cost after research (BINARY-ONLY). Two more variants, the
same as `cb053-ctl` and `cb053-up` with player 0 given BET (`lrt 0
0x1000`): `cb053-bet-ctl` and `cb053-bet-up`.

With BET, miniaturization is `min(5·m, 80)%` (`COMPONENTS.md`). Long
Hump 6 (m = 3, 15%) is 4/0/1 either way. Cost per Victim:

- lowest level 5 (25%): hull 9/0/13, armor 4/0/0 → **17/0/14**;
- lowest level 6 (30%): hull 8/0/12, armor 3/0/0 → **15/0/13**.

Predictions:
- `cb053-up` (no BET): **old tech**, 18/0/15.
- `cb053-bet-up`: **new tech**, 15/0/13.
- `cb053-bet-ctl`: 17/0/14.

## Results

Cycles 20000 and 30000 gave the same battle in every variant: Player 1's
destroyers killed 24 Victims in two kill events of 12 each, and 76
survived the battle. So the prediction "all 100 destroyed" failed, which
does not affect the reading: salvage per event is
`trunc(12·c/3) − trunc(trunc(12·c/3)/4)`.

| case | biotech after | salvage (Fe/B/G) | old-cost value | new-cost value |
|---|---|---|---|---|
| `cb053-ctl` | 5 | 108/0/90 | 108/0/90 | (no level) |
| `cb053-up` | 6 | **108/0/90** | 108/0/90 | 102/0/84 |
| `cb053-pre` | 6 | **108/0/90** | 108/0/90 | 102/0/84 |
| `cb053-bet-ctl` | 5 | 102/0/84 | 102/0/84 | (no level) |
| `cb053-bet-up` | 6 | **90/0/78** | 102/0/84 | 90/0/78 |

- **CONFIRMED (2 of 2 streams):** without BET, a ship destroyed in the
  year its owner levels up a miniaturization field is priced at the tech
  from before the year's level, both when the level comes from this
  year's research (`cb053-up`) and when the stored research already
  covered it at the start of the year (`cb053-pre`).
- **CONFIRMED (2 of 2 streams):** with Bleeding Edge Technology the same
  kill is priced at the new tech (`cb053-bet-up`), as stars-elegy #141
  reads it.
- Every per-event value matched `S − trunc(S/4)` with
  `S = trunc(k·c/3)` and the predicted design costs, so the
  miniaturization rule for these items (20%/24%, and 25%/30% with BET)
  also held.
- The kill events are random; the salvage given the kills is not.
