# OT-6: KERNEL gaps K1 (Alternate Reality colonist loss: which fleets count
# as moving) and K3 (ship power speed code). Player 0 is AR, player 1 WM;
# both at tech 26. Deep-space AR freighters (design 1, hold 210 kT) near
# y = 1030..1090, x = 1200:
#   1: 22 kT, moves 20 ly east at warp 5      2: 23 kT, moves 20 ly
#   3: 100 kT, waypoint 1 on its own position, warp 5
#   4: 100 kT, fuel 0, waypoint 1 50 ly east at warp 5
#   5: 100 kT, chases fleet 6 at warp 5       6: scout, moves 25 ly east
#   7: 100 kT, waypoint 1 20 ly east at warp 0
# Power test ships: design "BMC" (Battle Cruiser, Trans-Star 10 ×2, 7 Big
# Mutha Cannons) and "DIS" (9 Disruptors) for each player, stationary.
research 0 0
research 1 0
prt 0 8
prt 1 2
relation 0 1 1
relation 1 0 1
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
design 0 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Scout
design 0 1 Medium Freighter, 1 Long Hump 6, 1 Rhino Scanner, 1 Crobmnium = Freighter
design 0 2 Battle Cruiser, 2 Trans-Star 10, empty, empty, 3 Big Mutha Cannon, 3 Big Mutha Cannon, 1 Big Mutha Cannon, empty = BMC
design 0 3 Battle Cruiser, 2 Trans-Star 10, empty, empty, 3 Disruptor, 3 Disruptor, 3 Disruptor, empty = DIS
design 1 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Scout
design 1 1 Battle Cruiser, 2 Trans-Star 10, empty, empty, 3 Big Mutha Cannon, 3 Big Mutha Cannon, 1 Big Mutha Cannon, empty = BMC
design 1 2 Battle Cruiser, 2 Trans-Star 10, empty, empty, 3 Disruptor, 3 Disruptor, 3 Disruptor, empty = DIS
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 0 1 at 1200 1030 ships 1:1 fuel 400 cargo 0 0 0 22 to 1220 1030 warp 5
fleet 0 2 at 1200 1040 ships 1:1 fuel 400 cargo 0 0 0 23 to 1220 1040 warp 5
fleet 0 3 at 1200 1050 ships 1:1 fuel 400 cargo 0 0 0 100 to 1200 1050 warp 5
fleet 0 4 at 1200 1060 ships 1:1 fuel 0 cargo 0 0 0 100 to 1250 1060 warp 5
fleet 0 5 at 1200 1070 ships 1:1 fuel 400 cargo 0 0 0 100 to 1200 1080 fleet 0 6 warp 5
fleet 0 6 at 1200 1080 ships 0:1 fuel 300 to 1225 1080 warp 5
fleet 0 7 at 1200 1090 ships 1:1 fuel 400 cargo 0 0 0 100 to 1220 1090 warp 0
fleet 0 8 planet 17 at 1306 1060 ships 2:1 fuel 500
fleet 0 9 planet 17 at 1306 1060 ships 3:1 fuel 500
fleet 1 0 planet 8 at 1169 1145 ships 0:1
fleet 1 1 planet 8 at 1169 1145 ships 1:1 fuel 500
fleet 1 2 planet 8 at 1169 1145 ships 2:1 fuel 500
