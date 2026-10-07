# CombatLab tooling check: ship launch (route destinations, a nearly full fleet list)

One pinned turn on the two-player Combat Lab base (cycles 30000) checking
the CombatLab directives that the ship-launch oracle batch will use: the
`route` key of `planetset`, the `fleets OWNER FROM-TO` range form, and the
dump's new-fleet readback. Results in `docs/ORACLE.md`, "Route
destinations and fleet ranges". Raw run: stars-oracle-apparatus
`evidence/sl/sltool`.

Setup (`sltool.spec`):

- Player 0 (planet 17): one Scout; queue `1:2:2,17:1:2` (two of design 1, a
  bare Scout, then starbase design 1, an Orbital Fort, replacing the Space
  Station); `route=raw:0013` (planet 18, written as a raw word);
  factories 100.
- Player 1 (planet 8): fleets 0..509, one Scout each (510 fleets); queue
  `0:3:2` (three Scouts); `route=5`.

Observed (one run):

- The route words survived the turn as written (`route=0006`,
  `route=0013`), which fits the decomp's reading: planet number + 1.
- Player 0's two Scouts were built as one new fleet (id 1, `ships=1:2`,
  fuel 600 of 600). Its waypoint 1 was planet 18, task 8 (route), warp 6.
  The Orbital Fort replaced the Station (`design=1`) and the queue emptied.
- Player 1 built one Scout as fleet 510, with waypoint 1 at planet 5,
  task 8, warp 5. That made 511 fleets. The queue kept `0:2:28:2`, two
  Scouts with the next 28% done. This looks like a resource limit, not
  the fleet limit; the limit is untested here.
- No fleet-name blocks were written for the new fleets.
- Byte 5 of player 1's 510 pre-existing fleets changed from 0x09 to 0x29.
  The new fleet kept 0x09. Not interpreted.
