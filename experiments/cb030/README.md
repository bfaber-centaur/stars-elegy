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
