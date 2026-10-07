# KB-1B: Alternate Reality maximum population by starbase hull, and AR
# installation caps. Random events off (CB base). Player 1 is AR at tech
# 26, with lesser traits that keep the race legal (No Advanced Scanners,
# Low Starting Population, Bleeding Edge Technology, No Ram Scoop Engines;
# none acts in this year). Research tax 0. Planets at 50/50/50 (hab 100):
#   13: Orbital Fort, pop 2505        (max 2,500 by hull)
#   9:  Space Dock, pop 5005          (max 5,000), environment 80/80/80
#       (hab 3): AR resources use max(25, hab)
#   10: Ultra Station, pop 20005      (max 20,000)
#   11: Death Star, pop 30005         (max 30,000)
#   12: Space Station, pop 10005, queue Auto Mines ×10, Auto Factories
#       ×10, Auto Defenses ×10, 1000 kT of each mineral: AR caps are 0.
#       A player 1 Mini-Miner (2 Robo-Mini-Miners, 8 robot points) orbits
#       it with the remote-mining task: an AR planet adds its owner's
#       stationary miners to its own mines
research 0 0
research 1 0
prt 1 8
lrt 1 7296
tech 1 energy 26
tech 1 weapons 26
tech 1 prop 26
tech 1 con 26
tech 1 elec 26
tech 1 bio 26
sbdesign 1 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Station
sbdesign 1 1 Orbital Fort, empty, empty, empty, empty, empty = Fort
sbdesign 1 2 Space Dock, empty, empty, empty, empty, empty, empty, empty, empty = Dock
sbdesign 1 3 Ultra Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Ultra
sbdesign 1 4 Death Star, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Death
planet 13 owner 1 pop 2505 starbase 1
planetset 13 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 13 none
planet 9 owner 1 pop 5005 starbase 2
planetset 9 mines=0 factories=0 defenses=0 excess=0 env=80,80,80 orig=80,80,80
queue 9 none
planet 10 owner 1 pop 20005 starbase 3
planetset 10 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 10 none
planet 11 owner 1 pop 30005 starbase 4
planetset 11 mines=0 factories=0 defenses=0 excess=0 env=50,50,50 orig=50,50,50
queue 11 none
planet 12 owner 1 pop 10005 starbase 0
planetset 12 mines=0 factories=0 defenses=0 excess=0 fe=1000 bo=1000 ge=1000 env=50,50,50 orig=50,50,50
queue 12 0:10:1,1:10:1,2:10:1
queue 8 none
queue 17 none
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 1 0 planet 8 at 1169 1145 ships 0:1
fleet 1 1 planet 12 at 1245 1158 ships 5:1 fuel 100 task mine
