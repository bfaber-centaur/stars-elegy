# KB-4A: movement and fuel leftovers. Random events off (CB base), one year.
# Player 0: Interstellar Traveler with Improved Fuel Efficiency, No Advanced
# Scanners, Low Starting Population and Bleeding Edge Technology (legal),
# tech 26. Player 1 treats player 0 as a friend; player 0 is neutral to
# player 1. Both players' Space Stations are unarmed. Deep-space fleets
# start at x = 1020-1060 (no planet within 40 ly).
#   G1, G2: Anti-matter Generator scout (tank 250), stationary, fuel 100 / 230
#   X1, X2: one Super-Fuel Xport (tank 2250), stationary, fuel 1000 / 2150
#   E:      QJ5 tank scout, 100 ly east at warp 6, fuel 300 (IFE factor)
#   K:      the same with fuel 20 and a 300 ly leg (cannot afford the leg,
#           keeps fuel after this year's move)
#   H, H0:  Small Freighter with a Radiating Hydro-Ram Scoop carrying 70 kT
#           of colonists: moving 100 ly at warp 6 / stationary
#   Q:      Small Freighter + Medium Freighter (both QJ5) carrying 111 kT
#           of ironium, 100 ly at warp 6 (equal engine factors)
#   C:      QJ5 tank scout chasing fleet E at warp 9 with fuel 5
#   T1:     Small Freighter at planet 9 (no ironium), waypoint 0 transport
#           "wait for 50% ironium", then a waypoint 25 ly east at warp 5
#   T2:     Small Freighter at planet 12 with 10 kT of ironium, waypoint 0
#           transport "unload all ironium", then 25 ly south at warp 5
#   F1, F2: tank scouts at player 1's homeworld 8 (friend, Space Station),
#           fuel 10 / 400
#   F3:     player 1's tank scout at player 0's homeworld 17 (player 0 is
#           neutral to player 1), fuel 10
#   F4:     tank scout at player 0's planet 13 (Orbital Fort, no dock), fuel 10
#   F5:     tank scout at player 0's homeworld 17 (Space Station), fuel 10
research 0 0
research 1 0
prt 0 7
lrt 0 0x1c01
relation 1 0 1
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
design 0 0 Scout, 1 Quick Jump 5, 1 Bat Scanner, 1 Fuel Tank = Tank
design 0 1 Scout, 1 Quick Jump 5, 1 Bat Scanner, 1 Anti-matter Generator = Gen
design 0 2 Super-Fuel Xport, 2 Quick Jump 5, empty, empty = Xport
design 0 3 Small Freighter, 1 Radiating Hydro-Ram Scoop, empty, empty = Ram
design 0 4 Small Freighter, 1 Quick Jump 5, empty, empty = SF
design 0 5 Medium Freighter, 1 Quick Jump 5, empty, empty = MF
design 1 0 Scout, 1 Quick Jump 5, 1 Bat Scanner, 1 Fuel Tank = Tank
sbdesign 0 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Station
sbdesign 0 1 Orbital Fort, empty, empty, empty, empty, empty = Fort
sbdesign 1 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Station
planet 9 owner 0 pop 1000 starbase none
planetset 9 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50 orig=50,50,50
planet 12 owner 0 pop 1000 starbase none
planetset 12 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50 orig=50,50,50
planet 13 owner 0 pop 1000 starbase 1
planetset 13 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 9 none
queue 12 none
queue 13 none
queue 8 none
queue 17 none
fleet 0 0 planet 17 at 1306 1060 ships 0:1 fuel 10
fleet 0 1 at 1030 1200 ships 1:1 fuel 100
fleet 0 2 at 1040 1200 ships 1:1 fuel 230
fleet 0 3 at 1050 1200 ships 2:1 fuel 1000
fleet 0 4 at 1060 1200 ships 2:1 fuel 2150
fleet 0 5 at 1020 1030 ships 0:1 fuel 300 to 1120 1030 warp 6
fleet 0 6 at 1020 1050 ships 0:1 fuel 20 to 1320 1050 warp 6
fleet 0 7 at 1020 1070 ships 3:1 fuel 130 cargo 0 0 0 70 to 1120 1070 warp 6
fleet 0 8 at 1030 1220 ships 3:1 fuel 130 cargo 0 0 0 70
fleet 0 9 at 1020 1240 ships 4:1,5:1 fuel 300 cargo 111 0 0 0 to 1120 1240 warp 6
fleet 0 10 at 1020 1010 ships 0:1 fuel 5 to 1020 1030 fleet 0 5 warp 9
fleet 0 11 planet 9 at 1208 1297 ships 4:1 fuel 100 task transport 6:50,-,-,-,- to 1233 1297 warp 5
fleet 0 12 planet 12 at 1245 1158 ships 4:1 fuel 100 cargo 10 0 0 0 task transport 2:0,-,-,-,- to 1245 1183 warp 5
fleet 0 13 planet 8 at 1169 1145 ships 0:1 fuel 10
fleet 0 14 planet 8 at 1169 1145 ships 0:1 fuel 400
fleet 0 15 planet 13 at 1249 1354 ships 0:1 fuel 10
fleet 1 0 planet 8 at 1169 1145 ships 0:1
fleet 1 1 planet 17 at 1306 1060 ships 0:1 fuel 10
