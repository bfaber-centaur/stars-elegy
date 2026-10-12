# CB-057 Q1: Regenerating Shields with Organic Armor in two separate armor slots.
# Player 1 JOAT + Regenerating Shields, tech 26. Destroyers with one Organic Armor
# in the general-purpose slot and one in the armor slot ("Split"), against the
# control with both in the armor slot ("Pair"). Each carries one Laser and uses a
# plan whose targets miss the attacker, so it stays on the board without firing.
# Player 0's Laser Battleships fire at them; the damage units give the armor.
# Prediction: elegy #185 head 89cbc6a (TestPredictionCB057RegeneratingShieldsTwoSlots).
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
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Laser, empty, empty, empty, empty, 6 Superlatanium, empty, empty = Laser BB
design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, 1 Organic Armor, 1 Organic Armor, empty, empty = Split DD
design 1 1 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Organic Armor, empty, empty = Pair DD
plan 0 1 5 1 0 1 = Max Any
plan 1 1 4 6 0 1 = Hold
queue 17 none
queue 8 none
fleet 1 1 at 1000 1400 ships 0:1 plan 1 fuel 300
fleet 1 2 at 1000 1400 ships 0:1 plan 1 fuel 300
fleet 1 3 at 1000 1400 ships 0:1 plan 1 fuel 300
fleet 1 4 at 1000 1400 ships 1:1 plan 1 fuel 300
fleet 1 5 at 1000 1400 ships 1:1 plan 1 fuel 300
fleet 1 6 at 1000 1400 ships 1:1 plan 1 fuel 300
fleet 0 1 at 1000 1400 ships 0:1 plan 1 fuel 2800
fleet 0 2 at 1000 1400 ships 0:1 plan 1 fuel 2800
