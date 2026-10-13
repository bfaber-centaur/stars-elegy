# FS-1: what the second slot of 0x05b (and the fleet slot of 0x059) holds.
# A state edit on Combat Lab base2400 (combatlab build). Every scrapping fleet has
# a scrap task on waypoint 0. Designs are Scouts that differ only in name and slot.
relation 0 1 2
relation 1 0 2
design 0 2 Scout, 1 Long Hump 6, empty, empty = Scout2
design 0 5 Scout, 1 Long Hump 6, empty, empty = Scout5
design 0 7 Scout, 1 Long Hump 6, empty, empty = Scout7
design 0 9 Scout, 1 Long Hump 6, empty, empty = Scout9
design 0 15 Scout, 1 Long Hump 6, empty, empty = Scout15
design 0 11 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
design 1 0 Scout, 1 Long Hump 6, empty, empty = Scout0
design 1 3 Scout, 1 Long Hump 6, empty, empty = Scout3
design 1 4 Scout, 1 Long Hump 6, empty, empty = Scout4
design 1 11 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
# (a) P0 fleet 3, design 5, deep space, unfollowed
fleet 0 3 at 1100 1200 ships 5:1 fuel 100 task scrap
# (b) P1 fleet 0, design 0, deep space, unfollowed
fleet 1 0 at 1200 1240 ships 0:1 fuel 100 task scrap
# (c) P1 fleet 1, design 0, deep space, followed by P0 fleet 9 (waypoint 1 aimed at it)
fleet 1 1 at 1300 1250 ships 0:1 fuel 100 task scrap
fleet 0 9 at 1300 1150 ships 11:1 fuel 300 to 1300 1250 fleet 1 1 warp 4
# (d) P1 fleet 2, design 3, deep space, unfollowed
fleet 1 2 at 1060 1160 ships 3:1 fuel 100 task scrap
# (e) P1 fleet 4, design 3, deep space, followed by its own P1 fleet 5
fleet 1 4 at 1380 1180 ships 3:1 fuel 100 task scrap
fleet 1 5 at 1380 1080 ships 11:1 fuel 300 to 1380 1180 fleet 1 4 warp 4
# (f) P0 fleet 6, two designs (2 and 7), deep space, unfollowed
fleet 0 6 at 1200 1080 ships 7:1,2:1 fuel 100 task scrap
# (m) P0 fleet 8, design 15, deep space, unfollowed
fleet 0 8 at 1100 1350 ships 15:1 fuel 100 task scrap
# (p) P0 fleet 7, design 9, scraps at P0 planet 0 (no starbase)
planet 0 owner 0 pop 87 starbase none
planetset 0 env=50,50,50 excess=0 scanner=31
fleet 0 7 planet 0 at 1045 1291 ships 9:1 fuel 100 task scrap
# (q) P1 fleet 6, design 4, scraps at P1 planet 2 (no starbase)
planet 2 owner 1 pop 87 starbase none
planetset 2 env=50,50,50 excess=0 scanner=31
fleet 1 6 planet 2 at 1090 1295 ships 4:1 fuel 100 task scrap
