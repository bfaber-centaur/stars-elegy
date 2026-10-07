# CO-08: as CO-07; the design "Queued" (slot 8) is used only by the homeworld queue, so the client allows Edit. It gets a Bat Scanner.
design 0 6 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
design 0 7 Scout, 1 Long Hump 6, Bat Scanner, empty = Looker
design 0 8 Scout, 1 Long Hump 6, empty, empty = Queued
fleet 0 0 at 1306 1060 planet 17 ships 7:1 fuel 50
fleet 0 1 at 1100 1230 ships 6:2,7:1 fuel 500
fleet 0 2 at 1100 1230 ships 6:2 fuel 500
queue 17 6:2:0:2,8:1:0:2
