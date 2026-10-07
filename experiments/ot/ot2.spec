# OT-2: Mystery Trader encounter (6b) after battles (6). Player 0's 24
# Medium Freighters with exactly 5000 kT of ironium sit, stationary, where
# the Trader ends its move (1084,1210, as in OB-004); three of player 1's
# Destroyers (base design 4) sit there too. Mutual enemies.
research 0 0
research 1 0
relation 0 1 2
relation 1 0 2
plan 1 0 4 1 0 1 = Enemies
thing trader 0 1020 1210 1380 1210 8
fleet 0 0 planet 17 at 1306 1060 ships 1:1
fleet 0 1 at 1084 1210 ships 3:24 fuel 2000 cargo 5000 0 0 0
fleet 1 0 planet 8 at 1169 1145 ships 1:1
fleet 1 1 at 1084 1210 ships 4:3 fuel 1500 plan 0
