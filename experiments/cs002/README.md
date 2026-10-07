# CS-002: engine fuel tables

Question: is each engine's fuel factor `f(w)` in `data/components.json`
what the original game charges, for all 16 engines at warps 2–10?

`gen.py` (header) builds four FleetLab turns, one per four engines: per
engine and warp one fleet of Small Freighter clones carrying ironium, mass
`M = ceil(20000/w²)`, heading 150 ly east. With `w²·M ≥ 20000` each step of
`f` changes the charge by at least 1 mg (KERNEL.md "Fuel cost"), so the
charge identifies `f`. Paid fleets start with 20000 mg (over-capacity fuel
is kept in deep space); fleets at a free warp start with 1 mg so the
ram-scoop gain shows how many following warps are also free. Player 0 has
tech 26 everywhere (the game strips parts above the owner's tech).
`predictions.tsv` (end x, fuel, charge) was committed before the run, from
`engines-pred.json` (the private binary reading).

## Result (run 2026-10-07, one turn each)

144 of 144 fleets as predicted (`compare.py`, `results.tsv`): every engine's
factor at warps 2–10, every free warp and ram-scoop gain, every end
position. Three 2-ship fleets at warp 10 lost one ship (Radiating Hydro-Ram
Scoop, Trans-Galactic Fuel Scoop, Trans-Galactic Super Scoop, none rated
for warp 10); each had paid the full charge, then kept half its fuel and
cargo, truncated. No ship with a warp-10-rated engine was lost (10 ships).

Run: `python3 experiments/cs002/gen.py PRED.json OUTDIR`, then
`tools/fleetlab/fleetlab build` and `tools/fleetlab/oracle-turn` per
`turnN.spec`, then `compare.py RUN0 RUN1 RUN2 RUN3`. Raw files: private
apparatus repository, `evidence/cs/cs-002/`.
