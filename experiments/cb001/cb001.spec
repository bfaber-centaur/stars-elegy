# CB-001: baseline beams (E-1), beams vs shields, torpedo hit counts (E-2)
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
design 0 1 Cruiser, 2 Trans-Star 10, empty, empty, 2 Beta Torpedo, empty, empty, empty = Beta Cruiser
design 0 2 Cruiser, 2 Trans-Star 10, 1 Battle Super Computer, empty, 2 Beta Torpedo, empty, empty, empty = Beta Cruiser BSC
design 1 0 Small Freighter, 1 Quick Jump 5, empty, empty = Hauler
design 1 1 Frigate, 1 Long Hump 6, empty, empty, 2 Mole-skin Shield = Shield Frigate
design 1 2 Battleship, 4 Trans-Star 10, empty, empty, empty, empty, empty, empty, empty, 6 Neutronium, empty, empty = Hulk
design 1 3 Battleship, 4 Trans-Star 10, empty, empty, empty, empty, empty, empty, empty, 6 Neutronium, 1 Jammer 20, empty = Hulk J20
design 1 4 Battleship, 4 Trans-Star 10, empty, empty, empty, empty, empty, empty, empty, 6 Neutronium, 1 Jammer 50, empty = Hulk J50
# plan 1 of player 0: maximize damage, any target, attack enemies
plan 0 1 5 1 0 1 = Max Any
# B1 (E-1) baseline beams vs unarmed freighters
fleet 0 0 at 1020 1230 ships 0:5 plan 1 fuel 100
fleet 1 0 at 1020 1230 ships 0:10 fuel 100
# B2 beams vs shielded unarmed frigates
fleet 0 1 at 1060 1230 ships 0:5 plan 1 fuel 100
fleet 1 1 at 1060 1230 ships 1:4 fuel 100
# B3-B6 (E-2) 202-torpedo salvos vs one armored battleship
fleet 0 2 at 1100 1230 ships 1:101 plan 1 fuel 500
fleet 1 2 at 1100 1230 ships 2:1 fuel 500
fleet 0 3 at 1140 1230 ships 2:101 plan 1 fuel 500
fleet 1 3 at 1140 1230 ships 2:1 fuel 500
fleet 0 4 at 1180 1230 ships 2:101 plan 1 fuel 500
fleet 1 4 at 1180 1230 ships 3:1 fuel 500
fleet 0 5 at 1220 1230 ships 2:101 plan 1 fuel 500
fleet 1 5 at 1220 1230 ships 4:1 fuel 500
