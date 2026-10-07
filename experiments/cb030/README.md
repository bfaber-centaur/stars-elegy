# CB-030: several movers on both sides

Round 4 (COMBAT.md "Movement order", BINARY-ONLY; the open CB-018 item).
Each player has a fleet of 2 Heavy Destroyers (mass 165, speed code 1)
and 3 Light Frigates (mass 23, speed code 3), all with Lasers, tactic 5.
Pinned at cycles 20000 and 30000.

## Predictions (committed before the run)

Moves per round: heavy 1, 1, 0, 1 (rounds `r % 4` = 0, 1, 2, 3); light 2,
1, 1, 1. Inside a phase tokens move by descending jittered weight, which
for these masses always puts both Heavy tokens before both Light tokens
(165·0.72 > 23·1.28). So the move records of a round, while all four
tokens live, follow (as a subsequence, since a token may not move):

- `r % 4 = 0`: Light, Light (phase 2), then Heavy, Heavy, Light, Light;
- `r % 4` = 1 or 3: Heavy, Heavy, Light, Light;
- `r % 4 = 2`: Light, Light.

The order between the two Heavy (or two Light) tokens depends on the
jitter and is not predicted. Every hit replays with the checker.

## Result

Both seeds (20000, 30000); all 51 and 49 actions replayed with the checker.
Move records per round by class (H heavy, L light, with the owner):

| round | 20000 | 30000 |
|---|---|---|
| 0 | L1 L0 H1 H0 L1 L0 | L1 L0 H0 H1 L1 L0 |
| 1 | H1 H0 L0 L1 | H1 H0 L1 L0 |
| 2 | L0 | L1 |
| 3 | H0 L1 L0 | H0 H1 L1 L0 |
| 4 | H0 H1 L0 | H1 L0 |

Every round is a subsequence of the predicted pattern, and no Light token
moved before a Heavy token inside a phase. The order between the two
Heavy tokens varied (H1 H0 and H0 H1). CONFIRMED in 2 streams.
