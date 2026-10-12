# RM-1 to RM-3 predictions (pushed before the runs)

Source: stars-elegy #155, `docs/KERNEL.md` "Remote mining", "Order of the
checks" (BINARY-ONLY). Setup: `rm.spec` on RG-002's settled 2462 files;
two years generated (2462 to 2464), the computer players planning as
usual. Each added fleet is stationary with one waypoint, task remote
mining.

| Case | Fleet | Predicted, year 1 | Predicted, year 2 |
|---|---|---|---|
| RM-1a | player 0 (JOAT) scout, no robots, at its own colony 100 | 0x075 (no mining modules), then 0x04e; task cleared | no remote-mining message for it |
| RM-1b | player 0 scout, no robots, at Robotoid (HE) planet 52 | 0x075, not 0x076; then 0x04e; task cleared (if the scout survives any battle there) | no remote-mining message for it |
| RM-2 | Macinti (AR) miner at player 0's colony 92 | no message; task still remote mining after the year; nothing mined from 92 | same again, if Macinti's own orders leave the fleet's waypoint as it is |
| RM-3 | player 0 miner in deep space | 0x077 (deep space), then 0x04e; task cleared | no remote-mining message for it |

Interpretation rules fixed before the runs: a case counts only when its
fleet is still in place at the end of the year; a battle loss or a
computer player's move order is recorded as such, not as a miss.
