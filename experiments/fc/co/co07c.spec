# CO-07c: as CO-07, but fleet 1 (2 Freighters, 1 Looker) holds 300 fuel and 100 Ir, to read how its fuel and cargo follow the deleted ships.
design 0 6 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
design 0 7 Scout, 1 Long Hump 6, Bat Scanner, empty = Looker
design 0 8 Scout, 1 Long Hump 6, empty, empty = Queued
fleet 0 0 at 1306 1060 planet 17 ships 7:1 fuel 50
fleet 0 1 at 1100 1230 ships 6:2,7:1 fuel 300 cargo 100 0 0 0
fleet 0 2 at 1100 1230 ships 6:2 fuel 500
queue 17 6:2:0:2,8:1:0:2
