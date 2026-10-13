# LW (lane D's late-tech weapons). Combat Lab base2400; players 0 and 1 at
# tech 26 in every field, mutual enemies. Every case is its own deep-space
# battle on y = 1230. Player 1's targets hold (plan 1: primary fuel
# transports, never fires); its approachers (plan 2) attack. Except in S3,
# every player-1 target carries 4000 shields a ship, so beam and gatling
# damage is read exactly as shield damage.
#   G1 (1020): GNC BB (primary armed, secondary any) vs armed A + unarmed F
#   G2 (1060): Big Mutha Cannon BB vs held T1 + approaching armed T2
#   G3 (1100): Mini Gun BB, as G2
#   S1 (1140): Phased Sapper BB + Syncro Sapper BB vs 8 Complete Phase BBs
#   S2 (1180): Syncro Sapper BB vs L (300 shields) + M (2 Complete Phase BBs)
#   S3 (1220): Pulsed Sapper BB vs an armed Laser DD + an unarmed BB
#   B  (1260): one BB per late beam (8 fleets) vs 20 Shield BBs
#   N  (1300): Battle Nexus + Alpha Torpedo BB vs a Shield BB
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
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Gatling Neutrino Cannon, empty, empty, empty, empty, 6 Neutronium = GNC BB
design 0 1 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Big Mutha Cannon, empty, empty, empty, empty, 6 Neutronium = BMC BB
design 0 2 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Mini Gun, empty, empty, empty, empty, 6 Neutronium = MiniGun BB
design 0 3 Battleship, 4 Trans-Galactic Drive, empty, empty, 2 Phased Sapper, empty, empty, empty, empty, 6 Neutronium = Phased BB
design 0 4 Battleship, 4 Trans-Galactic Drive, empty, empty, 2 Syncro Sapper, empty, empty, empty, empty, 6 Neutronium = Syncro BB
design 0 5 Battleship, 4 Trans-Galactic Drive, empty, empty, 2 Pulsed Sapper, empty, empty, empty, empty, 6 Neutronium = Pulsed BB
design 0 6 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Myopic Disruptor, empty, empty, empty, empty, 6 Neutronium = MyoD BB
design 0 7 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Disruptor, empty, empty, empty, empty, 6 Neutronium = Disr BB
design 0 8 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Mega Disruptor, empty, empty, empty, empty, 6 Neutronium = MegaD BB
design 0 9 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Mini Blaster, empty, empty, empty, empty, 6 Neutronium = MiniB BB
design 0 10 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Mark IV Blaster, empty, empty, empty, empty, 6 Neutronium = Mk4 BB
design 0 11 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Heavy Blaster, empty, empty, empty, empty, 6 Neutronium = HvyB BB
design 0 12 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Streaming Pulverizer, empty, empty, empty, empty, 6 Neutronium = StrP BB
design 0 13 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Anti-Matter Pulverizer, empty, empty, empty, empty, 6 Neutronium = AmP BB
design 0 14 Battleship, 4 Trans-Galactic Drive, empty, empty, 1 Alpha Torpedo, empty, empty, empty, empty, 6 Neutronium, 1 Battle Nexus = Nexus BB
design 1 0 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, empty, empty, empty, empty, empty, 6 Neutronium = Shield BB
design 1 1 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, 1 Laser, empty, empty, empty, empty, 6 Neutronium = Armed Shield BB
design 1 2 Battleship, 4 Trans-Galactic Drive, empty, empty, empty, empty, empty, empty, empty, 6 Neutronium = Bare BB
design 1 3 Battleship, 4 Trans-Galactic Drive, empty, 3 Bear Neutrino Barrier, empty, empty, empty, empty, empty, 6 Neutronium = Thin BB
design 1 4 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Tritanium = Laser DD
plan 0 1 5 1 0 1 = Max Any
plan 0 2 5 3 1 1 = Armed First
plan 1 1 4 6 0 1 = Hold
plan 1 2 5 1 0 1 = Attack
queue 17 none
queue 8 none
# G1
fleet 0 1 at 1020 1230 ships 0:1 plan 2 fuel 2000
fleet 1 1 at 1020 1230 ships 1:1 plan 1 fuel 2000
fleet 1 2 at 1020 1230 ships 0:1 plan 1 fuel 2000
# G2
fleet 0 2 at 1060 1230 ships 1:1 plan 1 fuel 2000
fleet 1 3 at 1060 1230 ships 0:1 plan 1 fuel 2000
fleet 1 4 at 1060 1230 ships 1:1 plan 2 fuel 2000
# G3
fleet 0 3 at 1100 1230 ships 2:1 plan 1 fuel 2000
fleet 1 5 at 1100 1230 ships 0:1 plan 1 fuel 2000
fleet 1 6 at 1100 1230 ships 1:1 plan 2 fuel 2000
# S1
fleet 0 4 at 1140 1230 ships 3:1 plan 1 fuel 2000
fleet 0 5 at 1140 1230 ships 4:1 plan 1 fuel 2000
fleet 1 7 at 1140 1230 ships 0:8 plan 1 fuel 2000
# S2
fleet 0 6 at 1180 1230 ships 4:1 plan 1 fuel 2000
fleet 1 8 at 1180 1230 ships 3:1 plan 1 fuel 2000
fleet 1 9 at 1180 1230 ships 0:2 plan 1 fuel 2000
# S3
fleet 0 7 at 1220 1230 ships 5:1 plan 1 fuel 2000
fleet 1 10 at 1220 1230 ships 4:1 plan 2 fuel 300
fleet 1 11 at 1220 1230 ships 2:1 plan 1 fuel 2000
# B
fleet 0 8 at 1260 1230 ships 6:1 plan 1 fuel 2000
fleet 0 9 at 1260 1230 ships 7:1 plan 1 fuel 2000
fleet 0 10 at 1260 1230 ships 8:1 plan 1 fuel 2000
fleet 0 11 at 1260 1230 ships 9:1 plan 1 fuel 2000
fleet 0 12 at 1260 1230 ships 10:1 plan 1 fuel 2000
fleet 0 13 at 1260 1230 ships 11:1 plan 1 fuel 2000
fleet 0 14 at 1260 1230 ships 12:1 plan 1 fuel 2000
fleet 0 15 at 1260 1230 ships 13:1 plan 1 fuel 2000
fleet 1 12 at 1260 1230 ships 0:20 plan 1 fuel 2000
# N
fleet 0 16 at 1300 1230 ships 14:1 plan 1 fuel 2000
fleet 1 13 at 1300 1230 ships 0:1 plan 1 fuel 2000
