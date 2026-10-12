# FB-1: a queue item whose design has a part the owner may not build.
# Combat Lab base2400, player 0 (human JOAT) at tech 26. The designs are
# written into the state directly; the client would not let a JOAT design
# them (Mini Gun is Inner Strength only, Settler's Delight is Hyper
# Expansion only, Multi Function Pod is a Mystery Trader part the player
# does not own, Mass Driver 5 is Packet Physics only). Items: N:COUNT:PCT:2
# = ship design N, 16 + n (kind 2) = starbase design n, 8 (kind 1) = mines.
# Each ship case has the ship item first, then mines; the mines built
# measure the resources left. Ship planets have an empty Space Station (a
# dock, as the client requires). Population is in units of 100 colonists.
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
research 0 0
design 0 0 Scout, 1 Long Hump 6, empty, 1 Mini Gun = Gun Scout
design 0 1 Scout, 1 Settler's Delight, empty, empty = HE Scout
design 0 2 Scout, 1 Long Hump 6, empty, empty = Plain Scout
design 0 3 Scout, 1 Long Hump 6, empty, 1 Multi Function Pod = MT Scout
sbdesign 0 0 Orbital Fort, empty, empty, empty, empty, empty = Fort
sbdesign 0 1 Orbital Fort, 1 Mass Driver 5, empty, empty, empty, empty = Fort MD5
sbdesign 0 2 Space Station, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty, empty = Station
# (a) Gun Scout (IS-only weapon) x1 at 0%, then mines
planet 2 owner 0 pop 2000 starbase 2
planetset 2 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 2 0:1:0:2,8:150:1
# (a2) HE Scout (HE-only engine) x1 at 0%, then mines
planet 3 owner 0 pop 2000 starbase 2
planetset 3 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 3 1:1:0:2,8:150:1
# (a0) control: mines only
planet 4 owner 0 pop 2000 starbase 2
planetset 4 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 4 8:150:1
# (a1) control: Plain Scout (all parts allowed) x1 at 0%, then mines
planet 5 owner 0 pop 2000 starbase 2
planetset 5 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 5 2:1:0:2,8:150:1
# (b) MT Scout (unowned Mystery Trader part) x1 at 0%, then mines
planet 6 owner 0 pop 2000 starbase 2
planetset 6 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 6 3:1:0:2,8:150:1
# (c) Fort -> Fort MD5 (PP-only) at 0%, nothing after
planet 7 owner 0 pop 2000 starbase 0
planetset 7 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 7 17:1:0:2
# (c0) control: Fort, nothing queued
planet 9 owner 0 pop 2000 starbase 0
planetset 9 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 9 none
# (d) Gun Scout x3 at 0%, then mines, with resources for 1 ship and part of a second
planet 10 owner 0 pop 60 starbase 2
planetset 10 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 10 0:3:0:2,8:150:1
