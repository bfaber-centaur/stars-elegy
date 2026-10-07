# KB-2B: Super Stealth research stealing under slower tech (game option 0x82).
# The KX-003 S3L start (experiments/kx003/kx3s3l.spec) on the slower-tech base;
# player 0 researches weapons (set after the build with hst-edit field=1,6).
research 0 100
research 1 100
prt 0 3
prt 1 1
lrt 1 0x1b80
tech 0 energy 3
tech 0 weapons 3
tech 0 prop 3
tech 0 con 3
tech 0 elec 3
tech 0 bio 3
tech 1 energy 3
tech 1 weapons 3
tech 1 prop 3
tech 1 con 3
tech 1 elec 3
tech 1 bio 3
design 0 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Tank
design 1 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Tank
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 1 0 planet 8 at 1169 1145 ships 0:1
planet 0 owner 0 pop 500 starbase none
planet 1 owner 0 pop 500 starbase none
planet 2 owner 0 pop 2200 starbase none
planet 4 owner 1 pop 600 starbase none
planetset 0 mines=0 factories=0 defenses=0 excess=0 env=60,42,56 orig=60,42,56
planetset 1 mines=0 factories=0 defenses=0 excess=0 env=58,50,50 orig=60,50,50
planetset 2 mines=0 factories=0 defenses=0 excess=0 env=50,50,50
planetset 4 mines=0 factories=0 defenses=0 excess=0 env=50,50,50
