# PQ-1b (PQ-1 with an armed Destroyer for player 0's Scout): the races count in a 3+-player battle summary (P vs Q). CB16P base;
# players 0-3 at tech 26 in every field. Players 0, 1 and 2 are mutual
# enemies; player 3 is neutral to all (no relation lines) and they to it.
# Plan 1 of players 0-2 attacks enemies; player 3's plans 0 (its starbase's)
# and 1 attack nobody.
#
# M: in orbit of player 3's homeworld 7 (1151,1318), which has an unarmed
#    Space Station and no defenses. P0: 1 Shield BB + 1 Plain DD; P1, P2:
#    2 Shield BB each. No player-3 fleet.
# C: the same three fleets in deep space (1020,1100); no fourth player.
relation 0 1 2
relation 0 2 2
relation 1 0 2
relation 1 2 2
relation 2 0 2
relation 2 1 2
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
tech 3 energy 26
tech 3 weapons 26
tech 3 prop 26
tech 3 con 26
tech 3 elec 26
tech 3 bio 26
design 0 0 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, 3 Laser = Shield BB
design 0 1 Destroyer, 1 Trans-Galactic Drive, 1 Laser = Plain DD
design 1 0 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, 3 Laser = Shield BB
design 2 0 Battleship, 4 Trans-Galactic Drive, empty, 8 Complete Phase Shield, 3 Laser = Shield BB
sbdesign 3 0 Space Station = Bare Station
planet 7 owner 3 pop 250 starbase 0
planetset 7 defenses=0
plan 0 1 5 1 0 1 = Enemies
plan 1 1 5 1 0 1 = Enemies
plan 2 1 5 1 0 1 = Enemies
plan 3 0 5 1 0 0 = Nobody
plan 3 1 5 1 0 0 = Nobody
# M
fleet 0 1 planet 7 at 1151 1318 ships 0:1,1:1 plan 1 fuel 2000
fleet 1 1 planet 7 at 1151 1318 ships 0:2 plan 1 fuel 2000
fleet 2 1 planet 7 at 1151 1318 ships 0:2 plan 1 fuel 2000
# C
fleet 0 2 at 1020 1100 ships 0:1,1:1 plan 1 fuel 2000
fleet 1 2 at 1020 1100 ships 0:2 plan 1 fuel 2000
fleet 2 2 at 1020 1100 ships 0:2 plan 1 fuel 2000
