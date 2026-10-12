# RG-002 start: edits to AIX 2461 (ai/aix/y061/after). Every edit is listed
# here; nothing else changes. Built with combatlab build, then hst-edit for
# player 0's next field, then hst-edit xy for slower tech.
keepfleets-ordered

# Player 0 (the idle human slot): JOAT + ARM, habitat unchanged; energy
# raised from 12 to 25 (other levels as they were), research 30% (was 15%),
# energy accumulation set close to level 26 under slower tech.
prt 0 9
lrt 0 0x0004
tech 0 energy 25
tech 0 weapons 7
tech 0 prop 8
tech 0 con 8
tech 0 elec 8
tech 0 bio 5
research 0 30
field 0 energy
accum 0 energy 84450

# Designs: keepdesigns keeps every existing design and only adds or
# replaces the slots named here.
# Player 0: ship slot 3 a remote miner; starbase slot 1 a second Space Station
# design (queued at the homeworld to replace its Space Station), 2 an Orbital
# Fort, 3 an Ultra Station (placed on colony 100).
keepdesigns
design 0 3 Miner, 2 Long Hump 6, empty, 2 Robo-Midget Miner, 1 Robo-Midget Miner, 2 Robo-Midget Miner, 1 Robo-Midget Miner = Digger
sbdesign 0 1 Space Station, empty, 16 Laser, 16 Mole-skin Shield = Home Station
sbdesign 0 2 Orbital Fort, empty, 12 Laser, 12 Mole-skin Shield = Fort
sbdesign 0 3 Ultra Station, empty, 16 Laser, empty, 16 Laser, 20 Mole-skin Shield, 20 Mole-skin Shield = Ultra
# Macinti (AR): its empty starbase slot 3 gets a Death Star (an AR-only
# hull), placed on its planet 46.
sbdesign 6 3 Death Star, empty, 32 Beta Torpedo, empty, 30 Bear Neutrino Barrier, 30 Bear Neutrino Barrier = Death Star
planet 46 starbase 3

# Player 0 planets: the homeworld plus three unowned planets (the
# computer players' own orders refer to the planets they own, so none is
# taken from them). The colonies' current environment is moved inside
# player 0's range on one axis each. Auto items on every queue and in the
# default queue; the homeworld also queues its starbase slot 1 to
# replace its Space Station.
defqueue 0 1:100,0:100,2:20,4:5,5:5
planet 51 pop 18000
planet 92 owner 0 pop 800 starbase none
planet 95 owner 0 pop 2600 starbase 2
planet 100 owner 0 pop 3000 starbase 3
planetset 51 conc=25,22,28
planetset 92 mines=10 factories=10 env=18,23,84 conc=3,69,91
planetset 95 mines=20 factories=20 env=69,33,84 conc=74,5,81
planetset 100 mines=30 factories=30 env=57,80,58
queue 51 17:1:2,1:100:1,0:100:1,2:20:1,4:5:1,5:5:1
queue 92 1:100:1,0:100:1,2:20:1,4:5:1,5:5:1
queue 95 1:100:1,0:100:1,2:20:1,4:5:1,5:5:1
queue 100 1:100:1,0:100:1,2:20:1,4:5:1,5:5:1

# Player 0 fleets (fleet 1, the freighter at the homeworld, is kept):
# remote miners on four unowned planets, a scout in deep space, and a
# freighter with colonists two years from colony 92.
fleet 0 2 planet 73 at 1418 1030 ships 3:1 fuel 200 task mine
fleet 0 3 planet 87 at 1525 1104 ships 3:1 fuel 200 task mine
fleet 0 4 planet 116 at 1763 1147 ships 3:1 fuel 200 task mine
fleet 0 5 planet 45 at 1243 1015 ships 3:1 fuel 200 task mine
fleet 0 6 at 1400 1500 ships 0:1 fuel 100
fleet 0 7 at 1559 1375 ships 1:1 fuel 130 cargo 0 0 0 50 to 1559 1335 planet 92 warp 5 task unload

# Rototill (CA): a second Orbital Adjuster ship (its design slot 2) over a
# player 0 colony.
fleet 4 3 planet 95 at 1576 1306 ships 2:1 fuel 210
