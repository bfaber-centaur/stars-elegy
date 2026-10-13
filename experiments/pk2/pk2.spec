# PK-2 year 1: what sets a planet's packet settings when its starbase is rebuilt.
# A state edit on Combat Lab base2400 (combatlab build). Player 0 planets carry a
# Launch 10 starbase (Orbital Fort + Ultra Driver 10) with packet destination
# planet 17 at warp 10. Player 1 Laser destroyers sit at six of them and destroy
# the starbase there; nothing is queued this year. Year 2 (pk2-y2.spec) removes
# every fleet and queues a rebuild at 99% with a different design on each planet.
# Starbase design slot k is planetary item 16+k, kind 2.
relation 0 1 2
relation 1 0 2
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
research 0 0
research 1 0
sbdesign 0 0 Orbital Fort, empty, empty, empty, empty, empty = Fort
sbdesign 0 1 Orbital Fort, 1 Ultra Driver 10, empty, empty, empty, empty = Launch 10
sbdesign 0 2 Orbital Fort, 1 Mass Driver 5, empty, empty, empty, empty = Launch 5
sbdesign 0 3 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Launch 7
sbdesign 0 4 Orbital Fort, 1 Super Driver 8, empty, empty, empty, empty = Launch 8
sbdesign 0 5 Orbital Fort, 1 Ultra Driver 12, empty, empty, empty, empty = Launch 12
design 1 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD
plan 1 0 4 1 0 1 = Enemies
# (R5) attacked this year; year 2 rebuilds Launch 5 (Mass Driver 5)
planet 4 owner 0 pop 20000 starbase 1
planetset 4 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
fleet 1 0 planet 4 at 1143 1103 ships 0:10 plan 0 fuel 1400
# (R7) attacked this year; year 2 rebuilds Launch 7 (Mass Driver 7)
planet 6 owner 0 pop 20000 starbase 1
planetset 6 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
fleet 1 1 planet 6 at 1166 1017 ships 0:10 plan 0 fuel 1400
# (R8) attacked this year; year 2 rebuilds Launch 8 (Super Driver 8)
planet 1 owner 0 pop 20000 starbase 1
planetset 1 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
fleet 1 2 planet 1 at 1071 1087 ships 0:10 plan 0 fuel 1400
# (R12) attacked this year; year 2 rebuilds Launch 12 (Ultra Driver 12)
planet 11 owner 0 pop 20000 starbase 1
planetset 11 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
fleet 1 3 planet 11 at 1243 1123 ships 0:10 plan 0 fuel 1400
# (R0) attacked this year; year 2 rebuilds Fort (no driver)
planet 15 owner 0 pop 20000 starbase 1
planetset 15 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
fleet 1 4 planet 15 at 1281 1064 ships 0:10 plan 0 fuel 1400
# (R10) attacked this year; year 2 rebuilds Launch 10 again (Ultra Driver 10)
planet 18 owner 0 pop 20000 starbase 1
planetset 18 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
fleet 1 5 planet 18 at 1324 1192 ships 0:10 plan 0 fuel 1400
# (K) control: not attacked; Launch 10 kept, nothing queued in either year
planet 3 owner 0 pop 20000 starbase 1
planetset 3 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
# (U) control: not attacked; year 2 replaces Launch 10 with Launch 5 (no loss)
planet 9 owner 0 pop 20000 starbase 1
planetset 9 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,10
# (F) control: never had a starbase; year 2 builds Launch 5
planet 13 owner 0 pop 20000 starbase none
planetset 13 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
