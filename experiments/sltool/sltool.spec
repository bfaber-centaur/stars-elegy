# Ship launch tooling check: production queues, route destinations, a player near 512 fleets.
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Station
sbdesign 0 1 Orbital Fort, empty, 12 Colloidal Phaser, empty, empty, empty = Fort
tech 0 energy 26
tech 0 weapons 26
tech 0 prop 26
tech 0 con 26
tech 0 elec 26
tech 0 bio 26
fleet 0 0 at 1306 1060 planet 17 ships 0:1 fuel 50
queue 17 1:2:2,17:1:2
planetset 17 route=raw:0013 factories=100
fleets 1 0-509 at 1169 1145 planet 8 ships 0:1 fuel 50
queue 8 0:3:2
planetset 8 route=5
