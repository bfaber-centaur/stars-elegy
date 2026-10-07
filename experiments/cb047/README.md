# CB-047: queued ships lost with a starbase

Round 6. COMBAT.md (#38): when a (non-AR) starbase is destroyed, the
planet no longer has one, and ships and packets queued for building there
are lost (BINARY-ONLY). Production runs before battles in a year
(KERNEL.md "Turn order").

Two-player Combat Lab base. Player 1's homeworld (planet 8, armed Space
Station) queues 50 Laser Destroyers, then 20 factories (planetary item 7):
`queue 8 0:50:2,7:20:1`. `cb047`: 40 of player 0's Phaser Destroyers in
orbit destroy the Station. `cb047-ctl`: no attackers. Pinned at cycles
20000 and 30000.

## Predictions (committed before the run)

- `cb047-ctl`: after the turn the queue still starts with the Destroyer
  item (fewer than 50 left if some were built this year), then the
  factories.
- `cb047`: the Station is destroyed; after the turn the queue holds only
  the factory item (20 or fewer). Destroyers built this year before the
  battle exist (or died in it); the remaining Destroyer item is gone.
