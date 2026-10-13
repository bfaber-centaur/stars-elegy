# WK-2: several followers of one fleet destroyed in battle (case A), and one
# follower with gone-fleet targets at waypoint 2 or later (cases B1-B3).
# Combat Lab base2400, as WK-1: player 0's HB Battleships kill player 1's Laser
# Destroyers (plan Hold, never fires). Every victim pair starts in deep space
# and flies 20 ly due south at warp 5 to a deep-space point where a battleship
# waits, so where it dies differs from where it started. Followers are player 0
# Medium Freighters at warp 4, 100 ly or more from their targets: none arrives.
#   A:  victims 1/1, (1100,1320) -> (1100,1340). Followers 0/11 from the
#       north, 0/12 from the east, 0/13 from the south-west, each with
#       waypoint 1 aimed at 1/1.
#   B1: victims 1/2, (1300,1220) -> (1300,1240). Follower 0/14: waypoint 1
#       aimed at 1/2, waypoint 2 deep space (1220,1080), waypoint 3 aimed at 1/2.
#   B2: victims 1/3, (1200,1200) -> (1200,1220), and 1/4, (1380,1180) ->
#       (1380,1200). Follower 0/15: waypoint 1 aimed at 1/3, waypoint 2 at 1/4.
#   B3: victims 1/5, (1060,1160) -> (1060,1180). Follower 0/16: waypoint 1
#       deep space (1060,1380), waypoint 2 aimed at 1/5.
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
tech 1 energy 26
tech 1 weapons 26
tech 1 prop 26
tech 1 con 26
tech 1 elec 26
tech 1 bio 26
keepdesigns
research 0 0
research 1 0
relation 0 1 2
relation 1 0 2
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 6 Heavy Blaster, 6 Heavy Blaster, empty, empty, empty, empty, empty, empty = HB BB
design 0 15 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, empty, empty, empty = Laser DD
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
# A
fleet 1 1 at 1100 1320 ships 0:2 plan 1 fuel 300 to 1100 1340 warp 5
fleet 0 1 at 1100 1340 ships 0:1 fuel 300
fleet 0 11 at 1100 1220 ships 15:1 fuel 300 to 1100 1320 fleet 1 1 warp 4
fleet 0 12 at 1200 1320 ships 15:1 fuel 300 to 1100 1320 fleet 1 1 warp 4
fleet 0 13 at 1029 1249 ships 15:1 fuel 300 to 1100 1320 fleet 1 1 warp 4
# B1
fleet 1 2 at 1300 1220 ships 0:2 plan 1 fuel 300 to 1300 1240 warp 5
fleet 0 2 at 1300 1240 ships 0:1 fuel 300
fleet 0 14 at 1300 1120 ships 15:1 fuel 300 to 1300 1220 fleet 1 2 warp 4 to 1220 1080 warp 4 to 1300 1220 fleet 1 2 warp 4
# B2
fleet 1 3 at 1200 1200 ships 0:2 plan 1 fuel 300 to 1200 1220 warp 5
fleet 0 3 at 1200 1220 ships 0:1 fuel 300
fleet 1 4 at 1380 1180 ships 0:2 plan 1 fuel 300 to 1380 1200 warp 5
fleet 0 4 at 1380 1200 ships 0:1 fuel 300
fleet 0 15 at 1100 1200 ships 15:1 fuel 300 to 1200 1200 fleet 1 3 warp 4 to 1380 1180 fleet 1 4 warp 4
# B3
fleet 1 5 at 1060 1160 ships 0:2 plan 1 fuel 300 to 1060 1180 warp 5
fleet 0 5 at 1060 1180 ships 0:1 fuel 300
fleet 0 16 at 1060 1280 ships 15:1 fuel 300 to 1060 1380 warp 4 to 1060 1160 fleet 1 5 warp 4
