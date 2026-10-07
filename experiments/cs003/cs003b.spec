# CS-003-B: bombs with BINARY-ONLY zero values, MCM bomb, OCM colonize, Orbital Adjuster mining (experiments/cs003/gen.py)
relation 0 1 2
relation 1 0 2
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
research 0 0
research 1 0
plan 0 0 4 1 0 1 = Enemies
sbdesign 1 0 Orbital Fort = Bare Fort
design 0 0 Mini Bomber, 1 Long Hump 6, 1 LBU-17 Bomb = LBU-17 Bomb
design 0 1 Mini Bomber, 1 Long Hump 6, 1 LBU-32 Bomb = LBU-32 Bomb
design 0 2 Mini Bomber, 1 Long Hump 6, 1 LBU-74 Bomb = LBU-74 Bomb
design 0 3 Mini Bomber, 1 Long Hump 6, 1 Hush-a-Boom = Hush-a-Boom
design 0 4 Mini Bomber, 1 Long Hump 6, 1 Retro Bomb = Retro Bomb
design 0 5 Mini Bomber, 1 Long Hump 6, 1 Smart Bomb = Smart Bomb
design 0 6 Mini Bomber, 1 Long Hump 6, 1 Neutron Bomb = Neutron Bomb
design 0 7 Mini Bomber, 1 Long Hump 6, 1 Enriched Neutron Bomb = Enriched Neu
design 0 8 Mini Bomber, 1 Long Hump 6, 1 Peerless Bomb = Peerless Bom
design 0 9 Mini Bomber, 1 Long Hump 6, 1 Annihilator Bomb = Annihilator 
design 0 10 Cruiser, 2 Long Hump 6, empty, empty, 1 Multi Contained Munition, empty, empty, empty = MCM Cruiser
design 0 11 Colony Ship, 1 Long Hump 6, 1 Orbital Construction Module = Col-O1
design 0 12 Colony Ship, 1 Long Hump 6, 1 Colonization Module = Col-O2
design 0 13 Colony Ship, 1 Long Hump 6, empty = Col-O3
design 0 14 Midget Miner, 1 Long Hump 6, 2 Orbital Adjuster = Min-X1
design 0 15 Midget Miner, 1 Long Hump 6, 2 Robo-Midget Miner = Min-X2
planet 0 owner 1 pop 9 starbase none
planetset 0 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 0 planet 0 at 1045 1291 ships 0:1 plan 0 fuel 200
planet 1 owner 1 pop 9 starbase none
planetset 1 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 1 planet 1 at 1071 1087 ships 1:1 plan 0 fuel 200
planet 2 owner 1 pop 9 starbase none
planetset 2 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 2 planet 2 at 1090 1295 ships 2:1 plan 0 fuel 200
planet 3 owner 1 pop 9 starbase none
planetset 3 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 3 planet 3 at 1129 1265 ships 3:1 plan 0 fuel 200
planet 4 owner 1 pop 9 starbase none
planetset 4 mines=10 factories=10 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 4 planet 4 at 1143 1103 ships 4:1 plan 0 fuel 200
planet 5 owner 1 pop 1 starbase none
planetset 5 mines=20 factories=20 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 5 planet 5 at 1146 1180 ships 5:1 plan 0 fuel 200
planet 6 owner 1 pop 1 starbase none
planetset 6 mines=20 factories=20 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 6 planet 6 at 1166 1017 ships 6:1 plan 0 fuel 200
planet 7 owner 1 pop 1 starbase none
planetset 7 mines=20 factories=20 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 7 planet 7 at 1166 1382 ships 7:1 plan 0 fuel 200
planet 9 owner 1 pop 1 starbase none
planetset 9 mines=20 factories=20 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 8 planet 9 at 1208 1297 ships 8:1 plan 0 fuel 200
planet 10 owner 1 pop 1 starbase none
planetset 10 mines=20 factories=20 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 9 planet 10 at 1224 1359 ships 9:1 plan 0 fuel 200
planet 11 owner 1 pop 870 starbase none
planetset 11 mines=10 excess=0 defenses=0 env=50,50,50 scanner=31
fleet 0 10 planet 11 at 1243 1123 ships 10:1 plan 0 fuel 200
fleet 0 11 planet 12 at 1245 1158 ships 11:1 plan 0 fuel 200 cargo 0 0 0 25 task colonize
fleet 0 12 planet 13 at 1249 1354 ships 12:1 plan 0 fuel 200 cargo 0 0 0 25 task colonize
fleet 0 13 planet 14 at 1268 1317 ships 13:1 plan 0 fuel 200 cargo 0 0 0 25 task colonize
planetset 15 conc=100,100,100
fleet 0 14 planet 15 at 1281 1064 ships 14:1 plan 0 fuel 200 task mine
planetset 16 conc=100,100,100
fleet 0 15 planet 16 at 1284 1383 ships 15:1 plan 0 fuel 200 task mine
