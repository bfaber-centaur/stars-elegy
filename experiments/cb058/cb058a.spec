# CB-058 run A (Q1, Q3, Q6): both players JOAT, no cost LRT, tech 26, mutual enemies.
# Prediction: elegy #187 head eaa474e (engine/combat_cb058_test.go).
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
keepdesigns
research 0 0
research 1 0
relation 0 1 2
relation 1 0 2
design 0 0 Destroyer, 1 Long Hump 6, 1 Alpha Torpedo, empty, empty, empty, empty, empty = Alpha DD
design 0 1 Destroyer, 1 Trans-Galactic Drive, 1 Heavy Blaster, empty, empty, 2 Superlatanium, empty, empty = Blaster DD
sbdesign 0 1 Death Star, empty, 8 Heavy Blaster, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Blaster Star
design 1 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Laser, empty, empty, empty, empty, empty, 3 Jammer 50, 3 Jammer 50 = Jam BB
design 1 1 Large Freighter, 2 Long Hump 6, empty, empty = Hauler
design 1 2 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Superlatanium, empty, empty = Laser DD
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
# Q1: three Alpha DDs (computer 0) against the Jam BB (jammer 95, no shields; Laser and plan Hold so it stays): p = 1
fleet 0 1 at 1000 1400 ships 0:1 fuel 300
fleet 0 2 at 1000 1400 ships 0:1 fuel 300
fleet 0 3 at 1000 1400 ships 0:1 fuel 300
fleet 1 1 at 1000 1400 ships 0:1 plan 1 fuel 300
# Q3: four Haulers with 1000 Fe, 700 Bo, 333 Ge, 500 kT colonists (plan 0: no dump) against one Blaster DD
fleet 1 2 at 1020 1230 ships 1:4 fuel 2000 cargo 1000 700 333 500
fleet 0 4 at 1020 1230 ships 1:1 fuel 300
# Q6: the Blaster Star at player 0's planet 6 against four one-ship Laser DD fleets (default plan: they close in)
planet 6 owner 0 pop 1000 starbase 1
queue 6 none
fleet 1 3 planet 6 at 1166 1017 ships 2:1 fuel 300
fleet 1 4 planet 6 at 1166 1017 ships 2:1 fuel 300
fleet 1 5 planet 6 at 1166 1017 ships 2:1 fuel 300
fleet 1 6 planet 6 at 1166 1017 ships 2:1 fuel 300
