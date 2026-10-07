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
design 0 1 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Laser DD
design 1 4 Frigate, 1 Long Hump 6, empty, 2 Laser, 2 Mole-skin Shield = RS Gunboat
plan 0 1 5 1 0 1 = Max Any
plan 1 1 5 1 0 1 = Max Any
# Q1: armed RS shielded frigates close in, so they take fire for several rounds
fleet 0 0 at 1020 1230 ships 1:4 plan 1 fuel 100
fleet 1 0 at 1020 1230 ships 4:5 plan 1 fuel 100
# Q2: same with heavier fire, shields should reach 0 and stay there
fleet 0 1 at 1060 1230 ships 0:10 plan 1 fuel 100
fleet 1 1 at 1060 1230 ships 4:5 plan 1 fuel 100
