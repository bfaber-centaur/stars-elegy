# KB1-C: mining's random +1 and its draw order, by replaying the random
# stream. Random events on (option byte 0x40, set by run-kb.sh), year
# 2400. Five non-homeworld planets with 10 mines each and concentrations
# chosen so that every mineral's output has a non-zero remainder (15 draws),
# plus the two homeworlds' germanium (2 draws). No queues, no fleets in
# motion, no battles.
#   P0: 0 conc 33/57/91, 1 conc 12/45/78, 2 conc 66/24/5
#   P1: 4 conc 27/88/13, 5 conc 41/9/62
research 0 0
research 1 0
planet 0 owner 0 pop 1000 starbase none
planetset 0 mines=10 factories=0 defenses=0 excess=0 conc=33,57,91 env=50,50,50
planet 1 owner 0 pop 1000 starbase none
planetset 1 mines=10 factories=0 defenses=0 excess=0 conc=12,45,78 env=50,50,50
planet 2 owner 0 pop 1000 starbase none
planetset 2 mines=10 factories=0 defenses=0 excess=0 conc=66,24,5 env=50,50,50
planet 4 owner 1 pop 1000 starbase none
planetset 4 mines=10 factories=0 defenses=0 excess=0 conc=27,88,13 env=50,50,50
planet 5 owner 1 pop 1000 starbase none
planetset 5 mines=10 factories=0 defenses=0 excess=0 conc=41,9,62 env=50,50,50
queue 0 none
queue 1 none
queue 2 none
queue 4 none
queue 5 none
queue 8 none
queue 17 none
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 1 0 planet 8 at 1169 1145 ships 0:1
