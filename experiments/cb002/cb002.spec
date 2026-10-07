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
relation 0 1 2
relation 1 0 2
design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 0 1 Destroyer, 1 Long Hump 6, 1 Gatling Gun, empty, empty, empty, empty, empty = Gatling DD
design 0 2 Destroyer, 1 Long Hump 6, 1 Phaser Bazooka, 1 Colloidal Phaser, empty, empty, empty, empty = Long DD
design 0 3 Destroyer, 1 Long Hump 6, 1 Pulsed Sapper, 1 Pulsed Sapper, empty, empty, empty, empty = Sapper DD
design 0 4 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, 1 Flux Capacitor, empty, empty, 1 Energy Capacitor = Cap DD
design 0 5 Cruiser, 2 Trans-Star 10, empty, empty, 2 Jihad Missile, empty, empty, empty = Jihad Cruiser
design 0 6 Frigate, 1 Long Hump 6, empty, 1 Energy Dampener, empty = Dampener
design 0 7 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 0 8 Frigate, 1 Long Hump 6, empty, empty, 2 Mole-skin Shield = Shield Frigate
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Frigate, 1 Long Hump 6, empty, empty, 2 Mole-skin Shield = Shield Frigate
design 1 2 Battleship, 4 Trans-Star 10, empty, empty, empty, empty, empty, empty, empty, 6 Neutronium, empty, empty = Hulk
design 1 3 Destroyer, 1 Long Hump 6, empty, empty, empty, 2 Tritanium, 1 Beam Deflector, empty = Deflector DD
design 1 4 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
sbdesign 1 0 Space Station, empty, 2 Gatling Gun, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Gatling Station
# plans: tactic primary secondary who
plan 0 0 5 1 0 3 = Everyone
plan 0 1 5 1 0 1 = Max Any
plan 0 2 5 1 0 0 = Nobody
plan 1 0 5 1 0 1 = Enemies
plan 1 1 5 1 0 1 = Max Any
plan 1 2 5 1 0 0 = Nobody
# C1 gatling vs two stacks
fleet 0 0 at 1020 1230 ships 1:1 plan 1 fuel 100
fleet 1 0 at 1020 1230 ships 0:3 plan 2 fuel 100
fleet 1 1 at 1020 1230 ships 1:3 plan 2 fuel 100
# C2 range 2 and range 3 beams vs slow deflector destroyers
fleet 0 1 at 1060 1230 ships 2:1 plan 1 fuel 100
fleet 1 2 at 1060 1230 ships 3:3 plan 2 fuel 100
# C3 sappers vs an unshielded and a shielded stack
fleet 0 2 at 1100 1230 ships 3:5 plan 1 fuel 100
fleet 1 3 at 1100 1230 ships 0:3 plan 2 fuel 100
fleet 1 4 at 1100 1230 ships 1:3 plan 2 fuel 100
# C4 capacitors vs a deflector
fleet 0 3 at 1140 1230 ships 4:3 plan 1 fuel 100
fleet 1 5 at 1140 1230 ships 3:3 plan 2 fuel 100
# C5 202 Jihad missiles vs two unshielded hulks
fleet 0 4 at 1180 1230 ships 5:101 plan 1 fuel 500
fleet 1 6 at 1180 1230 ships 2:2 plan 2 fuel 500
# C6 retaliation: player 1 attacks nobody but is attacked
fleet 0 5 at 1220 1230 ships 0:5 plan 1 fuel 100
fleet 1 7 at 1220 1230 ships 4:5 plan 2 fuel 100
# C7 both sides attack nobody: no battle expected
fleet 0 6 at 1260 1230 ships 0:5 plan 2 fuel 100
fleet 1 8 at 1260 1230 ships 4:5 plan 2 fuel 100
# C8 energy dampener in the battle
fleet 0 7 at 1300 1230 ships 0:5,6:1 plan 1 fuel 100
fleet 1 9 at 1300 1230 ships 1:3 plan 2 fuel 100
# C9 player 0 homeworld (planet 17): station plan 0 = attack everyone, lone unarmed visitor
fleet 1 10 planet 17 at 1306 1060 ships 0:3 plan 2 fuel 100
# C10 player 1 homeworld (planet 8): gatling station plan 0 = attack enemies, two unarmed stacks
fleet 0 8 planet 8 at 1169 1145 ships 7:3 plan 2 fuel 100
fleet 0 9 planet 8 at 1169 1145 ships 8:3 plan 2 fuel 100
