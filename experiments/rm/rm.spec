# RM-1..RM-3: remote-mining refusal order (stars-elegy #155, KERNEL.md
# "Remote mining"). Base: RG-002's settled 2462 files (apparatus
# evidence/rg002/s0/settle/raw/after). Every base fleet is kept; the
# fleets below are added, each stationary with one waypoint.
keepfleets-ordered
# RM-1a: player 0 scout (no mining robots) at its own colony 100 (JOAT).
fleet 0 8 planet 100 at 1633 1380 ships 0:1 fuel 100 task mine
# RM-1b: player 0 scout (no mining robots) at Robotoid (HE) planet 52.
fleet 0 9 planet 52 at 1298 1631 ships 0:1 fuel 100 task mine
# RM-2: a Macinti (AR) one-ship remote miner (its design slot 14) at player
# 0's colony 92.
fleet 6 12 planet 92 at 1559 1335 ships 14:1 fuel 500 task mine
# RM-3: player 0 remote miner (design slot 3) in deep space.
fleet 0 10 at 1450 1450 ships 3:1 fuel 200 task mine
