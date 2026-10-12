# RM-4: does an Alternate Reality remote miner mine its own AR planet in
# the year it arrives? Combat Lab base2400. Player 1 is a human AR player
# (as CB-056 run A); player 0 is untouched and far away. Every AR colony
# has a starbase (an AR colony without one hits the KX-001 Z1 fault).
# The colonies are identical: population 500, concentrations 50/50/50,
# surface 0, environment 50/50/50, no installations.
prt 1 8
lrt 1 0x0400
tech 1 energy 26
tech 1 weapons 26
tech 1 prop 26
tech 1 con 26
tech 1 elec 26
tech 1 bio 26
research 1 0
design 1 0 Mini-Miner, 1 Long Hump 6, empty, 1 Robo-Miner, 1 Robo-Miner = Miner
# A: miner arrives at AR colony 4 with a remote-mining task, no further waypoint
planet 4 owner 1 pop 500 starbase 0
planetset 4 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 conc=50,50,50 env=50,50,50
queue 4 none
fleet 1 1 at 1143 1083 ships 0:1 fuel 300 to 1143 1103 planet 4 warp 5 task mine
# B: miner arrives at AR colony 5 with a remote-mining task and a further waypoint
planet 5 owner 1 pop 500 starbase 0
planetset 5 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 conc=50,50,50 env=50,50,50
queue 5 none
fleet 1 2 at 1146 1160 ships 0:1 fuel 300 to 1146 1180 planet 5 warp 5 task mine to 1146 1250 warp 5
# D: baseline AR colony 12, no fleet (the colony's own mining)
planet 12 owner 1 pop 500 starbase 0
planetset 12 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 conc=50,50,50 env=50,50,50
queue 12 none
# U: control, a miner arrives at unowned planet 11 with a remote-mining task
planetset 11 conc=50,50,50
fleet 1 3 at 1243 1103 ships 0:1 fuel 300 to 1243 1123 planet 11 warp 5 task mine
