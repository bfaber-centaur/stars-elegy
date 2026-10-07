prt 0 9
prt 1 9
prt 2 9
tech 0 energy 26
tech 0 weapons 3
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
research 0 0
relation 0 1 0
relation 0 2 0
relation 1 0 0
relation 1 2 2
relation 2 0 0
relation 2 1 2
design 0 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 0 Destroyer, 1 Long Hump 6, 1 Colloidal Phaser, 1 Colloidal Phaser, empty, 2 Tritanium, empty, empty = Phaser DD
design 2 0 Frigate, 1 Long Hump 6, empty, 2 Colloidal Phaser, empty = Phaser Frigate
plan 1 1 5 1 0 1 = Max Any
plan 2 1 5 1 0 1 = Max Any
# player 1 destroys player 2's frigates; player 0 (weapons 3) watches with a Hauler
fleet 0 0 at 1060 1080 ships 0:1 fuel 100
fleet 1 0 at 1060 1080 ships 0:4 plan 1 fuel 100
fleet 2 0 at 1060 1080 ships 0:3 plan 1 fuel 100
