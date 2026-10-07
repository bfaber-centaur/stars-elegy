# CS-003: the components table's BINARY-ONLY columns

Question: are the columns that CS-001 and CS-002 could not observe (the
`binary_only` lists in `data/components.json`) what the original game does?

Every prediction is the value already in `data/components.json` (read from
the original program), pushed through the public rule that uses it:
KERNEL.md (warp-10 losses, fuel transports, remote mining), OBJECTS.md
(sweeping, laying, decay), TAKEOVER.md (bombing, colonizing), COMBAT.md
(speed code, jammer, torpedo damage) and SCANNING.md (cloak %). Each case
also names the value a different table entry would give.

`gen.py` writes one Combat Lab spec per run and `predictions.tsv` (77
cases); both were committed before any CS-003 run.

| Run | Cases | Columns |
|---|---|---|
| CS-003-D | designer readouts of 7 designs | Enigma Pulsar `cloak_points`; Alien Miner `battle_speed_half_steps` (with and without an Enigma Pulsar); Mega Poly Shell and Multi Contained Munition scanner ranges |
| CS-003-W | 6 fleets of 10 Small Freighters per engine at warp 10; 4 stationary fleets with no fuel | engine `warp10_rated`; hull `fuel_transport` |
| CS-003-S | one Scout per plain beam at the centre of an enemy field with no planets; two mine layers | beam `kind` and `mines_swept`; hull `mine_layer_multiplier` |
| CS-003-B | one bomber per target planet (environment 50/50/50, no defenses); colony ships and miners at unowned planets | bomb zero `installations` / `min_kill`, Retro Bomb values; Multi Contained Munition bomb values; Orbital Construction Module `colonizes`; Orbital Adjuster `mining_rate` |
| CS-003-C | a Cruiser with 6 torpedoes or missiles against 3 unarmed, unshielded Battleships; a range-0 beam against an unarmed, unshielded Orbital Fort | torpedo `kind`; range-0 beam `kind` |

Engine `battle_warp` (all 16) and the single Enigma Pulsar's half step are
already observed by CB-000 (`experiments/cb000`): every engine's scout
showed the moves its battle warp predicts.

Run: `python3 experiments/cs003/gen.py OUT`, then per run
`tools/fleetlab/combatlab build CB.HST OUT/cs003X.spec start.HST` and
`tools/fleetlab/pinned-turn start.HST BASEDIR RUN`. Raw files: private
apparatus repository, `evidence/cs/cs-003/`.

`experiments/cs003/check.py RUN_W RUN_S RUN_B RUN_C RUN_C2 designer.tsv`
compares every case (`results.tsv`); `designer.tsv` is typed from the
CS-003-D screenshots. `apply.py` then clears the observed columns from
`data/components.json`.

CS-003-C2 was added after CS-003-C (its predictions committed before it
ran): with two torpedoes per salvo, 1 hit of `2d` looks like 2 hits of
`d`, and the Alpha Torpedo's 5 dp was below the Hulk stack's damage
resolution. C2 fires one torpedo per round at a single armed target.

## Result (run 2026-10-07, pinned generation, cycles 20000)

80 of 80 cases as predicted (77 directly; Alpha Torpedo, Juggernaut and
Doomsday Missile not told apart by CS-003-C and confirmed by CS-003-C2).
All 63 rows are now CONFIRMED; `data/components.json` has no BINARY-ONLY
row. Details and limits: `docs/PARITY.md`, "The remaining BINARY-ONLY
columns (CS-003)".

| Run | Cases | Result |
|---|---:|---|
| CS-003-D designer | 7 | 7 match |
| CS-003-W warp 10, fuel transports | 20 | 20 match (non-rated engines lost 58 of 660 ships, rated 0 of 300) |
| CS-003-S sweeping, laying | 19 | 19 match |
| CS-003-B bombing, colonizing, mining | 16 | 16 match |
| CS-003-C torpedoes, range-0 beams | 15 | 12 match, 3 not discriminated |
| CS-003-C2 single torpedoes | 3 | 3 match |
