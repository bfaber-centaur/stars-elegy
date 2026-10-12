# GAP-001 run 2 (gap001b): populations in the file unit (100 colonists), so the
# probe planets have the intended 20, 37 and 60 resources; G3/G4 added.
# GAP-001: Worsen, scrap at a starbase, IT packet costs, auto/mixed/driverless
# packets, Genesis Device, fleet gifts. Player 0 IT (tech 26), player 1 CA.
prt 0 7
lrt 0 0x1b80
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
mt 0 0x0400
research 0 0
prt 1 3
tech 1 prop 10
tech 1 bio 6
research 1 0
relation 1 0 0
relation 0 1 1

design 0 0 Small Freighter, 1 Long Hump 6, 1 Rhino Scanner, empty = Hauler
sbdesign 0 0 Orbital Fort, empty, empty, empty, empty, empty = Fort
sbdesign 0 1 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Catcher 7
design 1 0 Mini-Miner, 1 Long Hump 6, empty, 1 Orbital Adjuster, 1 Orbital Adjuster = OA2
design 1 1 Mini-Miner, 1 Long Hump 6, empty, 1 Orbital Adjuster, empty = OA1

# --- W: hostile Orbital Adjusters
planet 15 owner 0 pop 1000 starbase none
planetset 15 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
queue 15 none
planet 19 owner 0 pop 1000 starbase 0
planetset 19 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
queue 19 none
fleet 1 1 planet 15 at 1281 1064 ships 0:1
fleet 1 4 planet 15 at 1281 1064 ships 1:1
fleet 1 2 planet 19 at 1342 1123 ships 0:1
fleet 1 0 planet 8 at 1169 1145 ships 1:1

# --- S: scrap at a planet with a starbase, and without one
planet 21 owner 0 pop 1000 starbase 0
planetset 21 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0
queue 21 none
planet 18 owner 0 pop 1000 starbase none
planetset 18 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0
queue 18 none
fleet 0 10 planet 21 at 1359 1121 ships 0:2 cargo 50 20 10 0 task scrap
fleet 0 11 planet 18 at 1324 1192 ships 0:2 cargo 50 20 10 0 task scrap

# --- P and A: packets (LAUNCH = mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31)
# P1: one mixed item, IT, plenty of resources
planet 2 owner 0 pop 200 starbase 1
planetset 2 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=22,7
queue 2 17:1:1
# P2: ironium x20 with 37 resources (resource-cost probe)
planet 4 owner 0 pop 370 starbase 1
planetset 4 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=23,7
queue 4 14:20:1
# P3: mixed x20 with 37 resources (resource-cost probe)
planet 6 owner 0 pop 370 starbase 1
planetset 6 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=23,7
queue 6 17:20:1
# A1: Auto Mineral Packets x3 with a driver and destination, plenty of resources
planet 3 owner 0 pop 200 starbase 1
planetset 3 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=22,7
queue 3 6:3:1
# A2: Auto Mineral Packets x20 with 37 resources (short on resources)
planet 5 owner 0 pop 370 starbase 1
planetset 5 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=23,7
queue 5 6:20:1
# A3: no mass driver (no starbase): ironium x2 then mixed x1
planet 9 owner 0 pop 200 starbase none
planetset 9 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 9 14:2:1,17:1:1
# A4: no mass driver (no starbase): Auto Mineral Packets x5 alone
planet 10 owner 0 pop 200 starbase none
planetset 10 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 10 6:5:1
# A5: driver, no destination: Auto Mineral Packets x5 alone
planet 11 owner 0 pop 200 starbase 1
planetset 11 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=none
queue 11 6:5:1

# --- G: Genesis Device (planetary item 13)
# G1: 99% done, completes this year
planet 7 owner 0 pop 600 starbase none
planetset 7 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 orig=50,50,50 conc=30,30,30 excess=0 scanner=31
queue 7 13:1:99:1
# G2: from 0% with 37 resources (cost probe)
planet 13 owner 0 pop 370 starbase none
planetset 13 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 13 13:1:1

# --- T: fleet gifts to player 1 (transfer-fleet task, waypoint 0, deep space)
fleet 0 20 at 1200 1000 ships 0:1 fuel 200 task transfer 0
fleet 0 21 at 1200 1010 ships 0:1 fuel 200 cargo 0 0 0 10 task transfer 0
fleet 0 22 at 1200 1020 ships 0:1 fuel 200 cargo 30 0 0 0 task transfer 0

# G3, G4: Genesis Device cost bracket, from 0% with 999 and 500 resources
planet 14 owner 0 pop 9990 starbase none
planetset 14 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 14 13:1:1
planet 16 owner 0 pop 5000 starbase none
planetset 16 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 16 13:1:1
