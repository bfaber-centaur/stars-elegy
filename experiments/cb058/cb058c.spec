# CB-058 run C (Q5): Langston Shell under Regenerating Shields. Player 1 JOAT + RS.
# A: Rogue, 3 Langston Shell in slot 1 (shield or armor). B: Battleship, 3 Langston Shell
# in slot 2 (shield only). C: Rogue, 3 Organic Armor in slot 1. Each carries one Laser and
# plan Hold so it stays; two fleets of each. Player 0's Mega Disruptor Battleship fires.
# Prediction: elegy #187 head eaa474e (TestPredictionCB058LangstonShellRegeneratingShields).
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
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 6 Mega Disruptor, empty, empty, empty, empty, 6 Superlatanium, empty, empty = MD BB
design 1 0 Rogue, 2 Trans-Galactic Drive, 3 Langston Shell, empty, empty, 1 Laser, empty, empty, empty, empty = Shell Rogue
design 1 1 Battleship, 4 Trans-Galactic Drive, empty, 3 Langston Shell, 1 Laser, empty, empty, empty, empty, empty, empty, empty = Shell BB
design 1 2 Rogue, 2 Trans-Galactic Drive, 3 Organic Armor, empty, empty, 1 Laser, empty, empty, empty, empty = Organic Rogue
plan 0 1 5 1 0 1 = Max Any
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
fleet 1 1 at 1000 1400 ships 0:1 plan 1 fuel 300
fleet 1 2 at 1000 1400 ships 0:1 plan 1 fuel 300
fleet 1 3 at 1000 1400 ships 1:1 plan 1 fuel 300
fleet 1 4 at 1000 1400 ships 1:1 plan 1 fuel 300
fleet 1 5 at 1000 1400 ships 2:1 plan 1 fuel 300
fleet 1 6 at 1000 1400 ships 2:1 plan 1 fuel 300
fleet 0 1 at 1000 1400 ships 0:1 plan 1 fuel 2800
