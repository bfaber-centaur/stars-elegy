# OT-3: a packet launched this year flies half a year and hits (turn order
# step 5) before bombing (6a). Player 0 (tech 26) launches 1000 kT of
# ironium from planet 21 (Orbital Fort with a Mass Driver 7, packet speed
# left at the default) at player 1's planet 19, 17 ly away. Four player 0
# Lady Finger bombers orbit planet 19. Planet 19 has no starbase and no
# defenses and holds 150 units. Mutual enemies.
research 0 0
research 1 0
relation 0 1 2
relation 1 0 2
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
design 0 0 Scout, 1 Long Hump 6, 1 Rhino Scanner, 1 Fuel Tank = Scout
design 0 1 Mini Bomber, 1 Long Hump 6, 2 Lady Finger Bomb = Bomber
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase
sbdesign 0 1 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Catcher 7
plan 0 0 4 1 0 1 = Enemies
planet 21 owner 0 pop 3000 starbase 1
planetset 21 mines=0 factories=0 defenses=0 excess=0 fe=2000 bo=0 ge=0 driver=19
queue 21 14:10:1
planet 19 owner 1 pop 150 starbase none
planetset 19 mines=0 factories=0 defenses=0 excess=0
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 0 1 planet 19 at 1342 1123 ships 1:4 fuel 100 plan 0
fleet 1 0 planet 8 at 1169 1145 ships 1:1
