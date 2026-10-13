# LM-1: does the second word of a lay-mines task change what the host does?
# Computer players' orders store it equal to the years word (RG-002: 5, 5);
# the client and Combat Lab specs leave it 0. Combat Lab base2400; player 0
# fleets only, each one Layer (Mini Mine Layer, 2 Mine Dispenser 40),
# stationary in deep space at least 55 ly from any planet or other layer.
# "lay Y:W" writes the years word Y and the second word W.
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
research 0 0
research 1 0
design 0 0 Mini Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, empty, empty = Layer
plan 0 0 4 1 0 1 = Enemies
# indefinitely (years word 5)
fleet 0 0 at 1020 1020 ships 0:1 plan 0 fuel 400 task lay 5:0
fleet 0 1 at 1100 1020 ships 0:1 plan 0 fuel 400 task lay 5:5
fleet 0 2 at 1380 1020 ships 0:1 plan 0 fuel 400 task lay 5:9
# years word 1
fleet 0 3 at 1020 1200 ships 0:1 plan 0 fuel 400 task lay 1:0
fleet 0 4 at 1380 1200 ships 0:1 plan 0 fuel 400 task lay 1:5
# years word 0 (this year only)
fleet 0 5 at 1100 1380 ships 0:1 plan 0 fuel 400 task lay 0:0
fleet 0 6 at 1380 1380 ships 0:1 plan 0 fuel 400 task lay 0:5
