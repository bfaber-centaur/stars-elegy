# AO-1 C: Total Terraforming skip, case (c) of stars-elegy #192.
# Player 0: JOAT with TT, CE and LSP; player 1: JOAT with CE and LSP (control). CE and LSP (race points)
#   restrict no component. Both: energy 1, weapons 1,
#   propulsion 1, construction 10, electronics 10, biotech 0, researching biotech with exactly
#   the cost of biotech 1 stored (50 + 10*23 = 280). No production queues.
lrt 0 0x902
lrt 1 0x900
tech 0 energy 1
tech 0 weapons 1
tech 0 prop 1
tech 0 con 10
tech 0 elec 10
tech 0 bio 0
tech 1 energy 1
tech 1 weapons 1
tech 1 prop 1
tech 1 con 10
tech 1 elec 10
tech 1 bio 0
field 0 bio
field 1 bio
accum 0 bio 280
accum 1 bio 280
queue 17 none
queue 8 none
