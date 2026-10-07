# CB-033: a player found out at step 5 keeps firing

Round 4b (COMBAT.md "Rounds" step 5: a player found out keeps its tokens,
and they still fire; procedure step 8: friends join; both BINARY-ONLY).
Setup from the Combat decomp pass (stars-elegy #38, stars-decomp #17).
Five-player game made by `tools/fleetlab/new-game` from `cb5p.def`, deep
space at (1060,1080). Spec: `cb033.spec` (written by `../cb023/gen.py`).
All relations neutral, except that player 2 considers player 0 a friend.

| player | role | ships | plan (tactic 5) |
|---|---|---|---|
| 0 | A, weak | 1 Laser Frigate | attack-who player 1 |
| 1 | E, strong | 4 Phaser DDs (2 Colloidal Phaser, range 3) | attack-who player 0 |
| 2 | F, armed | 1 Phaser Frigate (2 Colloidal Phaser) | attack-who nobody |
| 3 | tough | 3 Tough DDs (1 Laser, 2 Tritanium) | attack-who player 4 |
| 4 | tough | 3 Tough DDs | attack-who player 3 |

Pinned at cycles 8000, 12000, 16000, 20000, 30000 and 50000.

## Predictions (committed before the run)

Attack sets: A {1}, E {0}, players 3 and 4 each other. F is in `P` but
not in `Q` after retaliation; the friends pass gives it A's set, {1}, and
it joins. Nobody names F.

- The record names five players (mask 0x1f, `n` = 5) and F has a token.
  Start squares: A (4,1), E (6,8), F (1,4), player 3 (8,4), player 4
  (2,8).
- E's tokens fire only at A's token, and never at F's. F fires only at
  E. Players 3 and 4 fire only at each other.
- A's frigate is destroyed. In the rounds after that, step 5 finds E out
  (its set names only A) and then F out (it names only E, removed earlier
  in the same check). Players 3 and 4 stay in, so the battle goes on, and
  **F keeps firing at E** in those rounds while E fires at nobody.
- Players 3 and 4 survive to round 15 (each has 3 Lasers against 3
  armored Destroyers), so the battle lasts all 16 rounds.
- Alternatives: if F did not join, the record would name four players
  with no F token (start squares (1,1), (8,8), (1,8), (8,1)); if a player
  found out stopped firing, F would make no fire action after A's death.
- The firing live-token recheck has no observable effect and is not
  tested here.
