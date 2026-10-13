# AO-1: component announcements within one level

Question and predictions: `PREDICTION.md`, pushed in 950c64c. The GitHub
activity API shows the push at 2026-10-13T05:16:03Z, and the runs started
at 05:16:17Z. The rule tested is `MESSAGES.md` "Order of the component
messages within one level" (stars-elegy #192, f2778b3). Raw evidence:
private apparatus `evidence/ao1`. Each start ran one pinned year at
cycles 20000 and 30000.

Every player gained exactly one level, so every stream took the stated
branch. The table lists each player's level and component messages in
file order. The only other message was each homeworld's 0x03f.

| Case | Observed (2 of 2 streams) | Result |
|---|---|---|
| (a) JOAT, no NAS, energy 4 → 5 | 0x050 energy 5; 0x05f Dolphin Scanner, Cheetah Scanner, Battle Super Computer, Temp Terraform ±7; 0x157 Snooper 500X; 0x145 Missile Battery | CONFIRMED by prediction |
| (b) IS + ISB, construction 3 → 4 | 0x050 construction 4; 0x05f Croby Sharmor, Robo-Miner; 0x0d0 Space Dock; 0x078 Privateer, Fuel Transport | CONFIRMED by prediction |
| (c) JOAT + TT, biotech 0 → 1 | 0x050 biotech 1 only | CONFIRMED by prediction |
| (c) control, JOAT without TT | 0x050 biotech 1; 0x05f Gravity, Temp, Radiation Terraform ±3 | CONFIRMED by prediction |

What each case decides:
- (b): the starbase hull (0x0d0) came after a mining robot and before
  the ship hulls (0x078).
- (a): the planetary scanner (0x157) came before the planetary defense
  (0x145), and both came after every 0x05f.
- (c): a Total Terraforming race was not told of the three ±3
  terraforms, which the control was.

The component parameters give each part's category mask and index:
- scanner 2, shield 4, mining robot 128;
- starbase hull 1024, electrical 2048, terraforming 8192;
- ship hull 16384, planetary 32768.

Within a category, the order is ascending index (scanners 8, 11; hulls
11, 25). The Genesis Device's place was not run.
