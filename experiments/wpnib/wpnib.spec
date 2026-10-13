# WP-NIB: does the high nibble (bits 4-7) of a waypoint's target-type byte
# change what the host does? Combat Lab base2400; player 0 (human JOAT)
# fleets only. Every fleet is one Freighter (Medium Freighter, Long Hump 6)
# at warp 5 (25 ly a year). "hi N" sets the nibble of the waypoint before it
# (waypoint 0 when first); the builder's default is 1 (0x11 planet, 0x12
# fleet, 0x14 deep space). Each group differs only in the nibble.
tech 0 prop 26
research 0 0
design 0 15 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
# M: from deep space to planet 9 (1208,1297), 47.7 ly: mid-route after the year
fleet 0 1 at 1200 1250 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5
fleet 0 2 at 1200 1250 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5 hi 3
fleet 0 3 at 1200 1250 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5 hi 5
fleet 0 4 at 1200 1250 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5 hi 9
# A: from deep space to planet 9, 10.6 ly: arrives
fleet 0 5 at 1200 1290 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5
fleet 0 6 at 1200 1290 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5 hi 3
fleet 0 7 at 1200 1290 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5 hi 5
fleet 0 8 at 1200 1290 ships 15:1 fuel 300 to 1208 1297 planet 9 warp 5 hi 9
# D: deep space to deep space (1300,1240); 9/10 mid-route (40 ly), 11/12 arrive (10 ly)
fleet 0 9 at 1300 1200 ships 15:1 fuel 300 to 1300 1240 warp 5
fleet 0 10 at 1300 1200 ships 15:1 fuel 300 to 1300 1240 warp 5 hi 5
fleet 0 11 at 1300 1230 ships 15:1 fuel 300 to 1300 1240 warp 5
fleet 0 12 at 1300 1230 ships 15:1 fuel 300 to 1300 1240 warp 5 hi 5
# W: stationary, nibble on waypoint 0 only
fleet 0 13 planet 12 at 1245 1158 ships 15:1 fuel 300 hi 5
fleet 0 14 at 1350 1200 ships 15:1 fuel 300 hi 5
fleet 0 15 at 1350 1180 ships 15:1 fuel 300 hi 0
# T: arrive at an own colony with "unload all colonists" (10 carried)
planet 4 owner 0 pop 500
planetset 4 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50
queue 4 none
planet 5 owner 0 pop 500
planetset 5 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50
queue 5 none
fleet 0 16 at 1143 1083 ships 15:1 fuel 300 cargo 0 0 0 10 to 1143 1103 planet 4 warp 5 task unload
fleet 0 17 at 1146 1160 ships 15:1 fuel 300 cargo 0 0 0 10 to 1146 1180 planet 5 warp 5 hi 5 task unload
# F: chase fleet 0/20 (stationary at 1100,1300), 50 ly: mid-route
fleet 0 18 at 1100 1250 ships 15:1 fuel 300 to 1100 1300 fleet 0 20 warp 5
fleet 0 19 at 1100 1250 ships 15:1 fuel 300 to 1100 1300 fleet 0 20 warp 5 hi 5
fleet 0 20 at 1100 1300 ships 15:1 fuel 300
# O: leave orbit of planet 13 (1249,1354) for planet 16 (1284,1383), 45.5 ly: mid-route
fleet 0 21 planet 13 at 1249 1354 ships 15:1 fuel 300 to 1284 1383 planet 16 warp 5
fleet 0 22 planet 13 at 1249 1354 ships 15:1 fuel 300 to 1284 1383 planet 16 warp 5 hi 5
