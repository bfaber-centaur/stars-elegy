# CB-056 run A2 (Q2, Q4b, Q4 initiative rerun): run A fixed. Wall DDs armed with a plan whose targets miss the attacker, so they stay; the Flux Star carries one Heavy Blaster; the Nexus Star faces an armed visitor.
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
design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Superlatanium, empty, empty = Wall DD
design 1 1 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Superlatanium, 1 Beam Deflector, empty = Wall DD 1
design 1 2 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, 1 Beam Deflector, 2 Superlatanium, 1 Beam Deflector, empty = Wall DD 2
sbdesign 1 1 Death Star, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, 20 Superlatanium, empty, 20 Superlatanium, empty, empty = Wall Star
sbdesign 1 3 Death Star, empty, 1 Heavy Blaster, 4 Flux Capacitor, 2 Flux Capacitor, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Flux Star
sbdesign 1 4 Death Star, empty, 32 Heavy Blaster, 4 Battle Nexus, 4 Battle Nexus, empty, empty, 4 Battle Nexus, empty, 4 Battle Nexus, empty, empty, empty, empty, empty, empty, empty = Nexus Star
plan 0 1 5 1 0 1 = Max Any
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
# Q2: gatling stack against Wall Star plus three armed Wall DDs (0, 1, 2 deflectors) that target only fuel transports
planet 5 owner 1 pop 1000 starbase 1
fleet 0 1 planet 5 at 1146 1180 ships 1:3 plan 1 fuel 2800
fleet 1 1 planet 5 at 1146 1180 ships 0:1 plan 1 fuel 300
fleet 1 2 planet 5 at 1146 1180 ships 1:1 plan 1 fuel 300
fleet 1 3 planet 5 at 1146 1180 ships 2:1 plan 1 fuel 300
# Q4b: Flux Star (6 Flux Capacitors) fires one Heavy Blaster at an armed visitor
planet 1 owner 1 pop 1000 starbase 3
fleet 0 3 planet 1 at 1071 1087 ships 0:1 plan 1 fuel 300
# Q4 initiative: Nexus Star token values, armed visitor
planet 6 owner 1 pop 1000 starbase 4
fleet 0 4 planet 6 at 1166 1017 ships 0:1 plan 1 fuel 300
