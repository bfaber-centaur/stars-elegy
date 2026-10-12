# MR-1: a fleet aimed at another player's fleet F, which F's owner merges into Y
# the same year. This spec builds the prep year;
# after it, each owner's F and Y stand at the spot with the
# follower, and Y still has a waypoint ahead (warp 5 = 25 ly a year).
tech 0 prop 26
tech 1 prop 26
# Spot S1 (1240, 1100), follower W1 50 ly away, player 0's; F1 and Y1 are player 1's.
fleet 0 1 at 1240 1150 ships 3:1 fuel 300
fleet 1 1 at 1215 1100 ships 3:1 fuel 300 to 1240 1100 warp 5
fleet 1 2 at 1215 1100 ships 3:1 fuel 300 to 1290 1100 warp 5
# Spot S2 (1200, 1250), follower W2 50 ly away, player 1's; F2 and Y2 are player 0's.
fleet 1 3 at 1200 1200 ships 3:1 fuel 300
fleet 0 2 at 1175 1250 ships 3:1 fuel 300 to 1200 1250 warp 5
fleet 0 3 at 1175 1250 ships 3:1 fuel 300 to 1250 1250 warp 5
