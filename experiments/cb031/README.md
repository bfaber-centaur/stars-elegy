# CB-031: tech attempts with three players

Round 4 (COMBAT.md "Tech from battle", BINARY-ONLY and LEGACY BUG). A new
three-player game (`cb3p.def`, tiny, seed 11; built with
`tools/fleetlab/new-game`; all players set to JOAT). Player 0 has weapons
3, every other field 26 and research 0%; players 1 and 2 have 26
everywhere. Battles in deep space at (1060,1080). Each spec is pinned at
the 12 cycle counts of CB-029.

- `cb031-obs`: players 1 and 2 are enemies and fight (4 Phaser Destroyers
  against 3 Phaser Frigates); player 0, neutral to both, has an unarmed
  Freighter at the same place, so it is an observer, not in the battle.
- `cb031-n3`: all three players are enemies; player 0 has two Laser
  Frigates, player 1 four Phaser Destroyers, player 2 three Phaser
  Frigates and two Phaser Destroyers.

## Predictions (committed before the run)

- `cb031-obs`: the battle record names players 1 and 2 only. Player 0
  ends at weapons **3** in every stream: the observer attempt tests player
  0's number (0) against the observer mask, which never matches (LEGACY
  BUG). The intended rule would give player 0 weapons 4 in about a third
  of the streams.
- `cb031-n3`: three players in the record. Player 0 attempts in every
  stream (with three players every participant attempts, wiped out or
  not), so it reaches weapons 4 in some streams, about a third, whenever
  a weapons ≥ 4 design was destroyed.
- Start squares for three players are recorded (not predicted here).
