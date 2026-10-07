# CS-003-C: torpedo and missile damage; range-0 beams against a starbase (experiments/cs003/gen.py)
relation 0 1 2
relation 1 0 2
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
research 0 0
research 1 0
plan 0 0 5 1 0 1 = Enemies
sbdesign 1 0 Orbital Fort = Bare Fort
design 1 0 Battleship, 4 Long Hump 6, empty, empty, empty, empty, empty, empty, empty, 6 Neutronium, empty, empty = Hulk
design 0 0 Cruiser, 2 Trans-Star 10, empty, empty, 2 Alpha Torpedo, 2 Alpha Torpedo, 2 Alpha Torpedo, empty = T-00
design 0 1 Cruiser, 2 Trans-Star 10, empty, empty, 2 Beta Torpedo, 2 Beta Torpedo, 2 Beta Torpedo, empty = T-01
design 0 2 Cruiser, 2 Trans-Star 10, empty, empty, 2 Delta Torpedo, 2 Delta Torpedo, 2 Delta Torpedo, empty = T-02
design 0 3 Cruiser, 2 Trans-Star 10, empty, empty, 2 Epsilon Torpedo, 2 Epsilon Torpedo, 2 Epsilon Torpedo, empty = T-03
design 0 4 Cruiser, 2 Trans-Star 10, empty, empty, 2 Rho Torpedo, 2 Rho Torpedo, 2 Rho Torpedo, empty = T-04
design 0 5 Cruiser, 2 Trans-Star 10, empty, empty, 2 Upsilon Torpedo, 2 Upsilon Torpedo, 2 Upsilon Torpedo, empty = T-05
design 0 6 Cruiser, 2 Trans-Star 10, empty, empty, 2 Omega Torpedo, 2 Omega Torpedo, 2 Omega Torpedo, empty = T-06
design 0 7 Cruiser, 2 Trans-Star 10, empty, empty, 2 Anti Matter Torpedo, 2 Anti Matter Torpedo, 2 Anti Matter Torpedo, empty = T-07
design 0 8 Cruiser, 2 Trans-Star 10, empty, empty, 2 Jihad Missile, 2 Jihad Missile, 2 Jihad Missile, empty = T-08
design 0 9 Cruiser, 2 Trans-Star 10, empty, empty, 2 Juggernaut Missile, 2 Juggernaut Missile, 2 Juggernaut Missile, empty = T-09
design 0 10 Cruiser, 2 Trans-Star 10, empty, empty, 2 Doomsday Missile, 2 Doomsday Missile, 2 Doomsday Missile, empty = T-10
design 0 11 Cruiser, 2 Trans-Star 10, empty, empty, 2 Armageddon Missile, 2 Armageddon Missile, 2 Armageddon Missile, empty = T-11
design 0 12 Destroyer, 1 Long Hump 6, 1 Blackjack, empty, empty, empty, empty, empty = R0-Blackj
design 0 13 Destroyer, 1 Long Hump 6, 1 Bludgeon, empty, empty, empty, empty, empty = R0-Bludge
design 0 14 Destroyer, 1 Long Hump 6, 1 Blunderbuss, empty, empty, empty, empty, empty = R0-Blunde
fleet 0 0 at 1020 1230 ships 0:1 plan 0 fuel 200
fleet 1 0 at 1020 1230 ships 0:3 plan 0 fuel 200
fleet 0 1 at 1060 1230 ships 1:1 plan 0 fuel 200
fleet 1 1 at 1060 1230 ships 0:3 plan 0 fuel 200
fleet 0 2 at 1100 1230 ships 2:1 plan 0 fuel 200
fleet 1 2 at 1100 1230 ships 0:3 plan 0 fuel 200
fleet 0 3 at 1140 1230 ships 3:1 plan 0 fuel 200
fleet 1 3 at 1140 1230 ships 0:3 plan 0 fuel 200
fleet 0 4 at 1180 1230 ships 4:1 plan 0 fuel 200
fleet 1 4 at 1180 1230 ships 0:3 plan 0 fuel 200
fleet 0 5 at 1220 1230 ships 5:1 plan 0 fuel 200
fleet 1 5 at 1220 1230 ships 0:3 plan 0 fuel 200
fleet 0 6 at 1260 1230 ships 6:1 plan 0 fuel 200
fleet 1 6 at 1260 1230 ships 0:3 plan 0 fuel 200
fleet 0 7 at 1300 1230 ships 7:1 plan 0 fuel 200
fleet 1 7 at 1300 1230 ships 0:3 plan 0 fuel 200
fleet 0 8 at 1020 1030 ships 8:1 plan 0 fuel 200
fleet 1 8 at 1020 1030 ships 0:3 plan 0 fuel 200
fleet 0 9 at 1060 1030 ships 9:1 plan 0 fuel 200
fleet 1 9 at 1060 1030 ships 0:3 plan 0 fuel 200
fleet 0 10 at 1100 1030 ships 10:1 plan 0 fuel 200
fleet 1 10 at 1100 1030 ships 0:3 plan 0 fuel 200
fleet 0 11 at 1140 1030 ships 11:1 plan 0 fuel 200
fleet 1 11 at 1140 1030 ships 0:3 plan 0 fuel 200
planet 5 owner 1 pop 100 starbase 0
planetset 5 env=50,50,50 scanner=31 defenses=0
fleet 0 12 planet 5 at 1146 1180 ships 12:1 plan 0 fuel 200
planet 4 owner 1 pop 100 starbase 0
planetset 4 env=50,50,50 scanner=31 defenses=0
fleet 0 13 planet 4 at 1143 1103 ships 13:1 plan 0 fuel 200
planet 12 owner 1 pop 100 starbase 0
planetset 12 env=50,50,50 scanner=31 defenses=0
fleet 0 14 planet 12 at 1245 1158 ships 14:1 plan 0 fuel 200
