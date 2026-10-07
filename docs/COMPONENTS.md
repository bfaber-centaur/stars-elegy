# Components: ship parts, hulls, starbases and planetary items

Behavioral reference for every J-RC3 component: what it costs, who may build
it, its mass and tech requirement, and the values it contributes. The data
is in `data/components.json`; this file explains its columns and the rules
that turn base values into what a given race pays and sees.

Every value was read from the original program (private `stars-decomp`)
and then compared with the running original game (corpus `CS-`, raw
evidence in the private apparatus repository under `evidence/cs/`). No
third-party data table was used to build it. StarsAPI's item table was
compared privately afterwards and agrees on every item (name, tech, mass,
cost, category values, hull slots).

How a design combines parts (fleet cloak, jammer, computer, capacitor and
deflector percentages, initiative, battle speed) is in `SCANNING.md` and
`COMBAT.md`; fuel use in `KERNEL.md`. Those files refer to this one for
per-part values.

## Status

Each row of `data/components.json` has a `status`:

- **CONFIRMED**: every column of the row was observed in the original game.
- **BINARY-ONLY**: the columns named in the row's `binary_only` list were
  read from the original program only. All other columns of the row were
  observed.

| Category | Rows | CONFIRMED | Rows with a BINARY-ONLY column |
|---|---:|---:|---:|
| hull | 32 | 28 | 4 (`fuel_transport`, `mine_layer_multiplier`) |
| starbase_hull | 5 | 5 | 0 |
| engine | 16 | 0 | 16 (`warp10_rated`, `battle_warp`; Enigma Pulsar also `cloak_points`, `battle_speed_half_steps`) |
| scanner | 16 | 16 | 0 |
| shield | 10 | 10 | 0 |
| armor | 12 | 11 | 1 (Mega Poly Shell scanner) |
| beam | 24 | 7 | 17 (`kind`, `mines_swept` of plain beams; Multi Contained Munition scanner and bomb values) |
| torpedo | 12 | 0 | 12 (`kind`: torpedo or capital missile) |
| bomb | 15 | 5 | 10 (zero `min_kill` / `installations`, Retro Bomb values) |
| mining_robot | 8 | 6 | 2 |
| mine_layer | 10 | 10 | 0 |
| orbital | 16 | 16 | 0 |
| electrical | 17 | 17 | 0 |
| mechanical | 11 | 10 | 1 (OCM `colonizes`) |
| planetary | 15 | 15 | 0 |
| terraform | 20 | 20 | 0 |
| **total** | **239** | **176** | **63** |

Name, tech requirement, mass, base cost, race restriction and Mystery
Trader flag were observed for all 239 rows.

What was observed (details in `PARITY.md`, "Components (CS-001, CS-002)"):

- **Technology Browser**, 13 race setups (PRT, LRT, tech 0 or 26, Mystery
  Trader items owned or not): every item's name, displayed mineral and
  resource cost, mass, tech requirement, availability label, and the
  values its description states. 3,095 readouts, all as computed by the
  rules below (`experiments/cs001/check.py`).
- **Ship & Starbase Designer**: every hull's and starbase's slot layout,
  the hull lists offered to six races, and starbase hull costs for three.
- **Planet status panel**: defense coverage of all five defense types.
- **Movement** (CS-002): the fuel factor of all 16 engines at warps 2–10
  and their free warps, 144 fleets.

## Columns

| Column | Meaning |
|---|---|
| `category` | `hull`, `starbase_hull`, `engine`, `scanner`, `shield`, `armor`, `beam`, `torpedo`, `bomb`, `mining_robot`, `mine_layer`, `orbital`, `electrical`, `mechanical`, `planetary`, `terraform` |
| `index` | position within the category, from 0, in the game's own order (the order of the Technology Browser and of the designer's lists) |
| `name` | as the game shows it |
| `tech` | required level in each of the six fields; buildable when every level is at least this |
| `mass` | kT per unit; `null` for planetary and terraform items (no mass); 0 for starbase hulls and orbital items |
| `cost` | **base** cost per unit: resources and kT of ironium, boranium, germanium, before race modifiers and miniaturization |
| `restriction` | race rules, see "Who can build what" |
| `mystery_trader` | a Mystery Trader item: not listed and not buildable unless the player owns it |
| `stats` | category values below |
| `status`, `binary_only` | provenance, see "Status" |

### Category values (`stats`)

Units: armor and shield in damage points (dp); ranges in light-years
unless noted; percentages are integers.

- **Hull**: `armor`, `initiative` (base, before computers), `fuel_capacity`
  (mg), `cargo_capacity` (kT), `slots`: in the designer's order, each with
  the part `kinds` it accepts and `max` count. The first slot of every
  ship hull is the engine slot, and its `max` is the number of engines the
  design **must** have (the designer says "needs N"). The designer's slot
  names are: "General Purpose" = scanner, shield, armor, beam, torpedo,
  mine layer, electrical, mechanical; "Weapon" = beam, torpedo.
  `mine_layer_multiplier` 2: mines laid by this hull are doubled (Mini and
  Super Mine Layer). `fuel_transport`: the hull's design gives fuel to its
  fleet (Fuel Transport, Super-Fuel Xport; see KERNEL.md "Other movement
  rules").
- **Starbase hull**: `armor`, `initiative`, `dock_capacity` (kT of hull
  mass the dock builds; 0 = no dock; `null` = unlimited), `slots`.
- **Engine**: `fuel_table`, indexed by warp 0–10: the factor `f(w)` of
  KERNEL.md "Fuel cost". `free_warps`: warps with `f = 0` (ram-scoop gain,
  KERNEL.md). `warp10_rated`: the engine does not lose ships at warp 10.
  `battle_warp`: the warp used for battle speed (10 for rated engines,
  else the highest warp ≤ 9 whose factor is at most 120).
- **Scanner** (ship): `range`, `penetrating_range` (0 = none). The Bat
  Scanner has range 0.
  `steals_cargo`: `fleets` (Pick Pocket) or `fleets_and_planets` (Robber
  Baron).
- **Shield** `shield`; **armor** `armor`.
- **Beam**: `damage`, `range` (squares), `initiative`, `kind` (`beam`,
  `gatling` hits every target in range, `sapper` damages shields only),
  `mines_swept` per year (see "Mine sweeping").
- **Torpedo**: `damage`, `range`, `initiative`, `accuracy` (%), `kind`
  (`torpedo` or `missile`, the capital missiles).
- **Bomb**: `kind` (`normal`, `smart`, `retro`), `kill_tenths_pct`
  (population killed, in tenths of a percent), `installations` destroyed,
  `min_kill` (colonists killed at least). Bombing rules are not specified
  here.
- **Mining robot**: `mining_rate` (kT per year, see "Remote mining");
  Orbital Adjuster: `terraform_pct` per year.
- **Mine layer**: `mines_per_year`, `field` (`standard`, `heavy`,
  `speed_bump`; see "Minefields").
- **Orbital**: stargates `safe_mass` (kT) and `safe_range` (ly), `null` =
  unlimited; mass drivers `warp`.
- **Electrical / mechanical**: the effect the item has: `cloak_points`,
  `jammer_pct`, `initiative` + `accuracy_pct` (battle computers),
  `beam_damage_pct` (capacitors), `battle_speed` (+1 per Maneuvering Jet,
  +2 per Overthruster, −4 quarter-squares for the Energy Dampener),
  `tachyon`, `fuel_capacity` and `fuel_per_year` (Anti-matter Generator),
  `cargo_capacity`, `beam_deflection_pct`, `colonizes`,
  `orbital_construction`, `bomb_min_kill`, `jump_gate`.
- **Planetary**: scanners `range` and `penetrating_range`; defenses
  `coverage_tenths_pct` (see "Defense coverage"); Genesis Device.
- **Terraform**: `axis` (`all`, `gravity`, `temperature`, `radiation`) and
  `amount` (± clicks).

Several parts outside their own category carry values too, for example
Croby Sharmor and Langston Shell 65 dp of armor, Multi Cargo Pod 50 dp of
armor, Fielded Kelarium a 50 dp shield, Mega Poly Shell a 100 dp shield
and an 80/40 scanner, Multi Contained Munition a 150/75 scanner, 40
standard mines a year and bomb values, Alien Miner and Enigma Pulsar half
a square of battle speed. These are in each row's `stats`.

## Who can build what (CONFIRMED, CS-001)

`restriction` holds four lists:

- `prt_only`: the item needs one of these primary racial traits;
- `prt_not`: forbidden to these primary traits;
- `lrt_required`: needs every one of these lesser traits;
- `lrt_forbidden`: forbidden with any of these lesser traits.

Abbreviations: HE Hyper-Expansion, SS Super Stealth, WM War Monger, CA
Claim Adjuster, IS Inner Strength, SD Space Demolition, PP Packet Physics,
IT Interstellar Traveler, AR Alternate Reality, JOAT Jack of All Trades;
IFE Improved Fuel Efficiency, TT Total Terraforming, ARM Advanced Remote
Mining, ISB Improved Starbases, GR Generalized Research, UR Ultimate
Recycling, MA Mineral Alchemy, NRSE No Ram Scoop Engines, CE Cheap
Engines, OBRM Only Basic Remote Mining, NAS No Advanced Scanners, LSP Low
Starting Population, BET Bleeding Edge Technology, RS Regenerating Shields.

The Technology Browser shows a race's restricted items as "UnAvail", items
it may build once its tech allows with their research cost, and buildable
items as "Available". Mystery Trader items the player does not own are not
listed at all. The designer's hull lists follow the same rules (observed
for SS + IFE/TT/ARM/ISB, HE, IS, WM, SD and AR).

## Cost for an owner

The cost of one unit for a given race, from the base `cost`, per component
(resources and each mineral separately). Divisions truncate.

1. **Miniaturization** (CONFIRMED, CS-001). Not for terraform items or for
   planetary scanners and defenses (the Genesis Device is included).
   - `m` = the smallest `level − requirement` over the fields where the item
     requires more than 0; if it requires nothing, `m` = the race's lowest
     level in any field.
   - If `m > 0`: `d = min(4·min(m, 19), 75)`; with BET
     `d = min(5·min(m, 19), 80)`. Each nonzero component `c` becomes
     `c − round(c·d/100)` (halves rounded up), at least 1.
2. **Race** (CONFIRMED, CS-001). The first case that matches applies:
   - IT, stargates: `c − c/4`.
   - WM, beams, torpedoes and bombs: `c − c/4`.
   - IS, beams, torpedoes and bombs: `c + c/4`.
   - CA, terraform items: resources `c/2` (minerals unchanged).
   - CE, engines: `c − c/2`.
3. **Bleeding Edge Technology** (CONFIRMED, CS-001, at tech 0): with BET,
   if the item has a requirement and `m ≤ 0` (the race does not exceed it
   in every required field), every component is doubled. Terraform and
   planetary items are never doubled (they skip step 1).

A design costs its hull plus `count ×` each part, each computed as above
(COMBAT.md "Design cost" is the same rule; this file adds the
terraform/planetary exemption and the CA case).

**Starbases** (CONFIRMED, CS-001 designer): a starbase design's cost is
computed as above, then with ISB or AR each component `c − c/5`, then
halved rounding up: `(c + 1)/2`. Vectors at tech 26 (base → shown):

| Race | Hull | Owner cost (step 1–3) | Shown |
|---|---|---|---|
| AR | Death Star | 154 Fe, 102 Bo, 448 Ge, 960 res | 62, 41, 180, 384 |
| SS + ISB | Space Station | 60, 40, 125, 300 | 24, 16, 50, 120 |
| SS + ISB | Space Dock | 10, 2, 12, 50 | 4, 1, 5, 20 |
| HE | Space Station | 60, 40, 125, 300 | 30, 20, 63, 150 |

**Technology Browser** (CONFIRMED, CS-001): shows the owner cost, except
starbase hulls and orbital items, shown as `c − c/2`, without the ISB/AR
reduction. Mass is not shown when it is 0.

**Planetary installations** other than parts (factories, mines, defenses,
alchemy, terraforming) are in KERNEL.md "Item costs". The defenses'
cost there is the base cost of the SDI row.

## Fuel tables (CONFIRMED, CS-002)

`fuel_table[w]` was confirmed for every engine at warps 2–10 by charging
one fleet per engine and warp (KERNEL.md "Fuel cost"; the corpus chose
fleet masses so the charge identifies `f` exactly). Warp 1 is free for
every engine (FM-002..004). Free warps beyond 1 were confirmed by the
ram-scoop gain, including how many following warps are also free.

Warp-10 losses (MEASURED, CS-002): of 22 ships moving at warp 10 with
engines not rated for it, 3 were destroyed (each from a different 2-ship
fleet); none of 10 ships with rated engines. A destroyed ship's fleet paid
the full year's fuel first, then kept only the survivors' share of fuel
and cargo (`trunc(x·survivors/ships)`). The 1-in-10 chance per ship
(KERNEL.md) is BINARY-ONLY.

## Mine sweeping, laying and remote mining (BINARY-ONLY)

- **Sweeping**: per beam stack, `count × damage × r²` mines a year, where
  `r` = the weapon's range, 4 for a gatling, range + 1 on a starbase;
  sappers sweep nothing. `mines_swept` in the table is this for one weapon
  on a ship (`damage × r²`).
- **Laying**: `Σ count × mines_per_year` per field type a year; each Multi
  Contained Munition adds 40 standard mines; ×2 on Mini and Super Mine
  Layer hulls.
- **Remote mining**: `Σ count × mining_rate` kT a year over a fleet's
  robots, at most 4000.

## Minefields (CONFIRMED in the Technology Browser, CS-001)

| Field | Safe speed | Hit chance per ly per warp above safe | Damage to a ship (with ram scoop) | To a fleet, at least (with ram scoop) |
|---|---|---|---|---|
| standard | warp 4 | 0.3% | 100 (125) | 500 (600) |
| heavy | warp 6 | 1.0% | 500 (600) | 2000 (2500) |
| speed bump | warp 5 | 3.5% | 0 | 0 |

How minefields act (effective warp, hits, damage) is in `OBJECTS.md`.

## Defense coverage (CONFIRMED, CS-001)

Planetary defenses: with `n` defenses of coverage `c` (tenths of a
percent), the planet's coverage is `1 − (1 − c/1000)^n`. The status panel
shows it truncated to two decimals. Vectors, 10 defenses: SDI 9.56%,
Missile Battery 18.29%, Laser Battery 21.56%, Planetary Shield 26.25%,
Neutron Shield 32.11%. The defense type is the best one the owner's tech
allows. What coverage does in bombing is not specified here.

## Cloak points

`cloak_points` convert to a percentage as in SCANNING.md "Fleet cloak".
The browser states that percentage for each cloaking part (CONFIRMED for
every part with cloak points except Enigma Pulsar, whose description does
not give one).

## Oddities

- **Planetary scanners and NAS.** The penetrating planetary scanners are
  forbidden with No Advanced Scanners (`lrt_forbidden`), like the three
  penetrating ship scanners (CONFIRMED, CS-001 NAS setups).
- **BET and exempt items** (BINARY-ONLY reading, CONFIRMED outcome). The
  original's cost routine leaves its miniaturization variable unset for
  terraform and planetary items and then tests it for the BET doubling.
  In every observed case they were not doubled; Elegy should not double
  them.
- **Starbase display.** The Technology Browser halves starbase hull costs
  but ignores ISB/AR; the designer shows the real build cost.
