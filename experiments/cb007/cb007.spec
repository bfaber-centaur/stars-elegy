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
lrt 1 0x2000
design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 1 1 Frigate, 1 Long Hump 6, empty, empty, 2 Mole-skin Shield = Shield Frigate
design 1 5 Destroyer, 1 Long Hump 6, empty, empty, empty, 2 Tritanium, empty, empty = Armor DD
plan 0 1 5 1 0 1 = Max Any
plan 1 2 5 1 0 0 = Nobody
# R1 RS shields: regeneration while shields > 0
fleet 0 0 at 1020 1230 ships 0:5 plan 1 fuel 100
fleet 1 0 at 1020 1230 ships 1:5 plan 2 fuel 100
# R2 RS armor: Tritanium halved
fleet 0 1 at 1060 1230 ships 0:5 plan 1 fuel 100
fleet 1 1 at 1060 1230 ships 5:3 plan 2 fuel 100
