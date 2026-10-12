# CB-058: the 0-hit torpedo record, cargo with lost ships, salvage at two points, the Langston Shell under RS, a Death Star's reach

Lane D's next combat questions. Its predictions were pushed first, in elegy
eaa474e (`engine/combat_cb058_test.go`), and fetched at 20:01:19Z on
2026-10-12. Some run designs differ from the tests' designs so that the
answer can be read off the battle record. Elegy's numbers for those exact
designs were computed from eaa474e and pushed to the apparatus at 20:04:55Z,
before the runs began at 20:05:02Z. The exception is Q4: the numbers pushed
for it were for the test's Small Freighters, not run B's Laser Destroyers.
Run D (the Q1 rerun) was pushed at 20:11:24Z, the same second as its
self-reported start. Q1's numbers were already in the first push.

There are four Combat Lab starts on base2400. Each was generated at cycles
20000, 30000, 14000, 10000, 7000 and 5000. Raw evidence is in
stars-oracle-apparatus `evidence/cb058`.

## Setups

- `cb058a.spec`: Q1 (first try), Q3 and Q6.
  - Q3: four Large Freighters carrying 1000/700/333 kT and 500 kT of
    colonists, against one Heavy Blaster Destroyer, in deep space.
  - Q6: a Death Star with 8 Heavy Blasters at player 0's planet, against
    four Laser Destroyers.
- `cb058b.spec`, Q4: two deep-space points.
  - X (1020,1230): player 0's fleet 1 and player 1's fleet 4.
  - Y (1000,1400): player 0's fleet 3 and player 1's fleet 2.
  - Player 1's Destroyers are on a plan that never fires, so they stay and
    are destroyed.
  - The spec's comment says X has the larger y. That is wrong: X has the
    smaller y.
- `cb058c.spec`, Q5: player 1 has Regenerating Shields. It has two
  one-ship fleets of each of these designs:
  - a Rogue with 3 Langston Shells in its shield-or-armor slot;
  - a Battleship with 3 Langston Shells in its shield slot;
  - a Rogue with 3 Organic Armor in its shield-or-armor slot.

  Each carries a Laser and a plan that never fires. Player 0's Battleship
  with 6 Mega Disruptors fires at them.
- `cb058d.spec`, Q1: three Alpha Torpedo Destroyers (computer 0) against a
  Battleship with 6 Jammer 50s (jammer 95, no shields), on the default
  plan so that it closes in.

## Results

| Q | Prediction (eaa474e) | Observed | Status |
|---|---|---|---|
| 1 | A missed torpedo writes one hit record with 0 hits, 1 miss and no damage | Run A's battle had no actions: no one closed in. In run D, the 270 one-torpedo salvos each wrote exactly one record. The 268 misses were flagged 0x80 with no change; the 2 hits added 1 unit each. | CONFIRMED |
| 2 | Token cap with three players, or with a starbase | Not run: CB-042 (three players) and CB-043/CB-044 (a starbase, a skipped multi-design fleet) measured these setups | see COMBAT.md "Token cap" |
| 3 | Shares by cargo capacity per kill event (pre-pushed table) | Kill events of one Hauler each, in rounds 8–11, in every run. The salvage was 764/528/257: the pre-pushed shares, plus a third of each hull, less a quarter per event. All cargo lost with the last ship would give 762/525/258. The per-event shares were pushed before the run; the total is eaa474e applied after the run to the observed kill events. | CONFIRMED |
| 4 | Number 0 at player 0's fleet 1's point, 1 at the other | Number 0 at X and 1 at Y, in every run. Each held 6/4/2. This is not by the victims' lowest fleet; ascending y also fits. | MEASURED, consistent with eaa474e (the pre-pushed numbers were for other victims) |
| 5 | Shell Rogue 645 (by part kind), not 547 (by slot kind); Shell BB 2195; Organic Rogue 712 | All 90 Mega Disruptor hits replay (shield damage, units, kills) only with 645, 2195 and 712. With 547, 2–4 hits per run fail. Shields 525. | CONFIRMED |
| 6 | Reach 4; armor 1500 | No shot while the nearest enemy was 5 away; a shot at 4, in every run. The 40 Laser hits on the starbase fit armor 1126–1500. | reach CONFIRMED; armor MEASURED as consistent |

Runs of the same start gave the same Q3, Q4 and Q6 outcomes at every
cycles value. Only Q1's single hits and the battles' other details varied.
