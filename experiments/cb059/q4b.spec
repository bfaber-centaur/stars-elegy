# CB-058 Q4b (lane D): cb058b with the two points' y values swapped. Player 0's
# fleet 1 and player 1's fleet 4 are at X' = (1020,1400); player 0's fleet 3 and
# player 1's fleet 2 are at Y' = (1000,1230). By first fleet X' is examined first;
# by ascending y, Y' is. Prediction: elegy 5d2450e
# (TestPredictionCB058Q4bBattleOrderNotByY).
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
keepdesigns
research 0 0
research 1 0
relation 0 1 2
relation 1 0 2
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 6 Heavy Blaster, 6 Heavy Blaster, empty, empty, empty, empty, empty, empty = HB BB
design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, empty, empty, empty = Laser DD
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
fleet 0 1 at 1020 1400 ships 0:1 fuel 300
fleet 1 4 at 1020 1400 ships 0:2 plan 1 fuel 300
fleet 0 3 at 1000 1230 ships 0:1 fuel 300
fleet 1 2 at 1000 1230 ships 0:2 plan 1 fuel 300
