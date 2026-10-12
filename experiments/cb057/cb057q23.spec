# CB-057 Q2 and Q3. Player 0 and player 1 JOAT (no cost LRT), tech 26, mutual enemies.
# Prediction: elegy #185 head 89cbc6a (TestPredictionCB057NexusTorpedoes,
# TestPredictionCB057TargetCostCap).
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
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 6 Beta Torpedo, empty, empty, empty, empty, 6 Superlatanium, empty, empty = Probe BB
design 0 1 Destroyer, 1 Trans-Galactic Drive, 1 Heavy Blaster, empty, empty, 2 Superlatanium, empty, empty = Blaster DD
sbdesign 0 1 Death Star, empty, 32 Delta Torpedo, 4 Battle Nexus, 4 Battle Nexus, empty, empty, 4 Battle Nexus, empty, 4 Battle Nexus, empty, empty, empty, empty, empty, empty, empty = Torp Star
design 1 0 Battleship, 4 Trans-Galactic Drive, empty, 4 Mole-skin Shield, 1 Laser, empty, empty, empty, empty, 6 Superlatanium, empty, empty = Target BB
design 1 1 Battleship, 4 Trans-Galactic Drive, empty, empty, 6 Omega Torpedo, 6 Omega Torpedo, empty, empty, empty, empty, empty, empty = Omega BB
design 1 2 Destroyer, 1 Long Hump 6, empty, empty, empty, empty, empty, empty = Hump DD
plan 0 1 5 1 0 1 = Max Any
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
# Q2: the computer-99 Torp Star at player 0's planet 6 against 20 shielded Target BBs
# (shields 4 x 25 per ship, so a salvo's hits show as shield damage 13 per hit).
# The Probe BB (computer 0, 6 Beta Torpedoes) draws after the Torp Star in each round.
planet 6 owner 0 pop 1000 starbase 1
queue 6 none
fleet 1 1 planet 6 at 1166 1017 ships 0:20 fuel 2800
fleet 0 1 planet 6 at 1166 1017 ships 0:1 fuel 2800
# Q3: one Blaster DD (plan primary any) against S2 (16000 Omega BBs, first in token
# order, plan Hold so it never fires) and S1 (10000 Hump DDs, unarmed).
fleet 1 2 at 1000 1400 ships 1:16000 plan 1 fuel 30000
fleet 1 3 at 1000 1400 ships 2:10000 fuel 3000
fleet 0 2 at 1000 1400 ships 1:1 plan 1 fuel 300
