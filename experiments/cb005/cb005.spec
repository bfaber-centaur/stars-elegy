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
design 0 7 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 4 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
sbdesign 1 0 Space Station, empty, 2 Gatling Gun, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Gatling Station
plan 0 1 5 1 0 1 = Max Any
plan 0 2 5 1 0 0 = Nobody
plan 1 0 5 1 0 1 = Station
plan 1 1 5 1 0 1 = Max Any
plan 1 2 5 1 0 0 = Nobody
sbdesign 0 0 Space Station, empty, empty, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Unarmed Station
plan 0 0 5 1 0 1 = Station
# P1 homeworld (planet 8): gatling station vs two armed attacking player-0 fleets
fleet 0 0 planet 8 at 1169 1145 ships 0:5 plan 1 fuel 100
fleet 0 1 planet 8 at 1169 1145 ships 0:5 plan 1 fuel 100
# P0 homeworld (planet 17): unarmed station; player-0 frigates attack armed player-1 visitors (plan nobody)
fleet 0 2 planet 17 at 1306 1060 ships 0:5 plan 1 fuel 100
fleet 1 0 planet 17 at 1306 1060 ships 4:5 plan 2 fuel 100
