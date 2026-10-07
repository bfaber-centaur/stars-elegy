# KB-3A: the year-wide random draw order, by replaying the random stream.
# One year interleaves a tech attempt from scrapping at a starbase (before
# movement), mining, the random events, and a bombing pass (after
# movement). Random events on (option byte 0x40, set by run-kb.sh), year
# 2400. No queues, no fleets in motion, no battles.
#   - Player 0 (tech 26) scraps a Scout with a Long Hump 6 (propulsion 3)
#     at player 1's planet 12, which has an Orbital Fort. Player 1 (tech 0
#     in every field) makes one tech attempt: rand(100), below 50 nothing;
#     otherwise 13 rand(13) Trader tries (no Trader parts, so no second
#     draws), then rand(6) until propulsion (2) comes up, at most 6.
#   - Mining draws: planet 8's germanium, planet 13's three minerals
#     (25 mines at 114/97/14), planet 17's germanium.
#   - Random events (year index 0: comet and new-minerals draws pick a
#     planet and do nothing; climate change acts).
#   - Player 0's Mini Bomber with one LBU-17 (I 16, A 2, no minimum)
#     orbits player 1's planet 13 (no starbase; mines 25, factories 45,
#     defenses 0; pop 880, 1,012 after growth): factories lose
#     10 + [rand(70) < 20]; no defense draw; population loses
#     2 + [rand(1000) <= 24].
research 0 0
research 1 0
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
tech 1 energy 0
tech 1 weapons 0
tech 1 prop 0
tech 1 con 0
tech 1 elec 0
tech 1 bio 0
design 0 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Tank
design 0 1 Scout, 1 Long Hump 6, empty = Scout LH6
design 0 2 Mini Bomber, 1 Long Hump 6, 1 LBU-17 Bomb = LBU17
sbdesign 1 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Station
sbdesign 1 1 Orbital Fort, empty, empty, empty, empty, empty = Fort
planet 12 owner 1 pop 500 starbase 1
planetset 12 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
planet 13 owner 1 pop 880 starbase none
planetset 13 mines=25 factories=45 defenses=0 excess=0 conc=114,97,14 env=50,50,50 orig=50,50,50
queue 12 none
queue 13 none
queue 8 none
queue 17 none
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 0 1 planet 12 at 1245 1158 ships 1:1 fuel 100 task scrap
fleet 0 2 planet 13 at 1249 1354 ships 2:1 fuel 100
fleet 1 0 planet 8 at 1169 1145 ships 0:1
