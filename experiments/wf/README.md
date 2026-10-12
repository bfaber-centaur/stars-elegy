# A waypoint aimed at another player's fleet (WF-01..WF-03)

Shrinks the RG-001 mismatch on waypoints aimed at another player's fleet
(`docs/PARITY.md`, "Representative game (RG-001)"). In RG-001 year 5,
player 2's fleet 14 and player 5's fleet 33 got waypoint 1 aimed at a fleet
of player 1. The host file after the year still named the fleet, with the
fleet's end-of-year position, and year 6 kept tracking it. `ORDERS.md`
says the **owner's file** saves such a waypoint as deep space
(BINARY-ONLY, WU-A); Elegy also rewrites its game state (its W5
assumption).

Combat Lab base (game CB), `gen.py OUTDIR`. Unarmed Scouts in deep space.
Player 0's fleet 0 has waypoint 1 aimed at player 1's fleet 0 (100 ly
east), which flies south at warp 5. Player 0's fleet 1 has waypoint 1
aimed at its own fleet 2 (control), which flies south-east at warp 5.
`wf-enemy` sets both relations to enemy, `wf-friend` to friend. Two years:
year 2 runs on year 1's host file. Pinned at cycles 20000. Raw evidence:
stars-oracle-apparatus `evidence/wf/`.

## Predictions (committed before the runs)

- **WF-01 (host file).** After each year, player 0's fleet 0 still has a
  waypoint aimed at player 1's fleet 0 (target type fleet), at that
  fleet's end-of-year position. The same for the own-fleet control. Both
  relations.
- **WF-02 (owner's file).** In player 0's `.M` file after each year, the
  waypoint aimed at player 1's fleet is a deep-space waypoint at the same
  position. The own-fleet waypoint is still a fleet target.
- **WF-03 (year 2).** In year 2 fleet 0 moves toward player 1's fleet 0's
  position at the start of year 2 and the waypoint again ends at its
  end-of-year position: the host file's fleet target is used again, not a
  plain position.
