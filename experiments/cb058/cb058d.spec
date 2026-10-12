# CB-058 run D (Q1 rerun): run A's Q1 with the Jam BB on plan 0, so it closes in; run A's Jam BB (plan Hold) was never approached: both players JOAT, no cost LRT, tech 26, mutual enemies.
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
# Q1: three Alpha DDs (computer 0) against the Jam BB (jammer 95, no shields, one Laser, default plan): p = 1
fleet 0 1 at 1000 1400 ships 0:1 fuel 300
fleet 0 2 at 1000 1400 ships 0:1 fuel 300
fleet 0 3 at 1000 1400 ships 0:1 fuel 300
fleet 1 1 at 1000 1400 ships 0:1 fuel 300
