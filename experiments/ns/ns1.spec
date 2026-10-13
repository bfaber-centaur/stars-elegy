# NS-1: a transport task whose waypoint names a packet or salvage. Combat Lab
# base2400. Player 0 (human JOAT) runs every fleet; each fleet is one Medium
# Freighter (210 kT hold) with the task "load all ironium, load all boranium".
# Every named object holds 100 kT boranium and no ironium; every planet under
# test has 50 kT ironium and no boranium on its surface, so the cargo tells
# which source the fleet loaded from.
tech 0 prop 26
research 0 0
design 0 15 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
#
# (a) the named object sits over a planet
# A1: salvage (player 0's object 0) over player 0's planet 4; the fleet arrives
#     from 20 ly north at warp 5, waypoint 1 naming the salvage.
planet 4 owner 0 pop 500
planetset 4 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 4 none
thing packet 0 0 1143 1103 4 4 0 100 0
fleet 0 1 at 1143 1083 ships 15:1 fuel 300 to 1143 1103 thing 0x2000 warp 5 task transport 1:0,1:0,-,-,-
# A2: salvage (player 0's object 1) over player 1's planet 9; arrival as A1.
planet 9 owner 1 pop 500
planetset 9 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 9 none
thing packet 0 1 1208 1297 9 4 0 100 0
fleet 0 2 at 1208 1277 ships 15:1 fuel 300 to 1208 1297 thing 0x2001 warp 5 task transport 1:0,1:0,-,-,-
# A3: salvage (player 0's object 2) over player 0's planet 5; the fleet orbits
#     planet 5 and its waypoint 0 names the salvage.
planet 5 owner 0 pop 500
planetset 5 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 5 none
thing packet 0 2 1146 1180 5 4 0 100 0
fleet 0 3 planet 5 at 1146 1180 ships 15:1 fuel 300 target thing 0x2002 task transport 1:0,1:0,-,-,-
# A4: salvage (player 0's object 3) over player 1's planet 14; waypoint 0 as A3.
planet 14 owner 1 pop 500
planetset 14 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 14 none
thing packet 0 3 1268 1317 14 4 0 100 0
fleet 0 4 planet 14 at 1268 1317 ships 15:1 fuel 300 target thing 0x2003 task transport 1:0,1:0,-,-,-
# A5: player 0's packet (object 4) over player 0's planet 12 at the start of the
#     year, bound for planet 21 at packet warp 5; waypoint 0 names it.
planet 12 owner 0 pop 500
planetset 12 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 12 none
thing packet 0 4 1245 1158 21 5 0 100 0
fleet 0 5 planet 12 at 1245 1158 ships 15:1 fuel 300 target thing 0x2004 task transport 1:0,1:0,-,-,-
# A6: player 1's packet (object 0) over player 1's planet 19, bound for planet 6
#     at packet warp 5; waypoint 0 names it.
planet 19 owner 1 pop 500
planetset 19 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 19 none
thing packet 1 0 1342 1123 6 5 0 100 0
fleet 0 6 planet 19 at 1342 1123 ships 15:1 fuel 300 target thing 0x2200 task transport 1:0,1:0,-,-,-
#
# (b) the named packet has flown on from the fleet's position: a packet as it
#     stands after its launch year (moved and bit15 set, 40 ly out from the
#     planet toward its destination), named by waypoint 0 of a fleet orbiting
#     the planet it left.
# B1: player 0's packet (object 5) from player 0's planet 3, bound for planet 6.
planet 3 owner 0 pop 500
planetset 3 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 3 none
thing packet 0 5 1135 1225 6 5 0 100 0 moved bit15
fleet 0 7 planet 3 at 1129 1265 ships 15:1 fuel 300 target thing 0x2005 task transport 1:0,1:0,-,-,-
# B2: player 1's packet (object 1) from player 1's planet 20, bound for planet 21.
planet 20 owner 1 pop 500
planetset 20 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 20 none
thing packet 1 1 1351 1250 21 5 0 100 0 moved bit15
fleet 0 8 planet 20 at 1348 1290 ships 15:1 fuel 300 target thing 0x2201 task transport 1:0,1:0,-,-,-
