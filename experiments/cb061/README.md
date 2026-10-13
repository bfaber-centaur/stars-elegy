# CB-061 (PQ-1): the races count in a 3+-player battle summary

Question (from Elegy lane D, where the rule was an ASSUMPTION): in the
multi-race summaries 0x0a4–0x0a8 (`MESSAGES.md` "Battles and bombing"),
the slot after the location is a count of races. When a player is present
but does not fight, is that count every player present (P) or only the
players who fought (Q)? CB-059 B3 answered the 2-fighter form only.

**Predictions, pushed before the runs** (private apparatus):
- PQ-1: 3479c85, committed 2026-10-13T02:41:39Z, the push returned by
  02:41:41Z; runs started 02:41:48Z.
- PQ-1b: 0c957e5, committed 02:45:14Z, the push returned by 02:45:17Z;
  runs started 02:45:23Z.

Elegy's prediction was P, from lane D's spec.

**Setup.** `pq1b.spec` (`combatlab build` on the 16-player base, game
CB16P):
- Players 0–3 at tech 26 in every field. Players 0, 1 and 2 are mutual
  enemies; player 3 has no relations (neutral to all, and all neutral to
  it). Plan 1 of players 0–2 attacks enemies; player 3's plans attack
  nobody.
- M: at player 3's homeworld, which has an unarmed Space Station and no
  defenses. Player 0: 1 Shield BB (4000 shields, 3 Lasers) and 1 Plain DD
  (1 Laser). Players 1 and 2: 2 Shield BB each. No player-3 fleet.
- C (control): the same three fleets (a second fleet of each of players
  0, 1 and 2) in deep space at (1020,1100). Player 3 had nothing there:
  no fleet, planet or starbase, so it was absent from that battle.
- PQ-1 was the same with a Scout in place of the Plain DD.
- One pinned year at cycles 20000, 30000, 14000, 10000, 7000 and 5000.

Message parameters as stored: the location (two values), the races count,
then four counts.

| Run | Case | Branch | Players 0, 1, 2 | Player 3 | Result |
|---|---|---|---|---|---|
| PQ-1 | M | not taken in any stream: nothing was destroyed (the Scout was never hit) | 0x0a8, races 3 | 0x0a8, races 3 | MEASURED (6 streams) |
| PQ-1 | C | not taken in any stream: nothing was destroyed | 0x0a8, races 3 | none | MEASURED (6 streams) |
| PQ-1b | M | all 6 streams: player 0's Plain DD destroyed, nothing else; no shot at the starbase | 0x0a8, races 3 | 0x0a8, races 3 | Q: CONFIRMED by prediction (6 of 6). Elegy's P fails, and so does "player 3 gets no summary". |
| PQ-1b | C | all 6 streams: player 0's Plain DD destroyed | 0x0a8, races 3 | none | CONFIRMED by prediction (6 of 6) |

The four counts after the races count in PQ-1b M (MEASURED, all 6
streams):

| Recipient | Counts |
|---|---|
| Player 0 | 1, 2, 0, 5 |
| Players 1 and 2 | 0, 2, 1, 5 |
| Player 3 | 0, 1, 1, 6 |

Interpretation (not pushed before the runs): the counts are the
recipient's losses, the recipient's ships, everyone else's losses and
everyone else's ships. The uninvolved starbase is one of "everyone else's
ships" for the three fighters (5 = 4 Shield BB + the starbase), and the
starbase owner's own one ship in its message, with the six fighting ships
as everyone else's. In C the fighters' totals were 2 and 4.

Raw evidence: private apparatus, `evidence/pq1`.
