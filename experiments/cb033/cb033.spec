prt 0 9
prt 1 9
prt 2 9
prt 3 9
prt 4 9
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
tech 2 energy 26
tech 2 weapons 26
tech 2 prop 26
tech 2 con 26
tech 2 elec 26
tech 2 bio 26
tech 3 energy 26
tech 3 weapons 26
tech 3 prop 26
tech 3 con 26
tech 3 elec 26
tech 3 bio 26
tech 4 energy 26
tech 4 weapons 26
tech 4 prop 26
tech 4 con 26
tech 4 elec 26
tech 4 bio 26
relation 0 1 0
relation 0 2 0
relation 0 3 0
relation 0 4 0
relation 1 0 0
relation 1 2 0
relation 1 3 0
relation 1 4 0
relation 2 0 1
relation 2 1 0
relation 2 3 0
relation 2 4 0
relation 3 0 0
relation 3 1 0
relation 3 2 0
relation 3 4 0
relation 4 0 0
relation 4 1 0
relation 4 2 0
relation 4 3 0
design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 1 0 Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Colloidal Phaser, empty, 2 Tritanium, empty, empty = Phaser DD
design 2 0 Frigate, 1 Long Hump 6, empty, 2 Colloidal Phaser, empty = Phaser Frigate
design 3 0 Destroyer, 1 Long Hump 6, 1 Laser, empty, empty, 2 Tritanium, empty, empty = Tough DD
design 4 0 Destroyer, 1 Long Hump 6, 1 Laser, empty, empty, 2 Tritanium, empty, empty = Tough DD
plan 0 1 5 1 0 5 = Hunt P1
plan 1 1 5 1 0 4 = Hunt P0
plan 2 1 5 1 0 0 = Nobody
plan 3 1 5 1 0 8 = Hunt P4
plan 4 1 5 1 0 7 = Hunt P3
# A (0) and E (1) name each other; F (2) names nobody and is player 0's friend;
# players 3 and 4 fight each other all battle
fleet 0 0 at 1060 1080 ships 0:1 plan 1 fuel 100
fleet 1 0 at 1060 1080 ships 0:4 plan 1 fuel 100
fleet 2 0 at 1060 1080 ships 0:1 plan 1 fuel 100
fleet 3 0 at 1060 1080 ships 0:3 plan 1 fuel 100
fleet 4 0 at 1060 1080 ships 0:3 plan 1 fuel 100
