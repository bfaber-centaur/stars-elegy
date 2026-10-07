# FM-004: decomp movement predictions

Question: do the fuel and movement rules that the private stars-decomp
reading of fleet movement derives from the binary hold for cases FM-001..003
did not cover?

Same method as FM-001..003: `gen.py` writes `fm004.spec`; FleetLab builds
the PG001 2407 `.HST`; one turn (2407 → 2408) on the oracle. Designs 6–9
are FleetLab clones: Scout with Settler's Delight (6), Fuel Mizer (7),
Radiating Hydro-Ram Scoop (8), and a Small Freighter with Long Hump 6 (9).
The race is unchanged (SS, no LRT), so 6–8 use engines the race could not
normally build.

Groups (55 fleets):

| Group | Tests |
|---|---|
| LR | distance covered when fuel runs out, where the decomp's range formula and FM-001..003's `floor(fuel·20000/M)` differ by 1 ly |
| WD | warp after running dry for engines that are free above warp 1, a 0-fuel fleet, and a 2-ly leg |
| RS | fuel gained at free warps 1–7 (Fuel Mizer, Settler's Delight, Hydro-Ram), several ships, mixed fleet, tank cap, arrival year |
| MS | mixed-design fleets where rounding per ship stack differs from rounding the total |
| CA | which ship stack carries the cargo in a two-freighter fleet |
| TU | fuel top-up on a leg the fleet could afford at departure |
| DK | refuelling at the homeworld starbase (planet 7), over-capacity fuel, a planet without starbase |
| OR | a deep-space waypoint exactly on a planet |

`predictions.tsv` has two competing predictions per fleet, committed before
the turn was generated:

- `pred`: the decomp model (stars-decomp `tools/fleetcalc.py`, branch
  `claude/project-thread-yiboso` at 91243d1; computed by a private script
  kept with the raw evidence) as `pos; fuel; waypoint-1 warp; orbited
  planet (-1 none); waypoint count; events; notes`. Events: 78 arrived,
  139 out of fuel with the new warp, 243 fuel produced.
- `fitted`: the FM-001..003 description (`experiments/fmcheck.py`), which
  does not model starbase refuelling or fuel gain above warp 1.
