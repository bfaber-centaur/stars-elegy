# OT-1: Mystery Trader encounter (turn order 6b) before the unload task
# after movement (6c). Player 0's 24 Medium Freighters (base design 3) carry
# exactly 5000 kT of ironium, arrive at its own planet 15 this year with
# "unload all ironium" on that waypoint. The Trader moves 64 ly onto planet
# 15 before fleets move. Random events stay off (CB base).
research 0 0
research 1 0
relation 0 1 1
relation 1 0 1
thing trader 0 1217 1064 1380 1064 8
planet 15 owner 0 pop 1000 starbase none
planetset 15 mines=0 factories=0 defenses=0 excess=0 fe=0 bo=0 ge=0 env=50,50,50
fleet 0 0 planet 17 at 1306 1060 ships 1:1
fleet 0 1 at 1251 1064 ships 3:24 fuel 2000 cargo 5000 0 0 0 to 1281 1064 planet 15 warp 6 task transport 2:0,-,-,-,-
fleet 1 0 planet 8 at 1169 1145 ships 1:1
