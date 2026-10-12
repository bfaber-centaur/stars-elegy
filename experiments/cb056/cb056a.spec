# CB-056 run A (Q1, Q2, Q4, Q5): player 1 Alternate Reality, mutual enemies.
# Predictions: elegy 6bc9046 docs/COMBAT-STATUS.md "CB-056 predictions".
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
prt 1 8
lrt 1 0x0400
keepdesigns
research 0 0
research 1 0
relation 0 1 2
relation 1 0 2
design 0 0 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Superlatanium, empty, empty = Laser DD
design 0 1 Battleship, 4 Trans-Galactic Drive, empty, empty, empty, empty, 2 Gatling Neutrino Cannon, empty, empty, 6 Superlatanium, 1 Flux Capacitor, empty = GNC BB
design 0 2 Battleship, 4 Trans-Galactic Drive, empty, empty, empty, empty, empty, empty, empty, 6 Superlatanium, empty, empty = Hulk
design 1 0 Destroyer, 1 Trans-Galactic Drive, empty, empty, empty, 2 Superlatanium, empty, empty = Wall DD
design 1 1 Destroyer, 1 Trans-Galactic Drive, empty, empty, empty, 2 Superlatanium, 1 Beam Deflector, empty = Wall DD 1
design 1 2 Destroyer, 1 Trans-Galactic Drive, empty, empty, 1 Beam Deflector, 2 Superlatanium, 1 Beam Deflector, empty = Wall DD 2
sbdesign 1 1 Death Star, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, 20 Superlatanium, empty, 20 Superlatanium, empty, empty = Wall Star
sbdesign 1 2 Death Star, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, 4 Jammer 50, empty, 1 Jammer 50, empty = Jam Star
sbdesign 1 3 Death Star, empty, empty, 4 Flux Capacitor, 2 Flux Capacitor, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Flux Star
sbdesign 1 4 Death Star, empty, 32 Heavy Blaster, 4 Battle Nexus, 4 Battle Nexus, empty, empty, 4 Battle Nexus, empty, 4 Battle Nexus, empty, empty, empty, empty, empty, empty, empty = Nexus Star
sbdesign 1 5 Ultra Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Bare Ultra
plan 0 1 5 1 0 1 = Max Any
queue 17 none
queue 8 none
# Q1: Wall Star at 499/500 (armor 1500 + 40 Superlatanium = 61,500: a Laser hit is far below one unit)
planet 12 owner 1 pop 1000 starbase 1
planetset 12 sbdmg=499
fleet 0 0 planet 12 at 1245 1158 ships 0:1 plan 1 fuel 300
# Q2: gatling stack against Wall Star plus three Wall DDs (0, 1, 2 deflectors)
planet 5 owner 1 pop 1000 starbase 1
fleet 0 1 planet 5 at 1146 1180 ships 1:3 plan 1 fuel 2800
fleet 1 1 planet 5 at 1146 1180 ships 0:1 fuel 300
fleet 1 2 planet 5 at 1146 1180 ships 1:1 fuel 300
fleet 1 3 planet 5 at 1146 1180 ships 2:1 fuel 300
# Q4a, Q4b, Q4 initiative: token values of three Death Stars
planet 4 owner 1 pop 1000 starbase 2
fleet 0 2 planet 4 at 1143 1103 ships 0:1 plan 1 fuel 300
planet 1 owner 1 pop 1000 starbase 3
fleet 0 3 planet 1 at 1071 1087 ships 0:1 plan 1 fuel 300
planet 6 owner 1 pop 1000 starbase 4
fleet 0 4 planet 6 at 1166 1017 ships 2:1 plan 1 fuel 2800
# Q5: repair at the owner's Ultra Station and Death Star, no battle, no movement
planet 18 owner 1 pop 1000 starbase 5
planetset 18 sbdmg=300
fleet 1 4 planet 18 at 1324 1192 ships 0:2 fuel 300 dmg 0:400:50
planet 20 owner 1 pop 1000 starbase 1
planetset 20 sbdmg=300
fleet 1 5 planet 20 at 1348 1290 ships 0:2 fuel 300 dmg 0:400:50
