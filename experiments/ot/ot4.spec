# OT-4: Claim Adjuster year-end terraforming (turn order 7.3) before Orbital
# Adjusters (7.4). Player 1 is CA; player 0 owns a one-adjuster fleet in
# orbit of player 1's planet 15 (no starbase), environment and original
# 50/50/60. Both players at tech 26 (reach 15 on every axis; no level-up
# is possible within the year). Mutual enemies, no weapons.
research 0 0
research 1 0
prt 1 3
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
design 0 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Scout
design 0 1 Mini-Miner, 1 Long Hump 6, empty, 1 Orbital Adjuster, empty = OA1
planet 15 owner 1 pop 500 starbase none
planetset 15 mines=0 factories=0 defenses=0 excess=0 env=50,50,60 orig=50,50,60
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 0 1 planet 15 at 1281 1064 ships 1:1 fuel 100
fleet 1 0 planet 8 at 1169 1145 ships 1:1
