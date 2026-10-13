# NS-2: a transport task whose waypoint names a packet at distances other than
# 40 ly, and in the pass after movement. Combat Lab base2400. Player 0 (human
# JOAT) runs every fleet; each fleet is one Medium Freighter (210 kT hold) with
# the task "load all ironium, load all boranium". Every packet is player 0's,
# class 0 (no decay), with 100 kT boranium and no ironium; every planet under
# test is player 0's with 50 kT ironium and no boranium on its surface.
tech 0 prop 26
research 0 0
design 0 15 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
#
# (1) after movement
# P1: packet 0 at Q = (1080,1180), deep space, written unmoved (as NS-1 A5's),
#     bound for planet 4 at packet warp 5. The fleet starts 20 ly south and
#     arrives at Q at warp 5 (25 ly), waypoint 1 naming the packet.
thing packet 0 0 1080 1180 4 5 0 100 0
fleet 0 1 at 1080 1200 ships 15:1 fuel 300 to 1080 1180 thing 0x2000 warp 5 task transport 1:0,1:0,-,-,-
# P1-F: packet 1 at (1000,1300), deep space, in flight (moved and bit15 set, as
#     NS-1 B1's), bound for planet 1 at packet warp 5. The fleet starts 20 ly
#     south at warp 9 (81 ly), waypoint 1 naming the packet.
thing packet 0 1 1000 1300 1 5 0 100 0 moved bit15
fleet 0 2 at 1000 1320 ships 15:1 fuel 300 to 1000 1300 thing 0x2001 warp 9 task transport 1:0,1:0,-,-,-
#
# (2) waypoint 0, before movement
# N: the fleet orbits player 0's planet 3 (1129,1265); waypoint 0 names packet
#    2, in flight 10 ly away at (1130,1255), bound for planet 6.
planet 3 owner 0 pop 500
planetset 3 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 3 none
thing packet 0 2 1130 1255 6 5 0 100 0 moved bit15
fleet 0 3 planet 3 at 1129 1265 ships 15:1 fuel 300 target thing 0x2002 task transport 1:0,1:0,-,-,-
# F: the fleet orbits player 0's planet 13 (1249,1354); waypoint 0 names packet
#    3, in flight 150 ly away at (1166,1229), bound for planet 1.
planet 13 owner 0 pop 500
planetset 13 mines=0 factories=0 defenses=0 excess=0 fe=50 bo=0 ge=0
queue 13 none
thing packet 0 3 1166 1229 1 5 0 100 0 moved bit15
fleet 0 4 planet 13 at 1249 1354 ships 15:1 fuel 300 target thing 0x2003 task transport 1:0,1:0,-,-,-
