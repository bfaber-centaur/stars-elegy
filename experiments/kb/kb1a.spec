# KB-1A: economy and population rules still BINARY-ONLY in KERNEL.md.
# Random events off (CB base). Player 0 is JOAT with Only Basic Remote
# Mining; player 1 is JOAT with a narrow habitat (40..60 on every axis).
# Research tax 0 for both. Test planets have no mines (no mining draws)
# except planet 12, whose remainders are all 0.
#   13 (P0): 70/50/50 (hab 79), pop 10430: JOAT + OBRM maximum
#   9  (P0): 50/50/50, pop 45000: effective population limit 2·max
#   12 (P0): ironium concentration 4, 500 mines: depletion clamp below 5
#   16 (P0): 95 defenses, Auto Defenses ×100: maximum defenses cap 100
#   10 (P1): 90/50/50 (30 outside on one axis), pop 1000: hostile cap 15;
#            5 defenses, Auto Defenses ×100: maximum defenses floor 10
#   11 (P1): 90/90/50 (30 outside on two axes), pop 1000
#   14 (unowned, 68/78/76): player 1 (tech 26) remote-mines it with 80
#            Mini-Miners of 2 Robo-Super-Miners each (80·2·27 = 4320 robot
#            points): the 4000 cap
research 0 0
research 1 0
lrt 0 512
hab 1 50,50,50,40,40,40,60,60,60
tech 1 energy 26
tech 1 weapons 26
tech 1 prop 26
tech 1 con 26
tech 1 elec 26
tech 1 bio 26
design 1 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Scout
design 1 1 Mini-Miner, 1 Long Hump 6, 1 Rhino Scanner, 1 Robo-Super-Miner, 1 Robo-Super-Miner = SuperMiner
planet 13 owner 0 pop 10430 starbase none
planetset 13 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
planetset 13 env=70,50,50 orig=70,50,50
queue 13 none
planet 9 owner 0 pop 45000 starbase none
planetset 9 mines=0 factories=10 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 9 none
planet 12 owner 0 pop 5000 starbase none
planetset 12 mines=500 factories=0 defenses=0 excess=0 conc=4,100,100 env=50,50,50 orig=50,50,50
queue 12 none
planet 16 owner 0 pop 5000 starbase none
planetset 16 mines=0 factories=0 defenses=95 excess=0 fe=1000 bo=1000 ge=1000 env=50,50,50 orig=50,50,50
queue 16 2:100:1
queue 17 none
queue 8 none
planet 10 owner 1 pop 1000 starbase none
planetset 10 mines=0 factories=10 defenses=5 excess=0 fe=100 bo=100 ge=100 env=90,50,50 orig=90,50,50
queue 10 2:100:1
planet 11 owner 1 pop 1000 starbase none
planetset 11 mines=0 factories=0 defenses=0 excess=0 env=90,90,50 orig=90,90,50
queue 11 none
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 1 0 planet 8 at 1169 1145 ships 0:1
fleet 1 1 planet 14 at 1268 1317 ships 1:80 fuel 100 task mine
