# CB-060 (LW): late-tech weapons

Questions (from Elegy lane D's late-weapon coverage, where these rules had
no recorded battle or were BINARY-ONLY):

- G1: does a gatling skip a secondary-type target while a primary-type
  target is in reach?
- G2, G3: Big Mutha Cannon and Mini Gun damage, with no dropoff.
- S1: the dropoff of the Phased and Syncro Sappers, and no armor damage.
- S2: does a sapper shot that strips a stack's last shields carry on?
- S3: does a sapper with only unshielded targets hold fire?
- B: the damage, range and firing order of eight plain late beams.
- N: the initiative and computer of a ship with one Battle Nexus.

Existing evidence did not answer G1: every gatling plan in CB-002 to
CB-006 had primary "any" and secondary "none".

**Predictions, pushed before the runs** (private apparatus c3d48b65,
committed 2026-10-13T01:38:10Z, the push returned by 01:38:12Z; the runs
started 01:38:15Z), for the exact start. Elegy's numbers are from elegy
387c622.

**Setup.** `lw.spec` (`combatlab build` on the 2-player Combat Lab base):
- Players 0 and 1 at tech 26 in every field, mutual enemies.
- Each case is its own deep-space battle.
- Every player-0 ship is a Battleship with no computer, capacitor or
  shield, and one weapon slot filled.
- Every player-1 target except in S3 is a Battleship with 4000 shields a
  ship and no deflector, so beam and gatling damage reads exactly as
  shield damage.
- Player 1's held stacks are on a plan that never fires; its approachers
  attack.
- One pinned year at cycles 20000, 30000, 14000, 10000, 7000 and 5000.

Distances are read from the battle record, from each token's square at
the time of the shot.

| Case | Setup | Observed | Result |
|---|---|---|---|
| G1 | 1 Gatling Neutrino Cannon (damage 80, range 2), plan primary "armed ships", secondary "any". Player 1: A, armed with 1 Laser, and F, unarmed, both held. | 3 of 6 streams had a shot with both in reach: round 4, A at distance 1, F at 2. Each wrote a record on A and a record on F, 80 shield damage each. F left the board in round 5 in every stream. Every other shot had only A in reach. | A gatling also hit the secondary-type target while a primary-type one was in reach: CONFIRMED by prediction (3 streams). Elegy's rule (primary only) fails. |
| G2 | 1 Big Mutha Cannon. Player 1: T1 held, T2 armed and attacking. | 204 on T2 at distance 0 and 1, every shot, 6 streams. T1 was never within 2 at a shot. | 204 with no dropoff at 0 and 1: CONFIRMED by prediction. Distance 2 and two targets in one shot NOT RUN. |
| G3 | As G2 with 1 Mini Gun | 13 at 0 and 1, every shot | As G2 (dropoff would give 12 at 1) |
| S1 | 2 Phased Sappers and, in a second fleet, 2 Syncro Sappers, against 8 held Battleships (32000 shields) | Phased: 409, 396, 379 at distance 1, 2, 3. Syncro: 1049, 1017, 973. Armor damage 0 in every record. | `(100 − trunc(10x/3))·dp/100`, truncated once, and shields only: CONFIRMED by prediction for distances 1–3. Distance 0 NOT RUN. |
| S2 | 2 Syncro Sappers. Player 1: L with 300 shields, and M, 2 Battleships with 4000 shields each, both held. | The shot that took L's 300 then wrote a record on M in the 5 streams where M was within reach: 673 with L and M at 3; 685 with L at 2 and M at 3; 725 with L at 1 and M at 2. In 10000, M was 6 away and the shot stopped after L. | A sapper shot that strips the last shields carries on to another target in reach: MEASURED. Elegy's no-carry rule fails. |
| S3 | 2 Pulsed Sappers. Player 1: an unshielded armed Destroyer (attacking) and an unshielded unarmed Battleship. | No sapper record in any stream. The Destroyer fired at the sapper ship in every round from 4 to 15. | CONFIRMED by prediction |
| B | One firer each of the eight beams below, against 20 held Battleships | Every value seen matched; see the table below. No firer fired beyond its range. In all 12 rounds with two or more firers, the order was by weapon initiative, highest first, ties in reverse token order. | Values CONFIRMED by prediction for the distances seen (no shot at distance 0). The firing order is CONFIRMED by prediction. |
| N | 1 Alpha Torpedo and 1 Battle Nexus | The token had initiative 13 and computer 50. Every other player-0 Battleship token had initiative 10 and computer 0. | Initiative +3 and computer 50: CONFIRMED by prediction |

Beam damage seen in case B (shield damage at each distance):

| Part | Part initiative | x = 1 | x = 2 | x = 3 |
|---|---|---|---|---|
| Myopic Disruptor (169, range 1) | 9 | 152 | – | – |
| Disruptor (169, range 2) | 8 | 160 | 152 | – |
| Mega Disruptor (169, range 3) | 6 | 163 | 158 | 152 |
| Mini Blaster (66, range 1) | 9 | 59 | – | – |
| Mark IV Blaster (66, range 2) | 7 | 62 | 59 | – |
| Heavy Blaster (66, range 3) | 5 | 64 | 62 | 59 |
| Streaming Pulverizer (433, range 1) | 9 | 389 | – | – |
| Anti-Matter Pulverizer (433, range 2) | 8 | 411 | 389 | – |

Interpretation of S2 (not pushed before the runs): the three carried
amounts fit `COMBAT.md` "Beams" step 5, with "stripped of its shields" in
place of "died". Take the 1082 at the shot, `dp` the damage at L's
distance and `L = dp − 300`. Then `R' = R·L/dp` is applied to M with M's
own dropoff:
- 1082·673/973 = 748, then 90% gives 673;
- 1082·717/1017 = 762, then 90% gives 685;
- 1082·749/1049 = 772, then 94% gives 725.

Raw evidence: private apparatus, `evidence/lw`.
