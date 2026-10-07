prt 0 4
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
relation 0 1 0
relation 1 0 0
design 0 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 0 1 Fuel Transport, 1 Quick Jump 5, empty = Tanker
sbdesign 0 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Bare Station
sbdesign 0 1 Orbital Fort, empty, empty, empty, empty, empty = Bare Fort
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Fuel Transport, 1 Quick Jump 5, empty = Tanker
sbdesign 1 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Bare Station
sbdesign 1 1 Orbital Fort, empty, empty, empty, empty, empty = Bare Fort
planet 12 owner 0 pop 500 starbase none
planet 18 owner 0 pop 500 starbase 1
planet 5 owner 1 pop 500 starbase none
planet 0 owner 1 pop 500 starbase 1
planetset 17 sbdmg=200
planetset 8 sbdmg=200
planetset 18 sbdmg=100
planetset 0 sbdmg=100
fleet 0 0 at 1020 1230 ships 0:1 fuel 100 dmg 0:400:100
fleet 0 1 at 1100 1230 ships 0:1 fuel 100 dmg 0:400:100 to 1160 1230 warp 5
fleet 0 2 planet 8 at 1169 1145 ships 0:1 fuel 100 dmg 0:400:100
fleet 0 3 planet 17 at 1306 1060 ships 0:1 fuel 100 dmg 0:400:100
fleet 0 4 planet 12 at 1245 1158 ships 0:1 fuel 100 dmg 0:400:100
fleet 0 5 planet 18 at 1324 1192 ships 0:1 fuel 100 dmg 0:400:100
fleet 0 6 at 1220 1230 ships 0:1,1:1 fuel 100 dmg 0:400:100,1:400:100
fleet 1 0 at 1060 1230 ships 0:1 fuel 100 dmg 0:400:100
fleet 1 1 at 1100 1260 ships 0:1 fuel 100 dmg 0:400:100 to 1160 1260 warp 5
fleet 1 2 planet 17 at 1306 1060 ships 0:1 fuel 100 dmg 0:400:100
fleet 1 3 planet 8 at 1169 1145 ships 0:1 fuel 100 dmg 0:400:100
fleet 1 4 planet 5 at 1146 1180 ships 0:1 fuel 100 dmg 0:400:100
fleet 1 5 planet 0 at 1045 1291 ships 0:1 fuel 100 dmg 0:400:100
fleet 1 6 at 1260 1230 ships 0:1,1:1 fuel 100 dmg 0:400:100,1:400:100
