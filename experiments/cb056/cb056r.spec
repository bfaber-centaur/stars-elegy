# CB-056 run R (Q3, Q7): player 1 JOAT with Regenerating Shields.
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
lrt 1 0x2000
keepdesigns
research 0 0
research 1 0
relation 0 1 2
relation 1 0 2
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 6 Heavy Blaster, 6 Heavy Blaster, empty, empty, empty, 6 Superlatanium, empty, empty = HB BB
design 1 0 Battleship, 4 Trans-Galactic Drive, empty, 1 Mole-skin Shield, empty, empty, empty, empty, empty, 2 Superlatanium, empty, empty = BB
design 1 1 Battleship, 4 Trans-Galactic Fuel Scoop, empty, 1 Mole-skin Shield, empty, empty, empty, empty, empty, 2 Superlatanium, empty, empty = Scoop BB
design 1 2 Destroyer, 1 Trans-Galactic Drive, empty, empty, empty, 2 Superlatanium, empty, empty = Tank
design 1 3 Battleship, 4 Trans-Galactic Drive, empty, 1 Mole-skin Shield, empty, empty, empty, empty, empty, 2 Superlatanium, empty, empty = BB 2
design 1 4 Battleship, 4 Trans-Galactic Drive, empty, 8 Croby Sharmor, empty, empty, empty, empty, empty, 2 Tritanium, empty, empty = Croby BB
plan 0 1 5 1 0 1 = Max Any
queue 17 none
queue 8 none
thing minefield 0 0 1200 1200 50000 kind heavy
fleet 1 1 at 1160 1142 ships 0:5 fuel 2800 to 1241 1142 warp 9
fleet 1 2 at 1160 1153 ships 0:5 fuel 2800 to 1241 1153 warp 9
fleet 1 3 at 1160 1163 ships 0:5 fuel 2800 to 1241 1163 warp 9
fleet 1 4 at 1160 1174 ships 0:5 fuel 2800 to 1241 1174 warp 9
fleet 1 5 at 1160 1184 ships 0:5 fuel 2800 to 1241 1184 warp 9
fleet 1 6 at 1160 1195 ships 0:5 fuel 2800 to 1241 1195 warp 9
fleet 1 7 at 1160 1205 ships 0:5 fuel 2800 to 1241 1205 warp 9
fleet 1 8 at 1160 1216 ships 0:5 fuel 2800 to 1241 1216 warp 9
fleet 1 9 at 1160 1226 ships 0:5 fuel 2800 to 1241 1226 warp 9
fleet 1 10 at 1160 1237 ships 0:5 fuel 2800 to 1241 1237 warp 9
fleet 1 11 at 1160 1247 ships 0:5 fuel 2800 to 1241 1247 warp 9
fleet 1 12 at 1160 1258 ships 0:5 fuel 2800 to 1241 1258 warp 9
fleet 1 13 at 1000 1400 ships 4:1 fuel 2800
fleet 1 14 at 1000 1400 ships 4:1 fuel 2800
fleet 0 0 at 1000 1400 ships 0:1 plan 1 fuel 2800
