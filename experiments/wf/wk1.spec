# WK-1: a waypoint aimed at a fleet that is destroyed in battle this year.
# Combat Lab base2400. Player 0's HB Battleships (as E-8) kill player 1's
# Laser Destroyers (plan Hold, never fires) at three places. Player 0's
# Medium Freighters (followers) each aim waypoint 1 at one victim fleet from
# 100 ly away at warp 4, so no follower arrives.
#   A: victims 1/4 orbit unowned planet 7 (1166,1382) all year.
#   D: victims 1/1 sit in deep space at (1227,1363), 5 ly from planet 10
#      (1224,1359).
#   M: victims 1/2 start in deep space at (1045,1311) and fly 20 ly at warp 5
#      onto unowned planet 0 (1045,1291), where they are killed.
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
design 0 15 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, empty, empty, empty = Laser DD
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
# A
fleet 1 4 planet 7 at 1166 1382 ships 0:2 plan 1 fuel 300
fleet 0 1 planet 7 at 1166 1382 ships 0:1 fuel 300
fleet 0 11 at 1166 1282 ships 15:1 fuel 300 to 1166 1382 fleet 1 4 warp 4
# D
fleet 1 1 at 1227 1363 ships 0:2 plan 1 fuel 300
fleet 0 2 at 1227 1363 ships 0:1 fuel 300
fleet 0 12 at 1227 1263 ships 15:1 fuel 300 to 1227 1363 fleet 1 1 warp 4
# M
fleet 1 2 at 1045 1311 ships 0:2 plan 1 fuel 300 to 1045 1291 planet 0 warp 5
fleet 0 3 planet 0 at 1045 1291 ships 0:1 fuel 300
fleet 0 13 at 1045 1211 ships 15:1 fuel 300 to 1045 1311 fleet 1 2 warp 4
