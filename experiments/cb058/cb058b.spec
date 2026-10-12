# CB-058 run B (Q4): salvage at two deep-space points in one turn. Player 0's fleet 1
# (the lower) is at X = (1020,1230) with player 1's fleet 4; player 0's fleet 3 is at
# Y = (1000,1400) with player 1's fleet 2. X has the larger y, player 1's lower fleet is at Y.
# Prediction: elegy #187 head eaa474e (TestPredictionCB058SalvageTwoPoints's rule).
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
fleet 0 1 at 1020 1230 ships 0:1 fuel 300
fleet 1 4 at 1020 1230 ships 0:2 plan 1 fuel 300
fleet 0 3 at 1000 1400 ships 0:1 fuel 300
fleet 1 2 at 1000 1400 ships 0:2 plan 1 fuel 300
