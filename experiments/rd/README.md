# RD: race design corpus (predictions committed before the runs)

Question: how the original game values a race design (advantage points and
the leftover points spent at game start), what it does with an illegal or
malformed race when a game is created, what it does when an existing game
contains one (the turn-time penalty), and what the Random race produces.

Predictions are the stars-decomp race reading, restated here as behavior
before any RD run. Raw race files, game files and dumps go to the private
apparatus (`evidence/rd/`); this directory holds only the case tables and
game definitions.

## RD-1..RD-6: new games (decomp RW01..RW06)

`rwNN.def` = the stars-elegy new-game definition (`docs/ORACLE.md`, "New
games from a definition file"), run with `tools/fleetlab/new-game rwNN.def
OUT 20000 RACEFILES...`. The race files are one base race (apparatus
`evidence/ob/newgames/PG000.R1`) with fields rewritten; their settings are
in `races.tsv`:

- `predicted points`: the race's advantage points.
- `predicted outcome`: `L n` = the leftover points the game spends at
  creation, `min(50, points)`. RD-1..RD-3 hold 48 races with distinct L in
  1..50, one per case, so each case is identified by its own L. All use
  spend 0 (surface minerals), so L shows in the homeworld's surface
  minerals: the smallest mineral gains `10·L/4 + (10·L mod 4)` kT and all
  three gain `10·L/4` more (integer division).

Cases in `races.tsv` cover every growth-table row (3..20), immunities, TT,
a narrow habitat axis, factory and mine economy settings, colonists per
resource 700..2500, AR, NAS with three PRTs, LRT combinations, research
cost settings and every PRT.

RD-4 (rw04) adds the boundaries:

| Race | Prediction |
|---|---|
| rw04a, 0 points | legal, L 0 |
| rw04j, 50 points / rw04i, 51 points | L 50 / L 50 (capped) |
| rw04b (−1), rw04c (−1433) | illegal: replaced at creation by the default race (JOAT, growth 15, 15–85 on every axis, the standard economy and research), with a computer-chosen name and L 25 |
| rw04d, habitat centre off its range midpoint by one | kept, centre repaired, race flag 0x10 set |
| rw04e, race stat 15 = 1 | kept, stat 15 reset to 0, flag 0x10 |
| rw04f, growth 0 | kept, growth set to 1 (then 5851 points, L 50), flag 0x10 |
| rw04g, rw04h, spend 5 and 6 | act as spend 0 (surface minerals) |
| rw04k..m, wizard Random race | a generated race with 0..50 points and a computer name |
| rw04n, Random race named Zorgon | a generated race, 0..50 points, keeps the name Zorgon |
| players 14, 15 (computer players) | unaffected by the legality rules |

RD-5 and RD-6 (rw05, rw06): Random races (and computer players) in
2- and 3-player-size universes; each lands at 0..50 points. The decomp
predicts each generated race exactly; that comparison is private.

## RD-P1..RD-P10: turn-time penalty (decomp RP-1..RP-10)

Base: apparatus `evidence/kx001/raw/A1/before/PG001.HST` (player 0: SS,
growth 10, 245 points). Each case: `scripts/oracle/hst-edit edit PG001.HST
OUT.HST ARGS`, then one pinned year (`tools/fleetlab/pinned-turn`, cycles
20000).

"Punished" means: message 0x117 to the offending player, message 0x182 to
every other player, race flag 0x10 set, and the race changed as listed
(colonists per resource raised so the race reaches at least 500 points;
growth lowered when that is not enough).

| Case | hst-edit args | Points after the edit | Prediction |
|---|---|---|---|
| RD-P1 | `stat=2:5/5:2` | −444 | punished: colonists per resource 2500, growth 7 |
| RD-P2 | `stat=1:15/2:5/3:25/4:25/5:2/6:25` | −2092 | punished: 2500, growth 4 |
| RD-P3 | RD-P2 + `/8:2/9:2/10:2/11:2/12:2/13:2 lrt=a000006d` | −3667 | punished: 2500, growth 3 |
| RD-P4 | `hab=51,50,50,15,15,15,85,85,85` | 245 | punished (repair): centre back to 50, colonists 1700 |
| RD-P5 | `stat=15:1` | 245 | punished (repair): stat 15 = 0, colonists 1700 |
| RD-P6 | `stat=0:26` | 845 | punished (repair): colonists 2500, nothing else changes |
| RD-P7 | `prt=10` | 299 | punished (repair): PRT JOAT, colonists 1600 |
| RD-P8 | `hab=40,50,50,-5,15,15,85,85,85` | 212 | punished (repair): gravity 0–85, centre 42, colonists 1800 |
| RD-P9 | `stat=0:9/1:8/4:12` | 0 | not punished, unchanged, no messages |
| RD-P10 | `stat=0:14/1:7/4:19` | −1 | punished: 2500, growth 9 |

RD-P4..RD-P8 test that a malformed race with positive points is still
punished. A second year after a punished case should change nothing.

## Results

`docs/PARITY.md`, "Race design". All new-game predictions held: every
generated field of RD-1..RD-6, including each race and name. RD-4 ran once
the three race files with bad checksums were rewritten. Seven of ten
penalty cases held. RD-P5, P6 and P7 were not punished: the fields were
clamped silently.

## Follow-up: RD-7 and RD-P11..RD-P12 (committed before the runs)

From the race decomp's reconciliation (stars-decomp #21 at f1daf60,
RACES.md in stars-elegy #49): three cases still untested.

### RD-7: AR leftover spends (new game `rd07.def`)

Five human AR races, identical (34 points, so L 34) except race stat 7,
the leftover spend 0..4 (`racelab edit rw02m.r1 OUT spend=N`), plus one
computer player. An AR homeworld starts with no mines, factories or
defenses.

| Player | Spend | Prediction | Rules out |
|---|---|---|---|
| 0 | 0 minerals | surface 676/279/426 → 761/449/511 (the smallest +170, the others +85, as RD-1) | |
| 1 | 1 concentrations | 98/88/85 → 107/97/111 (+17 on the lowest, then +9 on all); minerals unchanged | |
| 2 | 2 mines | **no mines** (0), minerals and concentrations unchanged: the spend is lost | 17 mines kept; minerals instead |
| 3 | 3 factories | **no factories** (0); spend lost | 6 factories |
| 4 | 4 defenses | **no defenses** (0); spend lost | 3 defenses |

(The generator applies the spend, then sets an AR homeworld's installations
to 0.) Numbers are the decomp's model for this seed; the comparison is
`universe.py check`.

### RD-P11: growth 0 in a running game

The RD-7 start, `hst-edit ... growth=0` on player 0 (AR, 34 points), one
pinned year. Prediction: punished. Message 0x117 to player 0, flag 0x10
set, growth reset to 1. At growth 1 the race is far above 500 points, so
nothing else changes (colonists per resource stay 1800). The other
growth repairs (< 0, > 20) are silent; growth 0 is not.

### RD-P12: penalty messages with several players

The RD-7 start, player 0 edited to negative points. RD-P1's arguments do
not make this race negative, so the edit is `stat=0:1/1:1` (colonists per
resource 100 and factory output 1, both below their ranges: −1058 points
as written). One pinned year (both edits use `planet=81`, player 0's
homeworld, since hst-edit's default planet 7 is not owned here).
Prediction: player 0 gets 0x117; **every other player** (the four humans
and the computer player) gets 0x182 "hacked race discovered". Player 0 is
first clamped silently into range (factory output 5, colonists 700), is
still negative, and is then repaired: colonists raised to 2500, growth
lowered to 7 (985 points), flag 0x10.

### Follow-up results

Evidence: stars-oracle-apparatus `evidence/rd/rd07`, `rp11`, `rp12`.

- RD-7: held. `universe.py check` 93 match, 0 mismatch. Players 2, 3 and 4
  (spends 2, 3, 4): 0 mines, factories and defenses; surface 676/279/426
  and concentrations 98/88/85 unchanged. Player 1: concentrations
  107/97/111. Player 0: surface 761/449/511.
- RD-P11: held (punished; growth 1, colonists 1800).
- RD-P12: held for the humans (0x117 to player 0; 0x182 to players 1..4;
  colonists 2500, growth 7). The computer player's `.M6` carries no
  message block, so its 0x182 is not observable.

## Round 3: the remaining BINARY-ONLY rules (committed before the runs)

From the BINARY-ONLY sweep of `docs/RACES.md`. Predictions are
stars-decomp `tools/races.py` (20e93b8) for the penalty cases and
`tools/universe.py` for RW08; the model outputs and race files are in
the apparatus (`evidence/rd/round3/`, ff01ff25).

### RW08: creation repairs (new game `rw08.def`)

Small map, seed 808: three human races edited from PG000.R1 with
`racelab edit` (all legal as written), plus one computer player.

| Player | Edit | Points | Prediction | Rules out |
|---|---|---|---|---|
| 0 | `hab=50,50,50,-1,40,40,85,60,60` (gravity low = immune marker, centre and high not) | 413 | kept; gravity **immune** (centre and high set to the marker), tampered flag | a numeric clamp of −1 to 0 |
| 1 | `hab=67,50,50,15,15,15,120,85,85` (gravity high 120) | 218 | kept; gravity 15–100, centre 57, tampered flag | high kept at 120; race replaced |
| 2 | `growth=25 stat=0:25` | 159 | kept; growth **20**, colonists 2500, tampered flag | growth 25 kept |

The whole game (planets, homeworlds, the three races as repaired) is
predicted by `universe.py`.

### RD-P13..RD-P19: running-game clamps and the tampered flag

Same base and method as RD-P1..P10 (`PG001.HST`, one pinned year).

| Case | hst-edit args | Points after the edit | Prediction |
|---|---|---|---|
| RD-P13 | `growth=25 stat=0:25` | 159 | **silent**: growth 20, colonists 2500, no message, no flag |
| RD-P14 | `growth=25` | −440 | growth clamped to 20 first (still negative), then punished: colonists 2500, growth 16 (502), flag 0x10 |
| RD-P15 | `researchPct=150` | 245 | research share 15%, silent |
| RD-P16 | `hab=67,50,50,15,15,15,120,85,85` | 218 | punished (repair): gravity 15–100, centre 57, colonists 1800 (538), flag 0x10 |
| RD-P17 | `hab=50,50,50,-1,15,15,85,85,85` | −72 | punished: gravity immune, colonists 2500 (527), flag 0x10 |
| RD-P18 | `growth=-3` | 7565 | **silent**: growth 1, no message, no flag (unlike growth 0, RD-P11) |
| RD-P19 | RD-P1's edit, run for two years | −444 | year 1 as RD-P1 (colonists 2500, growth 7, flag); **year 2 unchanged, no 0x117** (already tampered, points positive) |

### RD-P20: a computer player's repair

Base: the AP game (apparatus `evidence/ai/ap/new/raw/AP01.HST`; player 1
is a computer player whose race scores −1173). Edit `player=1 planet=108
hab=61,29,-1,31,5,-1,93,53,-1` (gravity centre 61, one below the
midpoint 62). One pinned year. Prediction: centre back to 62 and the
tampered flag set, but **no message and no other change**: colonists per
resource, growth and research costs stay as they were, although the race
is negative.

### Round 3 follow-up: RD-P21 (committed before the run)

RD-P19's second year sent message 0x117 again although the race was
already marked tampered, had 1042 points and was not changed (prediction:
no message). Candidate: the penalty message goes to a human player every
year while the race carries the tampered flag, whether or not anything is
repaired. RW08's three human races carry the flag from creation (positive
points, nothing left to repair).

RD-P21: RW08 (`evidence/rd/rw08`), one pinned year. If the candidate
holds: 0x117 to players 0, 1 and 2, races unchanged. If 0x117 needs a
punishment or a repair that year: no 0x117, races unchanged. The
candidate is the prediction. RD-P19 year 3 is run alongside: the
candidate predicts 0x117 again, race unchanged.

### Round 3 results

Evidence: stars-oracle-apparatus `evidence/rd/rw08`, `rp13`..`rp20`,
`rp19-y2`, `rp19-y3`, `rp21`. Public record: `docs/PARITY.md` "Race
design", Round 3.

- RW08: held (`universe.py check` 65 match, 0 mismatch; all three races
  kept, repaired as predicted, flag 0x10).
- RD-P13..RD-P20: held (`races.py turn` 1/1 each; messages as predicted:
  0x117 in P14, P16, P17, P19 year 1; none new in P13, P15, P18, P20).
- RD-P19 year 2 first looked like a miss (0x117 in the turn file). The
  turn file carries the previous year's messages over when no orders were
  submitted: years 1, 2 and 3 held 3, 6 and 9 messages, each block
  starting with the previous one. RD-P21 showed the same (RW08's eight
  creation messages, then two new ones: 0x03f, an owned planet's empty
  queue, and 0x159, Super Stealth spying). So the original prediction held
  (no new 0x117, race unchanged in years 2 and 3), and the RD-P21
  candidate (a new 0x117 every year while flagged) is ruled out: no new
  0x117, races unchanged.
