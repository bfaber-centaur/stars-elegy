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
research 0 0
relation 0 1 2
relation 1 0 2
design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 1 0 Frigate, 1 Long Hump 6, empty, 2 Colloidal Phaser, empty = Phaser Frigate
plan 0 1 5 1 0 1 = Max Any
plan 1 1 5 1 0 1 = Max Any
# player 0 (weapons 3) destroys player-1 frigates whose Colloidal Phasers need more weapons tech
fleet 0 0 at 1020 1230 ships 0:20 plan 1 fuel 100
fleet 1 0 at 1020 1230 ships 0:3 plan 1 fuel 100
