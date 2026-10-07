# ES-001: client estimates (experiments/es001/gen.py)
tech 0 energy 7
tech 0 weapons 4
tech 0 prop 26
tech 0 con 7
tech 0 elec 9
tech 0 bio 4
research 0 10
field 0 weapons
design 0 0 Scout, 1 Quick Jump 5, empty, empty = R-Quick
design 0 1 Scout, 1 Fuel Mizer, empty, empty = R-Fuel
design 0 2 Scout, 1 Long Hump 6, empty, empty = R-Long
design 0 3 Scout, 1 Daddy Long Legs 7, empty, empty = R-Daddy
design 0 4 Scout, 1 Alpha Drive 8, empty, empty = R-Alpha
design 0 5 Scout, 1 Trans-Galactic Drive, empty, empty = R-Trans-Ga
design 0 6 Scout, 1 Interspace-10, empty, empty = R-Interspa
design 0 7 Scout, 1 Enigma Pulsar, empty, empty = R-Enigma
design 0 8 Scout, 1 Trans-Star 10, empty, empty = R-Trans-St
design 0 9 Scout, 1 Settler's Delight, empty, empty = R-Settler'
design 0 10 Scout, 1 Sub-Galactic Fuel Scoop, empty, empty = R-Sub-Gala
design 0 11 Scout, 1 Trans-Galactic Mizer Scoop, empty, empty = R-Trans-Ga
design 0 12 Scout, 1 Galaxy Scoop, empty, empty = R-Galaxy
design 0 13 Medium Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 0 14 Fuel Transport, 1 Long Hump 6, empty = Tanker
design 0 15 Scout, 1 Sub-Galactic Fuel Scoop, 1 Rhino Scanner, empty = Scoop
fleet 0 0 at 1020 1230 ships 13:3 fuel 400 cargo 300 0 0 0 to 1020 1230 warp 5 to 1040 1250 warp 5 to 1040 1300 warp 6 to 1070 1330 warp 4
fleet 0 1 at 1100 1230 ships 2:1 fuel 50 to 1100 1230 warp 5 to 1130 1230 warp 0 to 1150 1230 warp 6
fleet 0 2 at 1100 1260 ships 0:1 fuel 50 to 1100 1260 warp 5 to 1103 1262 warp 1 to 1103 1262 warp 5 to 1160 1262 warp 7
fleet 0 3 at 1020 1030 ships 13:2,15:1 fuel 300 cargo 100 0 0 0 to 1020 1030 warp 5 to 1120 1030 warp 5 to 1120 1130 warp 6
fleet 0 4 at 1020 1100 ships 14:1,13:1 fuel 300 to 1020 1100 warp 5 to 1170 1100 warp 6 to 1170 1200 warp 7
fleet 0 5 at 1250 1020 ships 13:1 fuel 200 to 1250 1020 warp 5 to 1306 1060 planet 17 warp 7 to 1390 1010 warp 8 to 1390 1210 warp 9
fleet 0 6 at 1200 1390 ships 4:1 fuel 30 to 1200 1390 warp 5 to 1390 1390 warp 9 to 1390 1200 warp 8
fleet 0 7 at 1050 1160 ships 2:1 fuel 50 to 1050 1160 warp 5 to 1075 1165 warp 5 to 1100 1165 warp 5
fleet 0 8 at 1060 1380 ships 9:1 fuel 20 to 1060 1380 warp 5 to 1110 1380 warp 3 to 1200 1380 warp 6
fleet 0 9 at 1030 1340 ships 0:1 fuel 23
fleet 0 10 at 1055 1340 ships 1:1 fuel 24
fleet 0 11 at 1080 1340 ships 2:1 fuel 25
fleet 0 12 at 1105 1340 ships 3:1 fuel 26
fleet 0 13 at 1130 1340 ships 4:1 fuel 27
fleet 0 14 at 1155 1340 ships 5:1 fuel 28
fleet 0 15 at 1180 1340 ships 6:1 fuel 29
fleet 0 16 at 1205 1340 ships 7:1 fuel 30
fleet 0 17 at 1230 1340 ships 8:1 fuel 31
fleet 0 18 at 1255 1340 ships 9:1 fuel 32
fleet 0 19 at 1280 1340 ships 10:1 fuel 33
fleet 0 20 at 1305 1340 ships 11:1 fuel 34
fleet 0 21 at 1330 1340 ships 12:1 fuel 35
fleet 0 22 at 1030 1060 ships 13:2,15:1 fuel 333 cargo 150 0 0 0
planet 15 owner 0 pop 200 starbase none
planetset 15 excess=0 defenses=0 mines=20 factories=20 fe=500 bo=500 ge=500 conc=60,60,60 env=50,50,50
queue 15 7:200:1
planet 19 owner 0 pop 400 starbase none
planetset 19 excess=0 defenses=0 mines=10 factories=40 fe=300 bo=300 ge=10 conc=50,50,1 env=50,50,50
queue 19 8:20:1,7:100:1
planet 21 owner 0 pop 100 starbase none
planetset 21 excess=0 defenses=0 mines=0 factories=10 fe=100 bo=100 ge=0 conc=40,40,1 env=50,50,50
queue 21 7:5:1,8:3:1
planet 11 owner 0 pop 700 starbase none
planetset 11 excess=0 defenses=0 mines=10 factories=10 fe=3000 bo=3000 ge=3000 conc=30,30,30 env=34,50,50 orig=34,50,50
queue 11 0:50:1,2:50:1,8:5:1
planet 12 owner 0 pop 300 starbase none
planetset 12 excess=0 defenses=0 mines=30 factories=30 fe=5 bo=5 ge=5 conc=20,20,20 env=50,50,50
queue 12 3:1:1,7:10:1,8:5:1
planet 18 owner 0 pop 300 starbase none
planetset 18 excess=0 defenses=0 mines=20 factories=20 fe=50 bo=50 ge=50 conc=40,40,40 env=30,50,62 orig=30,50,62
queue 18 8:5:1,7:3:1,3:1:1
planet 4 owner 0 pop 150 starbase none
planetset 4 excess=0 defenses=0 mines=15 factories=15 fe=0 bo=0 ge=0 conc=10,10,1 env=50,50,50
queue 4 1:20:1,8:5:1
planet 6 owner 0 pop 50 starbase none
planetset 6 excess=0 defenses=0 mines=0 factories=0 fe=20 bo=20 ge=20 conc=10,10,10 env=95,50,50
queue 6 none
planet 5 owner 0 pop 2000 starbase none
planetset 5 excess=0 defenses=0 mines=10 factories=10 fe=100 bo=100 ge=100 conc=30,30,30 env=17,17,17 orig=17,17,17
queue 5 7:20:1,8:30:1,9:10:1
