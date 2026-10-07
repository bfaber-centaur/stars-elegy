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
design 0 7 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 0 8 Frigate, 1 Long Hump 6, empty, empty, 2 Mole-skin Shield = Shield Frigate
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Frigate, 1 Long Hump 6, empty, empty, 2 Mole-skin Shield = Shield Frigate
design 1 3 Destroyer, 1 Long Hump 6, empty, empty, empty, 2 Tritanium, 1 Beam Deflector, empty = Deflector DD
design 1 4 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 1 5 Destroyer, 1 Long Hump 6, empty, empty, empty, 2 Tritanium, empty, empty = Armor DD
sbdesign 1 0 Space Station, empty, 2 Gatling Gun, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Gatling Station
plan 0 0 5 1 0 2 = Station
plan 0 1 5 1 0 1 = Max Any
plan 0 2 5 1 0 0 = Nobody
plan 0 3 4 1 0 1 = Tactic Test
plan 1 0 5 1 0 3 = Station
plan 1 1 5 1 0 1 = Max Any
plan 1 2 5 1 0 0 = Nobody
plan 1 3 1 1 0 1 = Challenged
# T tactic test (first battle in fleet order)
fleet 0 0 at 1020 1230 ships 2:1 plan 3 fuel 100
fleet 1 0 at 1020 1230 ships 4:5 plan 1 fuel 100
# G gatling vs two slow stacks
fleet 0 1 at 1060 1230 ships 1:1 plan 1 fuel 100
fleet 1 1 at 1060 1230 ships 3:3 plan 2 fuel 100
fleet 1 2 at 1060 1230 ships 5:3 plan 2 fuel 100
# D disengage if challenged
fleet 0 2 at 1100 1230 ships 0:5 plan 1 fuel 100
fleet 1 3 at 1100 1230 ships 4:3 plan 3 fuel 100
# S1 player 1 homeworld: station plan 0 plus an armed player-1 fleet attacking enemies
fleet 0 3 planet 8 at 1169 1145 ships 7:3 plan 2 fuel 100
fleet 0 4 planet 8 at 1169 1145 ships 8:3 plan 2 fuel 100
fleet 1 4 planet 8 at 1169 1145 ships 4:5 plan 1 fuel 100
# S2 player 0 homeworld: lone unarmed visitor, station plan 0
fleet 1 5 planet 17 at 1306 1060 ships 0:3 plan 2 fuel 100
