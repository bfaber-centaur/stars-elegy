# CB-009: deterministic deep-space cases (Q-6, Q-7, Q-8, Q-14). Mutual enemies, tech 26.
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
design 0 0 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 0 1 Cruiser, 2 Trans-Star 10, empty, empty, 2 Jihad Missile, empty, empty, empty = Jihad Cruiser
design 0 2 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, 2 Tritanium, empty, empty = Laser DD
design 0 3 Cruiser, 2 Trans-Star 10, empty, empty, 2 Beta Torpedo, empty, empty, empty = Beta Cruiser
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Small Freighter, 1 Quick Jump 5, empty, 1 Beam Deflector = Deflector Hauler
design 1 2 Frigate, 1 Long Hump 6, empty, 1 Laser, 1 Beam Deflector = Deflector Gunboat
design 1 3 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 1 4 Frigate, 1 Long Hump 6, 1 Fuel Tank, 2 Laser, empty = Tank Frigate
design 1 5 Frigate, 1 Long Hump 6, empty, empty, 2 Mole-skin Shield = Shield Frigate
plan 0 1 5 1 0 1 = Max Any
plan 1 1 5 1 0 1 = Max Any
plan 1 2 5 1 0 0 = Nobody
# K1 (Q-8): 202 Jihads vs 1000 unshielded freighters
fleet 0 0 at 1020 1230 ships 1:101 plan 1 fuel 500
fleet 1 0 at 1020 1230 ships 0:1000 plan 2 fuel 100
# K2 (Q-7): 10 Laser Frigates vs four stacks of 3 deflector freighters (unarmed)
fleet 0 1 at 1060 1230 ships 0:10 plan 1 fuel 100
fleet 1 1 at 1060 1230 ships 1:3 plan 2 fuel 100
fleet 1 2 at 1060 1230 ships 1:3 plan 2 fuel 100
fleet 1 3 at 1060 1230 ships 1:3 plan 2 fuel 100
fleet 1 4 at 1060 1230 ships 1:3 plan 2 fuel 100
# K3 (Q-7, armed targets that close in): 10 Laser Frigates vs four stacks of 3 deflector gunboats
fleet 0 2 at 1100 1230 ships 0:10 plan 1 fuel 100
fleet 1 5 at 1100 1230 ships 2:3 plan 2 fuel 100
fleet 1 6 at 1100 1230 ships 2:3 plan 2 fuel 100
fleet 1 7 at 1100 1230 ships 2:3 plan 2 fuel 100
fleet 1 8 at 1100 1230 ships 2:3 plan 2 fuel 100
# K4 (Q-6): stack size, 3 vs 5 identical frigates
fleet 0 3 at 1140 1230 ships 2:3 plan 1 fuel 100
fleet 1 9 at 1140 1230 ships 3:3 plan 2 fuel 100
fleet 1 10 at 1140 1230 ships 3:5 plan 2 fuel 100
# K5 (Q-6): two equal stacks of 3
fleet 0 4 at 1180 1230 ships 2:3 plan 1 fuel 100
fleet 1 11 at 1180 1230 ships 3:3 plan 2 fuel 100
fleet 1 12 at 1180 1230 ships 3:3 plan 2 fuel 100
# K6 (Q-6): same armor, the more expensive design (fuel tank) vs plain
fleet 0 5 at 1220 1230 ships 2:3 plan 1 fuel 100
fleet 1 13 at 1220 1230 ships 3:3 plan 2 fuel 100
fleet 1 14 at 1220 1230 ships 4:3 plan 2 fuel 100
# K7 (Q-6): damaged stack (100/500 on every ship) vs fresh stack of the same size
fleet 0 6 at 1260 1230 ships 2:3 plan 1 fuel 100
fleet 1 15 at 1260 1230 ships 3:3 plan 2 fuel 100
fleet 1 16 at 1260 1230 ships 3:3 plan 2 fuel 100 dmg 3:100:100
# K8 (Q-14): 20 Beta torpedoes vs shielded frigates (misses against shields)
fleet 0 7 at 1300 1230 ships 3:10 plan 1 fuel 500
fleet 1 17 at 1300 1230 ships 5:3 plan 2 fuel 100
