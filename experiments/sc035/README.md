# SC-035 and SC-036: scanning after bombing and in a three-player battle (round 7)

These are the SCANNING.md open experiments 12 and 13 (stars-elegy #57),
run with the combat round 7 batch. The specs are CombatLab specs.

## SC-035 (`sc035.spec`, game CB)

- Player 0 has no scanner anywhere: its homeworld scanner is removed
  and its fleets are scannerless Mini Bombers with 2 Cherry Bombs each.
- Two bombers, on a plan attacking enemies, orbit planet 23. Player 1
  (an enemy) owns planet 23 with 100 colonists, no starbase and no
  defenses.
- Control: two more bombers orbit planet 22, which is unowned from the
  start.

**Prediction:**
- planet 23 ends the year unowned;
- player 0's report of planet 23 is a normal report (environment and
  the unowned state), not the position-only orbit report;
- player 0's report of planet 22 is position only.

## SC-036 (`sc036.spec`, game CB3P)

- Players 0 and 1 are friends; player 2 is an enemy of both.
- One armed Destroyer fleet of each player meets in deep space, at
  (1060, 1080), and they fight.
- No homeworld has a planetary scanner, and the fleets carry none.

**Prediction:** each participant's file holds the designs of all the
other stacks in full, allies included, and each other player becomes a
known player. So player 0's file has player 1's Phaser DD and player
2's X-Ray DD in full, and player 1's file has player 0's Laser DD and
player 2's design in full.

## Results

(pending)
