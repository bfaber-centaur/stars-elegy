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
design 0 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Laser DD
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Laser Station
sbdesign 0 1 Space Station, empty, empty, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Unarmed Station
sbdesign 0 2 Orbital Fort, empty, empty, empty, empty, empty = Bare Fort
sbdesign 1 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Laser Station
sbdesign 1 1 Space Station, empty, empty, 8 Mole-skin Shield, empty, empty, 8 Mole-skin Shield, empty, empty, empty, empty, empty, empty = Unarmed Station
planet 18 owner 0 pop 500 starbase 0
planet 19 owner 0 pop 500 starbase 1
planet 21 owner 0 pop 500 starbase 0
planet 15 owner 0 pop 500 starbase 0
planet 22 owner 0 pop 500 starbase none
planet 5 owner 1 pop 500 starbase 1
planet 12 owner 1 pop 500 starbase 1
plan 0 0 5 2 0 1 = Station Starbase Only
plan 0 2 5 2 0 1 = Starbase Only
plan 1 1 5 1 0 1 = Max Any
# U1 planet 18, Laser Station: 3 P0 Laser Destroyers (starbase only) start a battle with P1 frigates
fleet 0 0 planet 18 at 1324 1192 ships 0:3 plan 2 fuel 100
fleet 1 0 planet 18 at 1324 1192 ships 1:5 plan 1 fuel 100
