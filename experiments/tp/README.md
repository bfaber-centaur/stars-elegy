# TP: Mystery Trader trades with computer players' planets

Tests `OBJECTS.md` "Computer players' planets" (BINARY-ONLY). Predictions
were written before the runs; `python3 gen.py --list` prints them.

Base game: AP-001 (`docs/PARITY.md`, "Computer players: Turindrone and
Automitron designs"), its host file after year 2401: human player 0, expert
Turindrone player 1, expert Automitron player 2. The raw game files are in
the private apparatus (`evidence/ai/ap/run001/y2401/raw/after/`).

```sh
tools/fleetlab/combatlab dump BASE/AP01.HST > base.dump
python3 experiments/tp/gen.py base.dump OUT
tools/fleetlab/combatlab build BASE/AP01.HST OUT/tp001.spec GAME/AP01.HST   # other base files copied to GAME
tools/fleetlab/pinned-turn GAME/AP01.HST GAME RUN 20000 AP01
```

`keepfleets` keeps the game's fleets; the six wormholes are copied as raw
records; three Traders are added (one per homeworld, each ending within
100 ly of that homeworld only), and the three homeworlds get 7,000 to
12,000 kT of surface minerals.

## Cases
| Case | Setup | Predicted | Rules out |
|---|---|---|---|
| TP-001-A | Turindrone (expert) homeworld 108, 7,000 kT on the surface, Trader 0 offering a part it lacks (bit 0) | Turindrone's part word 0000 -> 0001; planet 108 loses all its surface minerals (a scrapped Scout may add a few kT afterwards: each mineral at most 20) | no trade (only fleets trade) |
| TP-001-B | Automitron (expert) homeworld 80, 12,000 kT, tech 10,10,10,13,10,10 (sum 63), Trader 1 offering research | tech 12,11,11,13,11,11 (lowest field +1, six times); price 5,000 kT from germanium first: germanium 0, boranium down by the rest, ironium untouched | no trade; or ironium paid first |
| TP-001-C | human homeworld 39, 7,000 kT, Trader 2 offering a part | no trade: part word 0000, surface not taken | traded like a computer planet |
| TP-002-A | as TP-001-A, but Turindrone already owns bit 0 | one new bit among 1-12 (bit 12 gives only the bit); all surface minerals taken | nothing (offered part owned) |
| TP-002-B | as TP-001-B, but Automitron's tech is 25 in every field (sum 150) | nothing: tech unchanged, surface not reduced by 5,000 | six levels anyway |
| TP-002-C | as TP-001-C | no trade |  |
