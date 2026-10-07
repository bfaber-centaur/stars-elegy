# ES-002: client estimates, BINARY-ONLY follow-up (experiments/es002/gen.py)
tech 0 energy 7
tech 0 weapons 4
tech 0 prop 26
tech 0 con 7
tech 0 elec 9
tech 0 bio 4
lrt 0 0x1b90
research 0 10
field 0 weapons
tech 1 energy 25
tech 1 weapons 3
tech 1 prop 3
tech 1 con 3
tech 1 elec 3
tech 1 bio 3
research 1 15
field 1 energy
accum 1 energy 85090
design 0 0 Scout, 1 Long Hump 6, empty, empty = Gater
design 0 1 Medium Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 0 2 Medium Freighter, 1 Quick Jump 5, empty, 1 Crobmnium = Heavy
sbdesign 0 0 Space Station, Stargate 100/250, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Gate Station
sbdesign 0 1 Orbital Fort, Stargate 100/250, empty, empty, empty, empty = Gate A
sbdesign 0 2 Orbital Fort, Stargate 150/600, empty, empty, empty, empty = Gate B
planet 15 owner 0 pop 200 starbase 1
planetset 15 excess=0 defenses=0 mines=20 factories=20 fe=300 bo=300 ge=300 conc=50,50,50 env=50,50,50
planet 19 owner 0 pop 200 starbase 1
planetset 19 excess=0 defenses=0 mines=20 factories=20 fe=300 bo=300 ge=300 conc=50,50,50 env=50,50,50
planet 16 owner 0 pop 100 starbase 1
planetset 16 excess=0 defenses=0 mines=10 factories=10 fe=100 bo=100 ge=100 conc=50,50,50 env=50,50,50
planet 4 owner 0 pop 150 starbase 2
planetset 4 excess=0 defenses=0 mines=15 factories=15 fe=100 bo=100 ge=100 conc=50,50,50 env=50,50,50
planet 21 owner 0 pop 100 starbase none
planetset 21 excess=0 defenses=0 mines=10 factories=10 fe=100 bo=100 ge=100 conc=40,40,40 env=50,50,50
planet 18 owner 0 pop 300 starbase none
planetset 18 excess=0 defenses=0 mines=500 factories=20 fe=50 bo=50 ge=50 conc=40,40,40 env=50,50,50
queue 18 0:50:1,8:5:1
planet 11 owner 0 pop 700 starbase none
planetset 11 excess=0 mines=10 factories=10 defenses=100 fe=3000 bo=3000 ge=3000 conc=30,30,30 env=50,50,50
queue 11 2:50:1,1:20:1,7:5:1
planet 17 owner 0 pop 250 starbase 0
fleet 0 0 planet 15 at 1281 1064 ships 0:1 fuel 50 to 1281 1064 warp 5 to 1342 1123 planet 19 warp 11 to 1342 1150 warp 5
fleet 0 1 planet 15 at 1281 1064 ships 1:1 fuel 100 cargo 50 0 0 0 to 1281 1064 warp 5 to 1342 1123 planet 19 warp 11
fleet 0 2 planet 15 at 1281 1064 ships 0:1 fuel 50 to 1281 1064 warp 5 to 1284 1383 planet 16 warp 11
fleet 0 3 planet 4 at 1143 1103 ships 2:1 fuel 100 to 1143 1103 warp 5 to 1342 1123 planet 19 warp 11
fleet 0 4 planet 15 at 1281 1064 ships 0:1 fuel 50 to 1281 1064 warp 5 to 1359 1121 planet 21 warp 11
fleet 0 5 planet 15 at 1281 1064 ships 0:1 fuel 50 to 1281 1064 warp 5 to 1169 1145 planet 8 warp 11
fleet 0 6 planet 15 at 1281 1064 ships 0:1 fuel 50 to 1281 1064 warp 5 to 1300 1100 warp 11
fleet 0 7 planet 15 at 1281 1064 ships 0:1 fuel 50 to 1281 1064 warp 5 to 1245 1158 planet 12 warp 11
fleet 0 8 planet 21 at 1359 1121 ships 0:1 fuel 50 to 1359 1121 warp 5 to 1342 1123 planet 19 warp 11
fleet 0 9 planet 17 at 1306 1060 ships 0:1 fuel 50 to 1306 1060 warp 5 to 1281 1064 planet 15 warp 11 to 1342 1123 planet 19 warp 11
fleet 0 10 at 1020 1230 ships 0:1 fuel 50 to 1020 1230 warp 5 to 1040 1231 warp 5 to 1050 1232 warp 5 to 1053 1233 warp 2 to 1058 1234 warp 3
fleet 0 11 at 1020 1260 ships 0:1 fuel 50 to 1020 1260 warp 5 to 1020 1263 warp 2 to 1027 1264 warp 3
