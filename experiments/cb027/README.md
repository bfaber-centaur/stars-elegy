# CB-027: a starbase's cost in target choice

Round 4 (COMBAT.md "Target choice", BINARY-ONLY). Player 0 has a bare
Space Station (no parts: armor 500, no shields) and one Fuel Transport with
a Mole-skin Shield (armor 5, shield 25) at planet 18. One player-1 Hunter
(one Colloidal Phaser, primary "any") attacks. Pinned at cycles 20000,
30000 and 8000.

Attractiveness for a beam, `cost·100/(A + S + 1)`, with JOAT costs at tech
26 (`COMPONENTS.md`):

- station, plain owner cost 340 (resources 300 + boranium 40): 67;
- station at the starbase build cost (halved, 170): 33;
- Fuel Transport, cost 14: 45.

## Predictions (committed before the run)

- Whenever the Hunter fires while both the station and the Fuel Transport
  are eligible and in reach, it fires at the **station** (67 > 45). With
  the halved cost it would fire at the Fuel Transport until the station
  had taken more than about 123/500 damage.

## Result

Three seeds (8000, 20000, 30000). The Hunter fired 5 times in each, always
at the station. In 8000 the Fuel Transport fled out of reach (distance ≥ 4)
before the first shot, so that seed does not discriminate. In 20000 and
30000 the Fuel Transport was within distance 3 for 4 of the 5 shots, while
the station's damage stayed at or below 97/500 before each of those shots
(122 after the last). All 8 of those shots went to the **station**.
CONFIRMED: the starbase's target score uses its plain cost. All hits
replayed with the checker.
