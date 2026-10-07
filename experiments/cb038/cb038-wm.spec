prt 1 2
lrt 1 0x1b80
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
design 0 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Laser DD
design 1 0 Medium Freighter, 1 Long Hump 6, empty, empty = Medium
design 1 1 Frigate, 1 Long Hump 6, empty, empty, empty = Bare Frigate
plan 0 1 5 1 0 1 = Enemies
fleet 0 0 at 1020 1230 ships 0:1 plan 1 fuel 100
# M0 empty, M1 1 kT, M71 71 kT, a 2-freighter stack with 1 kT, a freighter + frigate fleet with 1 kT
fleet 1 0 at 1020 1230 ships 0:1 fuel 100
fleet 1 1 at 1020 1230 ships 0:1 fuel 100 cargo 1 0 0 0
fleet 1 2 at 1020 1230 ships 0:1 fuel 100 cargo 71 0 0 0
fleet 1 3 at 1020 1230 ships 0:2 fuel 100 cargo 1 0 0 0
fleet 1 4 at 1020 1230 ships 0:1,1:1 fuel 100 cargo 1 0 0 0
