# E-8: salvage from three deep-space battles in one year, two of them at points
# where salvage already lies. Player 0's fleets 1, 2 and 3 (one HB Battleship
# each) are at X = (1020,1230), Z = (1010,1150) and Y = (1000,1400) with player
# 1's fleets 4, 1 and 2 (two Laser Destroyers each, on a plan that never fires).
# Battle order by first fleet: X, Z, Y. By ascending y: Z, X, Y. By the victims'
# lowest fleet: Z, Y, X.
# Salvage already lying (written unmarked, so it decays this year):
#   player 1's number 1 at X, 250/50/30; player 0's number 0 at Y, 60/0/0.
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
thing packet 0 0 1000 1400 1023 4 60 0 0 bit15
thing packet 1 1 1020 1230 1023 4 250 50 30 bit15
fleet 0 1 at 1020 1230 ships 0:1 fuel 300
fleet 1 4 at 1020 1230 ships 0:2 plan 1 fuel 300
fleet 0 2 at 1010 1150 ships 0:1 fuel 300
fleet 1 1 at 1010 1150 ships 0:2 plan 1 fuel 300
fleet 0 3 at 1000 1400 ships 0:1 fuel 300
fleet 1 2 at 1000 1400 ships 0:2 plan 1 fuel 300
