# FS-1

## FS-1: the fleet slot of 0x05b

Question (lane D): what is in 0x05b's fleet slot? The values on record
did not follow the owner (`docs/MESSAGES.md` "Object ids in slots").

Predictions: `PREDICTION.md`, pushed alone in 06676d0. The activity API
shows the push at 2026-10-13T18:25:47Z, and the runs started at
18:26:06Z. Spec: `fs1.spec` (a state edit on CB, 2 players). Raw
evidence: private apparatus `evidence/fs1`. One pinned year at cycles
20000, 30000 and 14000. Every message line is the same in all three
streams; the raw host and player files differ between streams.

| Case | Fleet | Message, slot | Predicted (E) | Observed | Result |
|---|---|---|---|---|---|
| a | 0/3, design 5 | 0x05b, 2 | 2563 | 2563 | CONFIRMED by prediction |
| b | 1/0, design 0 | 0x05b, 2 | 0 | 0 | CONFIRMED by prediction |
| c | 1/1, design 0, followed by 0/9 | 0x05b, 2 | 1 | 1 | CONFIRMED by prediction |
| d | 1/2, design 3 | 0x05b, 2 | 1538 | 1538 | CONFIRMED by prediction |
| e | 1/4, design 3, followed by 1/5 | 0x05b, 2 | 1540 | 1540 | CONFIRMED by prediction |
| f | 0/6, designs 2 and 7 | 0x05b, 2 | 1030 | 9222 | prediction failed; MEASURED |
| m | 0/8, design 15 | 0x05b, 2 | 7688 | 7688 | CONFIRMED by prediction |
| p | 0/7, design 9, at planet 0 | 0x059, 1 | 4615 | 4615 | CONFIRMED by prediction |
| q | 1/6, design 4, at planet 2 | 0x059, 1 | 2054 | 2054 | CONFIRMED by prediction |

Other predicted values: 0x05b's first slot held the new salvage ids
(8192 to 8194 for player 0, 8704 to 8707 for player 1), and 0x028 to
player 0 was (9, 513). Both are CONFIRMED by prediction. 0x028 to player
1 was (517, 516), not the predicted (5, 516). That is MEASURED.

So reading E holds for fleets of one design: the slot is design·512 +
fleet number. Lane D's readings A to D do not fit. f's value is 0x2000 +
2·512 + 6. That bit 13 marks a fleet of more than one design is
inferred, from this one fleet.

MEASURED, not predicted:
- 0x028's follower slot is owner·512 + number (517 for player 1's 1/5).
- 0x140, sent with 0x059 to the planet owner, gave 7 for 0/7 and 518
  for 1/6, also owner·512 + number.

Scope: CB with 2 players, one year, one ship per fleet. The player-count
part of reading D rests on RG-002 year 1 and was not retested.
