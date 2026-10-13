# CB-059 (CB-B): battle-summary assumptions B1–B4, and the battle order (CB-058 Q4b)

Questions (from Elegy lane D's battle summaries, where four rules were
ASSUMPTION, and CB-058's open battle-order question):

- B1: what counts as "hit" in the one-ship texts 0x091–0x095?
- B2: which texts does a 2-player battle send when a single ship dies
  against several (0x0a2, 0x0a3, both BINARY-ONLY), and when both sides
  are wiped out?
- B3: who counts as a player in a "2-player battle" when a third player is
  present but does not fight?
- B4: is a battle summary sent when an Alternate Reality starbase dies?
- Q4b: are battle locations examined in the order of their first fleet, or
  by ascending y?
- Add-on: 0x113 and 0x114 (BINARY-ONLY).

**Predictions, pushed before the runs** (private apparatus 76789105,
committed 2026-10-13T01:13:15Z, the push returned by 01:13:17Z; the runs
started 01:13:24Z), for the exact starts. Elegy's Q4b prediction was
pushed earlier, as elegy 5d2450e (on GitHub by 01:07:19Z, when its CI run
was created). Each case states its hypotheses and the branch a stream
must take for it to decide the case; a stream that took another branch is
MEASURED.

**Setup.**
- `cbb.spec` (`combatlab build` on the 16-player Combat Lab base): players
  0, 1 and 2 at tech 26 in every field. Players 0 and 1 are mutual
  enemies; player 2 is neutral to both. Players 0 and 1 attack enemies;
  player 2's plan attacks nobody. Each case is its own battle at its own
  location.
- `q4b.spec` (`combatlab build` on the 2-player Combat Lab base): CB-058's
  `cb058b.spec` with the two points' y values swapped.
- One pinned year of each start at cycles 20000, 30000, 14000, 10000,
  7000, 5000, 25000 and 40000. The 25000 streams repeated 20000 and 40000
  repeated 30000 in every record and message.

| Case | Setup | Streams that took the stated branch | Player 0 | Player 1 | Player 2 | Result |
|---|---|---|---|---|---|---|
| B1-S | Player 0's Battleship with 4000 shields and 3 Lasers against player 1's Destroyer with 1 Laser | 8 of 8: player 1's ten hits each did 9–10 shield damage and no armor damage; player 1's ship died | 0x091 | 0x092 | — | Armor-only reading CONFIRMED by prediction. Elegy's reading (shield damage counts) fails. |
| B1-Z | Player 0's unshielded Battleship with jammers 95 and 3 Lasers against player 1's Destroyer with 1 Alpha Torpedo | 7 of 8: every player-1 record was a 0-hit record with no change; player 1's ship died | 0x091 | 0x092 | — | Elegy's reading CONFIRMED by prediction; "any record counts" fails. |
| B1-Z, other branch | The same | 7000: one torpedo hit for 1 armor unit | 0x093 | 0x094 | — | MEASURED |
| B1-M | As B1-Z with 800 shields and 1 Omega Torpedo | 3 of 8 (14000, 10000, 5000): no torpedo hit; 10 to 15 all-miss salvos, each a miss record with 39 shield damage and then a 0-hit record; no armor damage; player 1's ship died | 0x091 | 0x092 | — | Hit-records-only reading CONFIRMED by prediction. Elegy's reading (miss shield damage counts) fails. |
| B1-M, other branches | The same | 20000, 25000, 7000: one hit with armor damage, player 1 died. 30000, 40000: one hit, both survived | 0x093 / 0x095 | 0x094 / 0x095 | — | MEASURED |
| B2b-1 | Player 0's Battleship with 12 Heavy Blasters against player 1's 4 Heavy Blaster Destroyers and 4 Heavy Blaster Cruisers | 8 of 8: player 0's ship died; player 1 lost 4 of 8 | 0x0a3 | 0x0a2 | — | CONFIRMED by prediction (Elegy) |
| B2b-2 | As B2b-1 with 3 + 3 | 8 of 8: player 0's ship died; player 1 lost 3 of 6 | 0x0a3 | 0x0a2 | — | CONFIRMED by prediction (Elegy) |
| X | Player 0's Battleship with 4000 shields and 12 Heavy Blasters against player 1's 2 Laser Frigates and 2 Laser Destroyers | 8 of 8: all four of player 1's ships died in round 0; player 0 lost nothing | 0x113 | 0x114 | — | CONFIRMED by prediction (Elegy) |
| B3-SB | Player 2's planet with an unarmed Space Station and no player-2 fleet; player 0's armed Destroyer and player 1's Scout in orbit | 8 of 8: player 0 destroyed the Scout; nothing was aimed at the starbase, which had a token | 0x115 | 0x0a1 | 0x115 | MEASURED. No hypothesis matched: Elegy predicted 0x0a8 / 0x0a6 / 0x0a8. |
| B3-BY | Player 0's armed Destroyer, player 1's Scout and player 2's Scout (attacks nobody) in deep space | 8 of 8: player 0 destroyed player 1's Scout; player 2's Scout was not targeted or in the battle | 0x115 | 0x0a1 | none | MEASURED. No hypothesis matched: Elegy predicted 0x0a0 / 0x0a1 / none. |
| B3-C | B3-BY without player 2 | 8 of 8 | 0x091 | 0x092 | — | CONFIRMED by prediction (control) |
| Q4b | Player 0's fleet 1 and player 1's fleet 4 at X' (1020,1400); player 0's fleet 3 and player 1's fleet 2 at Y' (1000,1230) | 8 of 8: both of player 1's fleets died | | | | First-fleet order CONFIRMED by prediction (Elegy): player 1's salvage number 0 is at X', number 1 at Y'. The battle at X' is the first record, and its summaries come first, in both players' files. |

The count parameters in B3:
- B3-SB: player 0's 0x115 counts an "enemy force" of 2 that lost 1 (the
  Scout and the starbase). Player 2's 0x115 has its own starbase as the
  single ship and the same 2 and 1. Player 1's 0x0a1 counts 2 enemy
  ships.
- B3-BY: player 0's 0x115 counts an enemy force of 2 that lost 1 (both
  Scouts), and player 1's 0x0a1 counts 2. So the bystander's Scout is in
  both fighters' totals, though player 2 got no message.
- The named player was player 2 in both fighters' messages, in both cases,
  and player 1 in player 2's message.

**B4, from existing runs (MEASURED, no prediction record).** CB-041-sf
(`experiments/cb041`, player 1 AR with an Orbital Fort): of 20 preserved
streams, the Fort died in 17. In each of those, player 0 got 0x144 and
player 1 got 0x08e, and neither got a battle summary. In the other 3 the
Fort survived, and they got 0x09c and 0x09b.

**B2a and B2c (both sides wiped out) were not run.** Firing stops once only
one player has live tokens (`COMBAT.md` "Firing", CONFIRMED by replay), so
a 2-player battle can't end with both sides wiped out by fire.

Interpretation (not pushed before the runs):

- **B1:** a side counts as "hit" in 0x091–0x095 only when it took armor
  damage. Shield damage, from beam hits or from torpedo misses, does not
  count. Each sentence covers only the cases run: one ship a side, a Laser
  against 4000 shields, Alpha and Omega Torpedoes against jammers 95.
- **B3:** the text family follows the players who fought (two here). Each
  recipient then compares its own ships with every other ship at the
  location, the starbase and a bystander's fleet included. An uninvolved
  starbase owner got a summary; a bystander fleet's owner did not.

Raw evidence: private apparatus, `evidence/cbb`.
