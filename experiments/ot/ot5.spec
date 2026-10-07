# OT-5: Inner Strength colonists breeding in transit (turn order 3b) before
# production and growth (4). Player 0 is IS (growth 15%). Planets 15, 19
# and 21 are player 0's with identical environment 50/50/50 and no
# installations or queue: 15 holds 1000 units with fleet A (10 Medium
# Freighters, hold full with 2100 kT of colonists) in orbit; 19 holds 1157
# units (the control: 1000 + the predicted overflow); 21 holds 1000 units
# (the control for "after growth"). Fleet B (1 freighter, 200 kT) is in
# deep space; fleet C (1 freighter, full) orbits player 1's planet 4.
research 0 0
research 1 0
prt 0 4
relation 0 1 0
relation 1 0 0
planet 15 owner 0 pop 1000 starbase none
planetset 15 mines=0 factories=0 defenses=0 excess=0 env=50,50,50
planet 19 owner 0 pop 1157 starbase none
planetset 19 mines=0 factories=0 defenses=0 excess=0 env=50,50,50
planet 21 owner 0 pop 1000 starbase none
planetset 21 mines=0 factories=0 defenses=0 excess=0 env=50,50,50
planet 4 owner 1 pop 1000 starbase none
planetset 4 mines=0 factories=0 defenses=0 excess=0 env=50,50,50
fleet 0 0 planet 17 at 1306 1060 ships 1:1
fleet 0 1 planet 15 at 1281 1064 ships 3:10 fuel 500 cargo 0 0 0 2100
fleet 0 2 at 1200 1000 ships 3:1 fuel 100 cargo 0 0 0 200
fleet 0 3 planet 4 at 1143 1103 ships 3:1 fuel 100 cargo 0 0 0 210
fleet 1 0 planet 8 at 1169 1145 ships 1:1
