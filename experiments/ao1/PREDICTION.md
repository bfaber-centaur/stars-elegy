# AO-1 prediction: component announcements within one level (pushed before the runs)

Question (coordinator, from stars-elegy #192, `MESSAGES.md` "Order of the
component messages within one level"): which parts of that order hold?
These parts are BINARY-ONLY:
- where starbase hulls (0x0d0) fall;
- planetary scanners (0x157) before planetary defenses (0x145);
- Total Terraforming never announcing the three ±3 terraforms.

The rule under test, from #192 (merged at f2778b3). After the level message
(0x050), one message per component that the level made available, in
category order:
1. engines, scanners, shields, armor, beam weapons, torpedoes, bombs,
   mining robots, mine layers, orbital parts (0x05f);
2. starbase hulls (0x0d0);
3. electrical, mechanical, terraforming (0x05f);
4. ship hulls (0x078);
5. planetary items by index: scanners 0x157, defenses 0x145, then the
   Genesis Device (0x05f).

Within a category, items go in `data/components.json` index order. A
Total Terraforming race never gets Gravity, Temp or Radiation Terraform
±3. Which components a level makes available, and the race restrictions,
come from `data/components.json`.

## Setups

Each start is built by `combatlab build` on the 2-player Combat Lab base
(`ao1a.spec`, `ao1c.spec`). No production queues, so all resources go to
research. Each researching player starts with exactly the next level's
cost stored (`KERNEL.md` "Level cost"), so it gains one level this year.
The level after that costs more than a year's research.

| Case | Player | Race | Tech before | Level gained |
|---|---|---|---|---|
| (a) | 0 in `ao1a` | JOAT, no LRT (no NAS) | energy 4, electronics 16, biotech 7, others 0 | energy 5 |
| (b) | 1 in `ao1a` | IS with ISB and CE | energy 7, electronics 2, construction 3, others 0 | construction 4 |
| (c) | 0 in `ao1c` | JOAT with TT, CE and LSP | energy 1, weapons 1, propulsion 1, construction 10, electronics 10, biotech 0 | biotech 1 |
| (c) control | 1 in `ao1c` | JOAT with CE and LSP | the same | biotech 1 |

CE and LSP are there for race points. No component in
`data/components.json` is restricted by either.

Runs: one pinned year per start at cycles 20000 and 30000 (4 runs).

## Predicted messages

These are the level and component messages in each player's `.M`, in
order. Other messages are not part of the prediction.

- (a) player 0:
  1. 0x050 energy 5
  2. 0x05f Dolphin Scanner (scanner 8)
  3. 0x05f Cheetah Scanner (scanner 11)
  4. 0x05f Battle Super Computer (electrical 6)
  5. 0x05f Temp Terraform ±7 (terraform 13)
  6. 0x157 Snooper 500X (planetary 7)
  7. 0x145 Missile Battery (planetary 10)
- (b) player 1:
  1. 0x050 construction 4
  2. 0x05f Croby Sharmor (shield 3)
  3. 0x05f Robo-Miner (mining robot 2)
  4. 0x0d0 Space Dock (starbase hull 1)
  5. 0x078 Privateer (hull 11)
  6. 0x078 Fuel Transport (hull 25)

  This is the coordinator's list unchanged: every item's requirements
  are met for IS + ISB at this tech.
- (c) player 0 (TT): 0x050 biotech 1, and no 0x05f.
- (c) control, player 1: 0x050 biotech 1, then 0x05f Gravity
  Terraform ±3, 0x05f Temp Terraform ±3, 0x05f Radiation Terraform ±3.

## What would decide each part

- Starbase hulls: (b) puts Space Dock after Robo-Miner (a mining robot)
  and before the hulls. A starbase hull among the ship hulls, or after
  them, refutes its place.
- Scanners before defenses: in (a), 0x157 comes before 0x145.
- The TT skip: (c) with the control.

A run in which a player gains no level, or more than one, did not take
the stated branch. Its messages are MEASURED, not a test.
