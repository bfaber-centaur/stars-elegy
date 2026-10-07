# CB-041: an Alternate Reality starbase destroyed

Round 5 (COMBAT.md: destroying an AR race's starbase leaves the planet
uninhabited; if a battle destroyed an AR starbase, no participant makes a
tech attempt; both BINARY-ONLY). Two-player Combat Lab base, at player 1's
homeworld (planet 8). Player 1 has an Orbital Fort with 12 Colloidal
Phasers and an unarmed Freighter there, propulsion 3 and 0% research.
Player 0 attacks with 8 Destroyers using the Trans-Galactic Drive
(propulsion 9). `cb041`: player 1 is AR (`prt 1 8`, `lrt 1 0x1b80`).
`cb041-joat`: the same with player 1 JOAT. Pinned at the twelve cycle
counts 5000 … 50000.

## Predictions (committed before the run)

- The Fort is destroyed in every stream; player 1's Freighter survives
  (it disengages).
- `cb041`: planet 8 is **uninhabited** after the turn (no owner, no
  population). Player 1 stays at propulsion 3 in every stream, including
  those where a player-0 Destroyer was destroyed (no attempt).
- `cb041-joat`: planet 8 stays player 1's. In streams where a player-0
  Destroyer was destroyed, player 1 (a participant at its own planet with
  something left) reaches propulsion 4 in some (about a third).
- Player 0 makes no attempt in either (another player's planet).

## Second setup (committed before its run)

Committed after the first twelve-stream runs of both starts (results
below) and before these ran. In those runs player 1's Freighter died in
every stream, so player 1 had nothing left and the `n` = 2 rule ruled out
its attempt in the JOAT control too: the first setup cannot tell the AR
rule apart. `cb041-sf` and `cb041-sf-joat` replace the Freighter with one
fleet of ten Super Freighters (Long Hump 6, armor 400 each).

- Player 1 keeps at least one Super Freighter in every stream.
- `cb041-sf`: the Fort is destroyed, planet 8 is uninhabited, and player 1
  stays at propulsion 3 in every stream (no attempt after a destroyed AR
  starbase).
- `cb041-sf-joat`: planet 8 stays player 1's. In streams where a
  player-0 Destroyer was destroyed, player 1 reaches propulsion 4 in some.
