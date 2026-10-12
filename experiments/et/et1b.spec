# ET-1b (ET-1 plus a bracket fleet): does a transport task whose every action is empty send 0x04e
# ("fleet has finished its orders") when the fleet reaches its last
# waypoint? Combat Lab base2400. Player 0 (human JOAT) only; its colonies 4,
# 5 and 12 are identical (population 500, no installations, no queue).
tech 0 prop 26
research 0 0
design 0 15 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
# E: arrives at its own colony 4 with an empty transport task, no further waypoint
planet 4 owner 0 pop 500
planetset 4 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50
queue 4 none
fleet 0 1 at 1143 1083 ships 15:1 fuel 300 to 1143 1103 planet 4 warp 5 task transport -,-,-,-,-
# C: control, arrives at its own colony 5 with "unload all colonists" (10 carried), no further waypoint
planet 5 owner 0 pop 500
planetset 5 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50
queue 5 none
fleet 0 2 at 1146 1160 ships 15:1 fuel 300 cargo 0 0 0 10 to 1146 1180 planet 5 warp 5 task unload
# S: stationary at its own colony 12, empty transport task on its only waypoint
planet 12 owner 0 pop 500
planetset 12 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50
queue 12 none
fleet 0 3 planet 12 at 1245 1158 ships 15:1 fuel 300 task transport -,-,-,-,-
# N: bracket, arrives at its own colony 12 with no task and no further waypoint
# (0x04e (b) at the end of movement)
fleet 0 4 at 1245 1138 ships 15:1 fuel 300 to 1245 1158 planet 12 warp 5
