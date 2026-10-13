# CB-B: battle-summary assumptions B1-B3 (lane D). CB16P base; players 0, 1
# and 2 at tech 26 in every field. Players 0 and 1 are mutual enemies;
# player 2 is neutral to both (no relation lines). Each case is its own
# battle at its own location. Plan 1 of players 0 and 1 attacks enemies,
# any target; player 2's plan 1 attacks nobody.
#
# B1: duels in deep space (texts 0x091-0x095)
#   B1-S (1020,1100): P0 Shield BB (4000 shields, 3 Lasers) vs P1 Laser DD
#     (1 Laser, armor 300): P1 can only reach P0's shields.
#   B1-Z (1040,1100): P0 Jam BB (no shields, jammers 95, 3 Lasers) vs P1
#     Alpha DD (1 Alpha Torpedo): P1's misses write 0-hit records.
#   B1-M (1060,1100): P0 Shield Jam BB (800 shields, jammers 95, 3 Lasers) vs
#     P1 Omega DD (1 Omega Torpedo): misses do shield damage only.
# B2b: P0 one Big BB (12 Heavy Blasters) vs P1 HB DDs and HB CRs (two designs):
#   B2b-1 (1080,1100): 4 + 4; B2b-2 (1100,1100): 3 + 3.
# X (0x113/0x114) (1120,1100): P0 Super BB (4000 shields, 12 Heavy Blasters)
#   vs P1 2 Laser Frigates + 2 Laser DDs.
# B3: who counts as a player
#   B3-SB: P2's homeworld 25 with an unarmed station, P0 HB DD and P1 Scout in
#     orbit, no P2 fleet.
#   B3-BY (1060,1080): P0 HB DD, P1 Scout, P2 Scout (plan: nobody).
#   B3-C  (1080,1080): P0 HB DD, P1 Scout.
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
tech 2 energy 26
tech 2 weapons 26
tech 2 prop 26
tech 2 con 26
tech 2 elec 26
tech 2 bio 26
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, 3 Laser = Shield BB
design 0 1 Battleship, 4 Trans-Galactic Drive, empty, empty, 3 Laser, empty, empty, empty, empty, empty, 3 Jammer 50, 3 Jammer 50 = Jam BB
design 0 2 Battleship, 4 Trans-Galactic Drive, empty, 8 Bear Neutrino Barrier, 3 Laser, empty, empty, empty, empty, empty, 3 Jammer 50, 3 Jammer 50 = Shield Jam BB
design 0 3 Battleship, 4 Trans-Galactic Drive, empty, empty, 6 Heavy Blaster, 6 Heavy Blaster = Big BB
design 0 4 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, 6 Heavy Blaster, 6 Heavy Blaster = Super BB
design 0 5 Destroyer, 1 Trans-Galactic Drive, 1 Heavy Blaster, 1 Heavy Blaster = HB DD
design 1 0 Destroyer, 1 Trans-Galactic Drive, 1 Laser, empty, empty, 2 Tritanium = Laser DD
design 1 1 Destroyer, 1 Trans-Galactic Drive, 1 Alpha Torpedo = Alpha DD
design 1 2 Destroyer, 1 Trans-Galactic Drive, 1 Omega Torpedo = Omega DD
design 1 3 Destroyer, 1 Trans-Galactic Drive, 1 Heavy Blaster, 1 Heavy Blaster, empty, 2 Tritanium = HB DD
design 1 4 Cruiser, 2 Trans-Galactic Drive, empty, empty, 2 Heavy Blaster, 2 Heavy Blaster, empty, 2 Tritanium = HB CR
design 1 5 Frigate, 1 Trans-Galactic Drive, empty, 2 Laser = Laser Frig
design 1 6 Destroyer, 1 Trans-Galactic Drive, 1 Laser = Plain DD
design 1 7 Scout, 1 Trans-Galactic Drive = Scout
design 2 0 Scout, 1 Trans-Galactic Drive = Scout
sbdesign 2 0 Space Station = Bare Station
planet 25 owner 2 pop 500 starbase 0
plan 0 1 5 1 0 1 = Enemies
plan 1 1 5 1 0 1 = Enemies
plan 2 1 5 1 0 0 = Nobody
# B1-S
fleet 0 1 at 1020 1100 ships 0:1 plan 1 fuel 2000
fleet 1 1 at 1020 1100 ships 0:1 plan 1 fuel 300
# B1-Z
fleet 0 2 at 1040 1100 ships 1:1 plan 1 fuel 2000
fleet 1 2 at 1040 1100 ships 1:1 plan 1 fuel 300
# B1-M
fleet 0 3 at 1060 1100 ships 2:1 plan 1 fuel 2000
fleet 1 3 at 1060 1100 ships 2:1 plan 1 fuel 300
# B2b-1
fleet 0 4 at 1080 1100 ships 3:1 plan 1 fuel 2000
fleet 1 4 at 1080 1100 ships 3:4 plan 1 fuel 300
fleet 1 5 at 1080 1100 ships 4:4 plan 1 fuel 600
# B2b-2
fleet 0 5 at 1100 1100 ships 3:1 plan 1 fuel 2000
fleet 1 6 at 1100 1100 ships 3:3 plan 1 fuel 300
fleet 1 7 at 1100 1100 ships 4:3 plan 1 fuel 600
# X
fleet 0 6 at 1120 1100 ships 4:1 plan 1 fuel 2000
fleet 1 8 at 1120 1100 ships 5:2 plan 1 fuel 300
fleet 1 9 at 1120 1100 ships 6:2 plan 1 fuel 300
# B3-SB: in orbit of player 2's homeworld 25
fleet 0 7 planet 25 at 1326 1247 ships 5:1 plan 1 fuel 300
fleet 1 10 planet 25 at 1326 1247 ships 7:1 plan 1 fuel 100
# B3-BY
fleet 0 8 at 1060 1080 ships 5:1 plan 1 fuel 300
fleet 1 11 at 1060 1080 ships 7:1 plan 1 fuel 100
fleet 2 1 at 1060 1080 ships 0:1 plan 1 fuel 100
# B3-C
fleet 0 9 at 1080 1080 ships 5:1 plan 1 fuel 300
fleet 1 12 at 1080 1080 ships 7:1 plan 1 fuel 100
