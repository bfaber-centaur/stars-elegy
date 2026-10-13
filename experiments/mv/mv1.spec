# MV-1: does an owned planet with no scanner know an enemy minefield centred on it?
# A state edit on Combat Lab base2400 (combatlab build). Player 0 (viewer) keeps
# the base's tech 3 except electronics 0, has no fleets, and has a planetary
# scanner only at planet 13 (control S). Player 1 owns every minefield; each starts known
# only to player 1 (known mask 2). No player 1 fleet is near a field except in L.
relation 0 1 2
relation 1 0 2
tech 1 energy 26
tech 1 weapons 26
tech 1 prop 26
tech 1 con 26
tech 1 elec 26
tech 1 bio 26
tech 0 elec 0
research 0 0
research 1 0
design 1 0 Mini Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, empty, empty = Layer
plan 1 0 4 1 0 0 = Nobody
# player 0's homeworld keeps no planetary scanner
planet 17 scanner none
# (Z) field centred exactly on player 0's planet 18 (d2 0); no laying fleet
planet 18 owner 0 pop 1000 starbase none scanner none
planetset 18 mines=0 factories=0 defenses=0 env=50,50,50
thing minefield 1 0 1324 1192 400 kind std known 2
# (D1) field centred 1 ly east of player 0's planet 7 (d2 1)
planet 7 owner 0 pop 1000 starbase none scanner none
planetset 7 mines=0 factories=0 defenses=0 env=50,50,50
thing minefield 1 1 1167 1382 400 kind std known 2
# (D1280) planet 6 inside the field, off centre by (32,16) (d2 1280), as in RG-002/RG-003
planet 6 owner 0 pop 1000 starbase none scanner none
planetset 6 mines=0 factories=0 defenses=0 env=50,50,50
thing minefield 1 2 1198 1033 1600 kind std known 2
# (N) control: field in deep space, no player 0 planet inside
thing minefield 1 3 1200 1250 400 kind std known 2
# (L) as RG-004: a player 1 layer in orbit at player 0's planet 1 lays a new field this year
planet 1 owner 0 pop 1000 starbase none scanner none
planetset 1 mines=0 factories=0 defenses=0 env=50,50,50
fleet 1 0 planet 1 at 1071 1087 ships 0:1 plan 0 fuel 50 task lay 0
# (S) control: field 10 ly from player 0's planet 13, which has a planetary scanner
# (electronics 0); no fleet
planet 13 owner 0 pop 1000 starbase none
planetset 13 mines=0 factories=0 defenses=0 env=50,50,50 scanner=0
thing minefield 1 4 1259 1354 25 kind std known 2
