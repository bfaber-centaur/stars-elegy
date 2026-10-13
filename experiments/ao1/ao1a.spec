# AO-1 A: within-level component order, cases (a) and (b) of stars-elegy #192.
# Player 0 (a): JOAT, no LRTs (no NAS), energy 4, electronics 16, biotech 7, others 0;
#   researching energy with exactly the cost of energy 5 stored (340 + 10*27 = 610).
# Player 1 (b): IS with ISB (and CE, for race points; CE restricts no component), energy 7, electronics 2, construction 3, others 0;
#   researching construction with exactly the cost of construction 4 stored (210 + 10*12 = 330).
# No production queues, so all resources go to research.
prt 1 4
lrt 0 0
lrt 1 0x108
tech 0 energy 4
tech 0 weapons 0
tech 0 prop 0
tech 0 con 0
tech 0 elec 16
tech 0 bio 7
tech 1 energy 7
tech 1 weapons 0
tech 1 prop 0
tech 1 con 3
tech 1 elec 2
tech 1 bio 0
field 0 energy
field 1 con
accum 0 energy 610
accum 1 con 330
queue 17 none
queue 8 none
