# KX-005 T: terraforming. Player 0 JOAT (tech 3) builds terraform items;
# player 1 is Claim Adjuster (prop 10, bio 6: reach 11/3/3) with Orbital
# Adjuster fleets (2 per ship) at player 0 planets 15, 19 (starbase) and 21
# (arriving this year). Player 1's relation to player 0: 1 (0 neutral,
# 1 friend, 2 enemy). Player 0 treats player 1 as a friend (no battle).
research 0 0
research 1 0
prt 1 3
tech 1 prop 10
tech 1 bio 6
relation 1 0 1
relation 0 1 1
design 0 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Tank
fleet 0 0 planet 17 at 1306 1060 ships 0:1
design 1 0 Mini-Miner, 1 Long Hump 6, empty, 1 Orbital Adjuster, 1 Orbital Adjuster = OA2
fleet 1 0 planet 8 at 1169 1145 ships 0:1
fleet 1 1 planet 15 at 1281 1064 ships 0:1
fleet 1 2 planet 19 at 1342 1123 ships 0:1
fleet 1 3 at 1359 1091 ships 0:1 fuel 210 to 1359 1121 planet 21 warp 6
planet 0 owner 0 pop 1000 starbase none
planet 1 owner 0 pop 8000 starbase none
planet 2 owner 0 pop 3000 starbase none
planet 3 owner 0 pop 2000 starbase none
planet 9 owner 0 pop 16000 starbase none
planet 15 owner 0 pop 1000 starbase none
planet 19 owner 0 pop 1000 starbase 0
planet 21 owner 0 pop 1000 starbase none
planet 4 owner 1 pop 3000 starbase none
planet 5 owner 1 pop 1200 starbase none
planet 6 owner 1 pop 3000 starbase none
planet 7 owner 1 pop 500 starbase none
planet 13 owner 1 pop 3000 starbase none
planet 14 owner 1 pop 3000 starbase none
planet 16 owner 1 pop 3000 starbase none
planetset 0 mines=0 factories=0 defenses=0 excess=0 env=50,60,60 orig=50,60,60
planetset 1 mines=0 factories=0 defenses=0 excess=0 env=50,60,58 orig=50,60,58
planetset 2 mines=0 factories=0 defenses=0 excess=0 env=50,60,60 orig=50,60,60
planetset 3 mines=0 factories=0 defenses=0 excess=0 env=50,86,50 orig=50,86,50
planetset 9 mines=0 factories=0 defenses=0 excess=0 env=50,60,60 orig=50,60,60
queue 0 12:1:1
queue 1 5:9:1
queue 2 4:5:1
queue 3 4:1:1
queue 9 4:9:1
queue 5 12:3:1
planetset 15 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 19 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 21 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 4 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 5 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 6 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 7 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 13 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 14 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
planetset 16 mines=0 factories=0 defenses=0 excess=0 env=60,60,60 orig=60,60,60
