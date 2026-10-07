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

## Results

(after the runs)
