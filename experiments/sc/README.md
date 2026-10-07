# SC: scanning and per-player visibility corpus

Oracle tests of the stars-decomp scanning predictions S-1..S-24
(`docs/scanning-predictions.md`, stars-decomp PR #6, branch
`claude/project-thread-q0iccj` at 3b5de74), in the Combat Lab universe
(`docs/ORACLE.md`, "Combat Lab"). Each run is one pinned generation
2400 → 2401 (`tools/fleetlab/pinned-turn`, cycles 20000); nothing here
draws random numbers that matter (S-21 and S-22 are not tested).

```sh
experiments/sc/gen.py CB.XY experiments/sc/runs          # specs + case tables
tools/fleetlab/combatlab build CB.HST runs/sc001.spec start.HST
tools/fleetlab/pinned-turn start.HST BASEDIR OUT
experiments/sc/check.py sc001 CB.XY OUT/after.dump       # per case, then full views
```

## Setup common to every run

- Both players JOAT (unchanged Humanoid race), every tech field 26 unless a
  run says otherwise, research 0%. Both homeworlds have their planetary
  scanner removed (`planet N scanner none`, a new CombatLab key), so only
  the ships named below scan. Fleets are stationary.
- Viewers are player 0. Targets are player 1 Small Freighters with a
  Quick Jump 5 (29 kT) and at most one cloak in the scanner/electrical slot
  (Stealth 31 kT, Super-Stealth 32 kT, Ultra-Stealth 34 kT, Transport
  Cloaking 30 kT), or a Super Freighter with five Ultra-Stealth Cloaks
  ("Ghost"). Freighter viewers avoid the JOAT built-in hull scanner.
- Distances are placed as exact integer squared distances d² from the
  viewer. "Seen" means the fleet appears in the viewer's 2401 `.M` section
  (partial fleet, kind 3, or kind 4 with cargo).

## Model under test (restated from the decomp predictions)

- Ship ranges are the part table (S-1); several scanners on one design
  combine as the truncated fourth root of Σ r⁴ (S-2); a fleet uses the best
  design, without combining stacks or ship counts (S-3). No scanner =
  blind (S-4).
- A fleet at d is seen when d² ≤ R²; an orbiting fleet also needs
  d² ≤ P² (S-6). Normal scanners never report planets; penetrating ones
  report every planet with d² ≤ P² (S-5).
- Cloak: points (Stealth 70, Super-Stealth 140, Ultra 540, Transport 300)
  weighted by stack mass, divided by fleet mass plus cargo (not fuel),
  mapped to percent by the table in `docs/scanning.md` (S-12). A cloaked
  fleet (c%) is seen only if d² ≤ ⌊⌊(100−c)·R²/100⌋·(100−c)/100⌋, and the
  same with P² when it orbits (S-13). Tachyon Detectors multiply c by
  95, 93, … % for 1, 2, … detectors, rounded down (S-14).
- A fleet at exactly the viewer's position is always seen (S-15); a planet
  orbited by a viewer is reported at level 1 (no scanner), 3 (any scanner,
  Bat included) or 4 (Robber Baron) (S-4, S-20). Pick Pocket and Robber
  Baron viewers see the cargo of fleets at their exact position (S-20).
- A planet within P whose starbase cloak c gives d² > ⌊(100−c)²·P²/10000⌋
  is reported without its starbase (S-16).
- Planet scanners use the best planetary scanner the owner's tech allows
  (S-7); Snooper scanners penetrate to half their range (S-8).
- Allies share nothing (S-23).

`sclib.py` implements exactly this; on all 15 start files it predicts the
same per-player views as stars-decomp `tools/scan.py predict` (checked
before any run).

## Runs and predictions (committed before the runs)

`runs/scNNN.spec` is the CombatLab spec, `runs/scNNN.cases` the case
table: case id, viewer, object, expected level (0 = absent), claims, and
the alternative rules (`ALTS` in `sclib.py`) that predict a different
outcome for that case.

| Run | Tests | Content |
|---|---|---|
| SC-001 | S-1, S-2, S-3, S-12, S-13 | Rhino (50): plain, Stealth 35/17/10% (cargo 0/31/70), Super-Stealth 55%, Transport 75%, Ultra 85%, mixed Stealth+plain fleet 18%, Stealth with fuel 130, each just inside and just outside its bound. Two Rhinos on one Large Freighter (59): plain and cloaks at 26/31/45% where the one-step rounding (A2) differs. A fleet with two Rhino stacks and a fleet with two Rhino ships at 55 ly. |
| SC-001F | S-23 | SC-001 with both players friends: identical views. |
| SC-002 | S-4, S-15, S-20 | Blind and Bat viewers sharing a position with a 98% and an 85% fleet, the same at d = 1; blind and Bat viewers orbiting unowned planets; Pick Pocket co-located with a loaded freighter and one 30 ly away; Rhino co-located control. |
| SC-003..007 | S-5, S-6, S-13 | Ferret (185/50), Chameleon (160/45), Dolphin (220/100), Robber Baron (220/120), Elephant (300/200): one viewer with a planet at d² = P², one with a planet at the next representable d² > P²; plain freighters orbiting both; a Stealth freighter orbiting the edge planet and one in deep space at the same distance; every other planet's report. |
| SC-008 | S-1, S-5, S-6 | Mole (100/0) 30 ly from a planet: no planet reports, an orbiting freighter at 30 ly unseen, deep-space freighters at 30, 100 and √10001 ly. |
| SC-009 | S-16 | Dolphin viewers vs player-1 Space Stations with one Stealth Cloak (35%, hidden past d² 4225) and two (55%, past 2025), at the edge and one past it. |
| SC-010 | S-14 | Mole + 0/1/2 Tachyon Detectors vs Transport Cloaking (75%) at d² 625, 626, 841, 842, 900, 961, 962. |
| SC-011..013 | S-7, S-8 | Player 0's homeworld scanner kept; electronics 5, 6 and 10 (energy/bio 3 for the last): plain freighters at 150, 220, 280, 320 ly and just past; in SC-013 every planet within 160 ly reported and freighters orbiting planets within 250 ly seen only within 160. |
| SC-014 | S-4, S-20 | Robber Baron orbiting an unowned planet with a loaded enemy freighter (planet level 4, fleet kind 4 with cargo); Rhino control (level 3, kind 3). |

Specific predictions worth naming (from the case tables):

- SC001-plain: d² 2500 seen, 2501 unseen (not a truncated distance).
- SC001-st35: d² 1053 seen (the shrink-the-range-first rule A3 says unseen),
  1058 unseen.
- SC001-two-*: two Rhinos reach d² 3481 but not 3482; cloaked targets at
  d² 1906 (26%), 1657 (31%) and 1053 (45%) are unseen, where a single
  rounding (A2) would show them.
- SC001-stacks/ships: 55 ly unseen for both multi-Rhino fleets.
- SC003-orbit-past and planet-past: nothing at d² = P²+1; a Stealth
  freighter orbiting at d = P is unseen while one in deep space at the same
  distance is seen.
- SC009: starbase bit present at d² 4225 / 2025, absent (planet still
  reported) at 4226 / 2026.
- SC010: one detector extends the 75% bound from 25 to 29 ly (841 seen,
  842 unseen); two detectors to 31 (961 seen, 962 unseen).

## Round 2: race traits (predictions committed before the runs)

New CombatLab keys `prt P N` and `hab P C,C,C,L,L,L,H,H,H`. Player 0 is the
viewer with the trait under test; the combat-lab race is otherwise
unchanged. A race edit that leaves the race over its advantage-point budget
shows up as message 0x117 and degraded race stats in the generated year
(`docs/ORACLE.md`); each run is checked for that.

| Run | Tests | Content |
|---|---|---|
| SC-015 | S-20 (WM) | Player 0 War Monger, Rhino viewer seeing a plain and a Stealth freighter at 30 ly, an Ultra-Stealth one unseen at 45 ly: the two seen designs arrive as full designs. |
| SC-016 | S-20 (CA) | Player 0 Claim Adjuster, same fleets; player 1's habitability narrowed to grav 25–55, temp 35–85, rad 20–70. Player 1's block in player 0's `.M` carries that habitability and zero tech levels; designs stay partial. |
| SC-016N | S-20 (CA) | As SC-016, but player 1's only fleet is out of range: no block for player 1 (unknown players are not written). |
| SC-017 | S-9 | Player 0 NAS: Rhino reaches 100 ly (d² 10000 seen, 10001 not); Stealth 35% bound d² 4225. |
| SC-018 | S-9 | NAS Ferret (370/50): the planet at d² 2500 is still reported and its orbiting freighter seen (ship penetration not zeroed by NAS). |
| SC-019 | S-9 | NAS player, homeworld scanner kept, electronics 10 / energy 3 / bio 3: the best non-penetrating planetary scanner (Scoper 280) doubled to 560, no penetration: every deep-space freighter seen, every orbiting one unseen, no planet reports. |
| SC-020 | S-10 | JOAT, electronics 10: a Scout with no scanner part scans 200/100 (planet at d² 10000 reported, 10001 not; deep space 200 seen, √40001 not). |
| SC-021 | S-10, S-2 | JOAT, electronics 10: Scout + Elephant combines 200/100 with 300/200 to 313/203 (planet at d² 41209 reported, 41210 not; deep space 313 seen, where the larger part alone would give 300). |

## Round 3 (predictions committed before the runs)

SC-021 turned out to be a setup artifact, not a scanning result: its
player 0 had electronics 10, and the Elephant Scanner (electronics 16)
was gone from the design in the generated 2401 files (`Scout, 1 Quick
Jump 5, empty, empty`, mass 18 → 12). The viewer then behaved as a bare
Scout (planets within 100 ly reported, nothing beyond). Round 3 keeps
every part within the owner's tech.

| Run | Tests | Content |
|---|---|---|
| SC-015L | S-20 (WM) | SC-015 with player 0 also taking five cheap LRTs (No Ram Scoop, Cheap Engines, Only Basic Remote Mining, Low Starting Population, Bleeding Edge Tech) so the War Monger race stays within budget. Same predictions as SC-015. |
| SC-022 | S-10, S-2 | JOAT electronics 10, Scout + Possum (150): ⁴√(200⁴ + 150⁴) = 214. Deep-space freighters at d² 40000 (200), 40001, 42025 (205), 45796 (214) seen, 45797 unseen. Taking the larger scanner alone would stop at 200. |
| SC-023 | S-10, S-2, S-5 | JOAT electronics 16, Scout + Elephant: 369/217. Planet at d² 47089 (217) reported, next one past it not; freighter orbiting the edge planet seen (the larger part alone gives pen 200). |

## Round 4: rules SCANNING.md marked BINARY-ONLY (predictions committed before the runs)

`round2.py` (second SC lane round) writes SC-024..SC-031 and checks them:
`python3 round2.py specs OUTDIR`, `python3 round2.py list` (full case table
with the competing reading per case), `python3 round2.py check scNNN
AFTER.DUMP`. Both players are JOAT at tech 26, both homeworld scanners are
removed and both homeworld starbases are an empty Space Station, so fleets
in orbit start no battle. `combatlab dump` now also prints, for another
player's fleet, `dx dy warp wbits mass`, and for a planet report `env
popest defest surface`.

| Run | Tests (SCANNING.md) | Content and predictions |
|---|---|---|
| SC-024 | Fleets at your planets; starbases in every report | Player 0 has no fleets and no planetary scanners. Player 1 freighters orbit player 0's homeworld (a 98% Ghost) and a player 0 colony without a starbase: both seen. The same designs 1 ly away in deep space: unseen. Player 1's blind orbiters get position-only reports (level 1, no environment); the homeworld's report has the starbase bit and the (partial) starbase design, and player 0 becomes known to player 1. A player 1 freighter at the homeworld's position without the orbit flag is recorded only. |
| SC-025 | Starbases in every report; owner known | Player 0's only fleet is a blind freighter orbiting player 1's homeworld: position-only report with the starbase bit and the partial starbase design, player 1's block (partial). Player 1 sees the orbiter with no planetary scanner. |
| SC-026 | control for SC-025 | The same freighter 1 ly away in deep space: no report, no block either way. |
| SC-027 | Heading; mass; population and defense estimates | Player 0 Scout (built-in 520/260) sees moving player 1 freighters. Heading = waypoint − start, halved toward zero while a component is ≥ 128: (300,100) → (75,25); (50,−120) as is; (−127,0) as is; (−128,3) → (−64,1); (300,−7) → (75,−1) (floor halving would give −2); (−1,−395) → (0,−98) (floor: (−1,−99)). Warp is the waypoint's warp; a stationary fleet shows 0/0/0. A fleet that reaches its waypoint this year is recorded only. Mass: empty 29; 10/20/30 kT + 40 kT colonists → 129 (fuel not counted); two ships + 50 kT colonists → 108. Cargo shows 0. Planet estimates for player 1 colonies with 100,000 colonists and 1, 3, 5, 10, 40, 100 defenses (Neutron Shield, 3.8%): defense estimate `max(1, min(15, trunc((104 − k)/6)))` with `k = round(100·0.962ⁿ)`, i.e. 1, 2, 3, 6, 13, 15; 0 defenses → 0. Population estimate (in 400s) in `trunc((u + r − trunc(u/8))/4)`, `r < trunc(u/4)`, `u` = after-state population in 100s; u = 3 → 1. |
| SC-028 | More than two Tachyon Detectors | JOAT Frigate, built-in 520, three detectors (factor 91): a 75% target is 68% (seen at d² 27688, not at 27689; three-as-two-detectors would stop at 25985, four at 29446); an 85% target is 77% (seen at 14297, not at 14305). |
| SC-029 | Detectors over several designs or ships | Mole (100) viewers against 75%. A fleet of Mole + 1 detector with a second design carrying 1 detector, and a fleet of two Mole + 1 detector ships: factor 95 (71%, d² 841 seen, 842 not; adding up would see 842). Mole + 2 detectors with a 1-detector design: factor 93 (961 seen, 962 not). |
| SC-030 | Super Stealth +300; SS cargo; SS starbase | Player 1 SS (`lrt 1 0x1b80`). Elephant (300) viewer: a plain freighter is 75% (d² 5625 seen, 5626 not); with 50 kT cargo still 75% (dilution would give 51%). The bare station on player 1's homeworld, 60 ly from the viewer (P 200), is 75% and hidden beyond d² 2500: the planet is reported without its starbase. |
| SC-031 | Planet report after battle; design disclosure after battle | A player 0 Laser Cruiser (no scanner) and a player 1 Laser Destroyer orbit player 1's colony 5 and fight: player 0 gets a normal report (level 3) of planet 5, and each side gets the other's fighting design in full. Control: a blind player 0 freighter orbiting player 1 colony 12 with an unarmed player 1 freighter: position only, and both freighter designs partial. |

## Results

Every run was generated once with `pinned-turn` (cycles 20000) and
checked with `check.py`; raw files, dumps and check outputs are in the
private apparatus repository under `evidence/sc/`.

| Run | Cases | Result |
|---|---|---|
| SC-001, SC-001F | 28 + 28 | all as predicted; views identical with friends |
| SC-002 | 12 | all as predicted |
| SC-003..SC-007 | 5 × 26 | all as predicted |
| SC-008 | 26 | all as predicted |
| SC-009 | 4 | all as predicted |
| SC-010 | 21 | all as predicted |
| SC-011..SC-013 | 8 + 8 + 43 | all as predicted |
| SC-014 | 4 | all as predicted |
| SC-015 | 3 | as predicted (full designs), but the race was over budget (0x117) |
| SC-015L | 3 | all as predicted, legal race |
| SC-016, SC-016N | 3 + 0 | as predicted, including the player blocks |
| SC-017..SC-020 | 4 + 26 + 43 + 28 | all as predicted |
| SC-021 | 28 | invalid: Elephant Scanner removed from the design (tech 10 < 16); 11 cases and 15 view items differ, all explained by a bare Scout |
| SC-022, SC-023 | 5 + 26 | all as predicted |

Beyond the case tables, the whole view of both players (every fleet,
planet report, foreign design count and player block) matched the model in
every valid run. SC-001 regenerated with cycles 30000 gave the same views.
Behavior-level write-up: `docs/PARITY.md`, "Scanning".
