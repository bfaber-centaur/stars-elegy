# PD-1: a planet's packet destination, packet speed and queued packet items when
# a starbase item completes, by mass driver before and after. Combat Lab base2400,
# player 0 (human JOAT) at tech 26. A packet setting is stored with the
# starbase, so only planets with a starbase before can have one; where set,
# the destination is planet 17 (the homeworld). Every build case has the
# starbase item at 99% first in the queue, and plenty of resources and minerals. Items: 14 = ironium packet, 6 = auto packets,
# 16 + n (kind 2) = starbase design n.
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
research 0 0
sbdesign 0 0 Orbital Fort, empty, empty, empty, empty, empty = Fort
sbdesign 0 1 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Catcher 7
sbdesign 0 2 Space Station, 1 Mass Driver 5, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, 1 Mass Driver 5, 8 Mole-skin Shield = Twin 5
# (a0) no starbase -> Fort (no driver); no packet setting can be stored without a
# starbase; queue Fort, ironium packet x1, auto packets x1
planet 2 owner 0 pop 20000 starbase none
planetset 2 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 2 16:1:99:2,14:1:1,6:1:1
# (a) Fort -> Fort (no driver before or after); speed 6; same queue
planet 3 owner 0 pop 20000 starbase 0
planetset 3 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,6
queue 3 16:1:99:2,14:1:1,6:1:1
# (b) Catcher 7 (Mass Driver 7) -> Fort (none); speed 6; queue Fort, ironium packet x1
planet 4 owner 0 pop 20000 starbase 1
planetset 4 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,6
queue 4 16:1:99:2,14:1:1
# (c0) no starbase -> Catcher 7 (one Mass Driver 7); no setting before
planet 5 owner 0 pop 20000 starbase none
planetset 5 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31
queue 5 17:1:99:2
# (c) Fort (no driver) -> Catcher 7 (one Mass Driver 7); speed 6
planet 6 owner 0 pop 20000 starbase 0
planetset 6 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,6
queue 6 17:1:99:2
# (d) Catcher 7 -> Twin 5 (two Mass Driver 5s); speed 6
planet 9 owner 0 pop 20000 starbase 1
planetset 9 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,6
queue 9 18:1:99:2
# (e) Fort -> Twin 5 (two Mass Driver 5s); speed 9 (tests Dw + t = 6)
planet 10 owner 0 pop 20000 starbase 0
planetset 10 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,9
queue 10 18:1:99:2
# (k) control: Catcher 7, nothing built; speed 6
planet 11 owner 0 pop 20000 starbase 1
planetset 11 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,6
queue 11 none
