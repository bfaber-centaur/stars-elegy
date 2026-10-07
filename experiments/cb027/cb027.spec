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
relation 0 1 2
relation 1 0 2
sbdesign 0 0 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Bare Station
planet 18 owner 0 pop 500 starbase 0
plan 0 0 5 1 0 1 = Station Enemies
design 0 0 Fuel Transport, 1 Quick Jump 5, 1 Mole-skin Shield = Tanker
design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Colloidal Phaser, empty, empty, 2 Tritanium, empty, empty = Hunter
plan 1 1 5 1 0 1 = Max Any
fleet 0 0 planet 18 at 1324 1192 ships 0:1 fuel 100
# one Hunter (primary any) attacks the bare station and the Tanker at planet 18
fleet 1 0 planet 18 at 1324 1192 ships 0:1 plan 1 fuel 100
