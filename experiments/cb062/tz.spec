# TZ (lane D's target-zero-score spec). Combat Lab base2400; players 0 and 1
# at tech 26 in every field, mutual enemies. Each case is its own
# deep-space battle on y = 1230. Player 1's stacks hold (plan 1: primary
# fuel transports, never fires). Player 0's firers use plan 2, primary
# armed ships, secondary any.
#   Z1  (1020): Pulsed Sapper BB vs Laser DD (armed, no shields) + Shield BB (unarmed, 4000)
#   Z1c (1060): Pulsed Sapper BB vs Armed Shield BB (armed, 4000) + Shield BB (unarmed, 4000)
#   Z2  (1100): Alpha Torpedo BB vs Shield Frigate (armed, armor 45, shields 1000) + Bare Frigate (unarmed, none)
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
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 2 Pulsed Sapper, empty, empty, empty, empty, 6 Neutronium = Pulsed BB
design 0 1 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Alpha Torpedo, empty, empty, empty, empty, 6 Neutronium = Alpha BB
design 1 0 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, empty, empty, empty, empty, empty, 6 Neutronium = Shield BB
design 1 1 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, 1 Laser, empty, empty, empty, empty, 6 Neutronium = Armed Shield BB
design 1 2 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Tritanium = Laser DD
design 1 3 Frigate, 1 Trans-Galactic Drive, empty, 1 Laser, 2 Complete Phase Shield = Shield FF
design 1 4 Frigate, 1 Trans-Galactic Drive, empty, empty, empty = Bare FF
plan 0 2 5 3 1 1 = Armed First
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
# Z1
fleet 0 1 at 1020 1230 ships 0:1 plan 2 fuel 2000
fleet 1 1 at 1020 1230 ships 2:1 plan 1 fuel 300
fleet 1 2 at 1020 1230 ships 0:1 plan 1 fuel 2000
# Z1c
fleet 0 2 at 1060 1230 ships 0:1 plan 2 fuel 2000
fleet 1 3 at 1060 1230 ships 1:1 plan 1 fuel 2000
fleet 1 4 at 1060 1230 ships 0:1 plan 1 fuel 2000
# Z2
fleet 0 3 at 1100 1230 ships 1:1 plan 2 fuel 2000
fleet 1 5 at 1100 1230 ships 3:1 plan 1 fuel 125
fleet 1 6 at 1100 1230 ships 4:1 plan 1 fuel 125
