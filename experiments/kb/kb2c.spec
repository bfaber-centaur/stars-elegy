# KB-2C: terraforming with an immune axis. Random events off (CB base).
# Player 1: JOAT, gravity immune, temperature and radiation 45..55 (centre
# 50; an immune axis has centre, low and high all −1, written 255), with No Ram Scoop Engines, No Advanced Scanners, Low Starting
# Population and Bleeding Edge Technology (legal); every field at 3, so
# its reach is ±3 on each axis. Research tax 0.
#   10: environment 20/47/50, pop 5000, queue Terraform ×5: the immune
#       gravity axis is not terraformed and adds no capacity; capacity 3
#       (temperature 47 → 50), the order is cut to 3 with a message and
#       built: 20/50/50
#   11: environment 10/50/50, pop 5000, queue Terraform ×2: capacity 0
#       (only the immune axis is off-centre), the order is removed with a
#       message, nothing built
research 0 0
research 1 0
lrt 1 7552
hab 1 255,50,50,255,45,45,255,55,55
tech 1 energy 3
tech 1 weapons 3
tech 1 prop 3
tech 1 con 3
tech 1 elec 3
tech 1 bio 3
planet 10 owner 1 pop 5000 starbase none
planetset 10 mines=0 factories=0 defenses=0 excess=0 env=20,47,50 orig=20,47,50
queue 10 12:5:1
planet 11 owner 1 pop 5000 starbase none
planetset 11 mines=0 factories=0 defenses=0 excess=0 env=10,50,50 orig=10,50,50
queue 11 12:2:1
queue 8 none
queue 17 none
fleet 0 0 planet 17 at 1306 1060 ships 0:1
fleet 1 0 planet 8 at 1169 1145 ships 0:1
