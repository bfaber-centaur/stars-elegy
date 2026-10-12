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

## Follow-ups (committed before their own runs)

Added after the coordinator's question on the RG-001 diff: what happens
when the target fleet is destroyed or out of sight. One year each, pinned
at cycles 20000.

- **WF-04 `wf-gone`.** Player 1's fleet 0 is scrapped in deep space at
  waypoint 0 (step 2, before movement), so player 0's fleet 0 aims at a
  fleet that is gone. Prediction (`ORDERS.md` "Target gone", CONFIRMED for
  a fleet id that did not exist): the waypoint becomes deep space at
  (1200,1230), fleet 0 flies 25 ly toward it, and nothing names player 1's
  fleet 0 after the year. The own-fleet control is unchanged from WF-01.
- **WF-05 `wf-unseen`.** Player 1's fleet 0 starts 150 ly from player 0's
  only fleet and flies away; no scanner of player 0's reaches it. Open,
  two candidates:
  - **track:** the host file keeps the fleet target and its end-of-year
    position (as in WF-01), and only the owner's file shows deep space;
  - **lose:** the target is turned into deep space at the last position
    player 0 saw (its start) in the host file too, with a lost-target
    message (0x28–0x2a) in player 0's `.M` file.
  Either way player 0's fleet 0 is recorded where it ends.
