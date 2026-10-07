# KB-2A: production pre-checks, the zero-item queue, the Ultimate Recycling
# scrap bonus, and field switching after a "same field" research reaches 26.
# Random events off (CB base).
# Player 0: JOAT, levels 25/0/0/5/5/5, energy current, next field "same",
# stored energy 85,080 (set after the build with hst-edit field=0,6
# accum=85080,0,0,0,0,0, which edits player 0 only); planet 10 pop 11000.
# Energy reaches 26 and the leftover moves to the lowest field; for the
# rest of the year the switch logic acts as if "lowest field" were chosen.
# Player 1: JOAT with Ultimate Recycling, No Advanced Scanners, Low Starting
# Population and Bleeding Edge Technology (legal), every field at 3, energy
# current, next field "same" (the base's setting). Planets at 50/50/50, no
# mines, factories or defenses:
#   13: pop 5000, no queue; 10 Mini-Miners (owner cost 241 resources each
#       for this race) scrap there (no starbase): the planet's resources
#       r = 500 become r + trunc(x·r/(x + r)) with x = 2410
#   9:  pop 3000, scanner present, queue Planetary Scanner ×1: removed
#       with a message; the planet sends its 300 resources to research
#   12: pop 2000, no starbase, queue Mass Driver packet ×1: removed with
#       a message (no driver); 200 resources to research
#   16: pop 4000, queue block with zero items: contributes nothing
research 0 0
research 1 0
lrt 1 7200
hab 0 50,50,50,15,15,15,85,85,85
tech 1 energy 3
tech 1 weapons 3
tech 1 prop 3
tech 1 con 3
tech 1 elec 3
tech 1 bio 3
tech 0 energy 25
tech 0 weapons 0
tech 0 prop 0
tech 0 con 5
tech 0 elec 5
tech 0 bio 5
design 1 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Scout
design 1 1 Mini-Miner, 1 Quick Jump 5, 1 Bat Scanner, 1 Robo-Mini-Miner, 1 Robo-Mini-Miner = Scrap
design 0 0 Scout, 1 Quick Jump 5, 1 Bat Scanner, 1 Fuel Tank = Scout
planet 13 owner 1 pop 5000 starbase none
planetset 13 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 13 none
planet 9 owner 1 pop 3000 starbase none
planetset 9 mines=0 factories=0 defenses=0 excess=0 scanner=0 env=50,50,50 orig=50,50,50
queue 9 27:1:1
planet 12 owner 1 pop 2000 starbase none
planetset 12 mines=0 factories=0 defenses=0 excess=0 fe=1000 bo=1000 ge=1000 env=50,50,50 orig=50,50,50
queue 12 14:1:1
planet 16 owner 1 pop 4000 starbase none
planetset 16 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 16 empty
queue 8 none
planet 10 owner 0 pop 11000 starbase none
planetset 10 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 10 none
queue 17 none
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 1 0 planet 8 at 1169 1145 ships 0:1
fleet 1 1 planet 13 at 1249 1354 ships 1:10 fuel 100 task scrap
