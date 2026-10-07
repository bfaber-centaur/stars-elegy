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

## Result

Twelve cycle counts (5000 … 50000) per setup. `cb031-obs` at 10000 failed
once (the run stopped before the turn) and passed on rerun.

- `cb031-obs`: twelve distinct records, each naming players 1 and 2 (mask
  0x6). The record is in player 1's and player 2's files only; player 0's
  file has none, although its Hauler was there and survived. Player 2's
  Phaser Frigates were all destroyed. Player 0 ended at weapons **3** in
  **12 of 12** streams. CONFIRMED (LEGACY BUG).
- `cb031-n3`: twelve distinct three-player records (mask 0x7). In every
  stream player 0's Laser Frigates and all of player 2's ships were
  destroyed, and player 1's four Phaser DDs survived. Player 0, although
  wiped out, ended at weapons **4** in **5 of 12** streams (5000, 7000,
  8000, 9000, 30000) and 3 in the other 7. CONFIRMED: with three players
  every participant attempts.
- Start squares with three players, all 12 streams: player 0 (4,1),
  player 1 (8,8), player 2 (1,8), with both of player 2's tokens on one
  square. This matches the COMBAT.md table row for three players.
  With two participants (players 1 and 2 in `cb031-obs`), player 1 started
  at (1,4) and player 2 at (8,5).
