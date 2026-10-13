# GC-1: ground combat with two drops by one player. Combat Lab base2400.
# Player 1 (JOAT, not IS) owns each target planet: environment 50/50/50
# (100% habitability), carry 0, 10 defenses (Neutron Shield at energy 26).
# Player 0 (JOAT) drops colonists from freighters already in orbit
# (waypoint-0 unload, before movement and growth). Populations and cargo
# are in units of 100 colonists.
relation 0 1 2
relation 1 0 2
tech 1 energy 26
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
research 0 0
research 1 0
design 0 11 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
queue 17 none
queue 8 none
# C: P 329; fleet 0 (2 freighters, 395) then fleet 1 (1 freighter, 165).
planet 2 owner 1 pop 329 starbase none
planetset 2 env=50,50,50 excess=0 scanner=31 defenses=10
fleet 0 0 planet 2 at 1090 1295 ships 11:2 plan 0 fuel 200 cargo 0 0 0 395 task unload
fleet 0 1 planet 2 at 1090 1295 ships 11:1 plan 0 fuel 200 cargo 0 0 0 165 task unload
# C2: as C with the order swapped: fleet 2 (165) then fleet 3 (395).
planet 10 owner 1 pop 329 starbase none
planetset 10 env=50,50,50 excess=0 scanner=31 defenses=10
fleet 0 2 planet 10 at 1224 1359 ships 11:1 plan 0 fuel 200 cargo 0 0 0 165 task unload
fleet 0 3 planet 10 at 1224 1359 ships 11:2 plan 0 fuel 200 cargo 0 0 0 395 task unload
# R: P 600 (repelled); fleet 4 (395) then fleet 5 (165).
planet 20 owner 1 pop 600 starbase none
planetset 20 env=50,50,50 excess=0 scanner=31 defenses=10
fleet 0 4 planet 20 at 1348 1290 ships 11:2 plan 0 fuel 200 cargo 0 0 0 395 task unload
fleet 0 5 planet 20 at 1348 1290 ships 11:1 plan 0 fuel 200 cargo 0 0 0 165 task unload
