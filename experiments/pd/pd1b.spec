# PD-1b (PD-1's two-driver cases rebuilt without Mass Driver 5, which is
# Packet Physics only): a planet's packet destination, packet speed and queued packet items when
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
sbdesign 0 2 Space Station, 1 Mass Driver 7, empty, empty, empty, empty, empty, empty, empty, empty, empty, 1 Mass Driver 7, empty = Twin 7
sbdesign 0 3 Orbital Fort, 1 Ultra Driver 10, empty, empty, empty, empty = Ultra 10
# (d) Catcher 7 (one Mass Driver 7) -> Twin 7 (two Mass Driver 7s); speed 6
planet 9 owner 0 pop 20000 starbase 1
planetset 9 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,6
queue 9 18:1:99:2
# (d2) Catcher 7 -> Ultra 10 (one Ultra Driver 10); speed 9
planet 3 owner 0 pop 20000 starbase 1
planetset 3 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,9
queue 3 19:1:99:2
# (e) Fort (no driver) -> Twin 7; speed 9 (Dw + t = 8)
planet 10 owner 0 pop 20000 starbase 0
planetset 10 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,9
queue 10 18:1:99:2
# (k) control: Catcher 7, nothing built; speed 6
planet 11 owner 0 pop 20000 starbase 1
planetset 11 mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31 packet=17,6
queue 11 none
