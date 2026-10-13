# TZ2, CB-062 Z1b (lane D's target-zero-score spec). Combat Lab base2400; players 0 and 1
# at tech 26 in every field, mutual enemies. Each case is its own
# deep-space battle on y = 1230. Player 1's stacks hold (plan 1: primary
# fuel transports, never fires). Player 0's firers use plan 2, primary
# armed ships, secondary any.
#   Z1b (1020): Sapper+Laser BB vs Laser DD (armed, no shields) + Slow Shield BB
#               (unarmed, 4000 shields, speed code 0)
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
design 0 1 Battleship, 4 Trans-Galactic Drive, empty, empty, 2 Pulsed Sapper, 1 Laser, empty, empty, empty, 6 Neutronium = Sapper Laser BB
design 1 1 Battleship, 1 Quick Jump 5, empty, 8 Complete Phase Shield, empty, empty, empty, empty, empty, 6 Neutronium = Slow Shield BB
design 1 2 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Tritanium = Laser DD
plan 0 2 5 3 1 1 = Armed First
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
# Z1b
fleet 0 1 at 1020 1230 ships 1:1 plan 2 fuel 2000
fleet 1 1 at 1020 1230 ships 2:1 plan 1 fuel 300
fleet 1 2 at 1020 1230 ships 1:1 plan 1 fuel 2000
