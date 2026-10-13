# GC-1 prediction: ground combat with two drops by one player

Pre-run record. It is written and pushed before any run of this start,
and it is never edited after the runs.

## Question

Lane G's rule (stars-elegy #195, `TAKEOVER.md` "Ground combat", head
6fc5c4d) computes strength per drop, `⌊⌊c·110/100⌋·s'⌋`, applying both
floors to each drop. It then pools the strengths, with no sequential
resolution. Its evidence is one MEASURED case (RG-003 2469). GC-1 tells
apart three readings:

- **H-drop** (lane G): `Σ` is the sum of the per-drop strengths, and the
  player's `best` is its own sum.
- **H-player**: one strength per player, from its total troops:
  `⌊⌊(c₁+c₂)·110/100⌋·s'⌋`.
- **H-seq**: the drops resolve one after another in fleet order. Each
  one fights the defenders left by the one before, and a drop onto a
  planet the player already holds just adds its colonists.

## Inputs, checked before the run

The defender is player 1 (JOAT, not IS) at energy 26. Its best planetary
defense is the Neutron Shield (`c` = 38 permille, needs energy 23,
`data/components.json`). Each target planet has 10 defenses, and all of
them count: `ceil(P/25)` is at least 14.

- `s = 0.962^10 = 0.678814` (single precision 0.6788139).
- `s' = s + (1 − s)/4 = 0.759110`.

Strengths, with the fraction before the floor:

| Drop (units) | `⌊c·1.1⌋` | `·s'` | Strength |
|---|---:|---:|---:|
| 395 | 434 | 329.45 | 329 |
| 165 | 181 | 137.40 | 137 |
| 560 (one player's total) | 616 | 467.61 | 467 |

Every fraction is at least 0.40 from an integer, so a float-versus-double
difference in `s'` cannot move a floor. Lane G's suggested 125-unit drop
was not used: `137·s' = 103.998`, which sits on the floor boundary. It
was replaced by 165.

## Start

Spec: `gc1.spec` (Combat Lab base2400). Each target planet is player 1's
own, with environment 50/50/50 (100% habitability), carry 0 and 10
defenses. Player 0's Medium Freighters orbit the planet with a
waypoint-0 unload. So the drops resolve before movement and before
growth, as in T-5, and `D = P` at the start of the year.

| Case | Planet | P | Drops, in fleet order |
|---|---|---:|---|
| C | 2 | 329 | fleet 0: 395, then fleet 1: 165 |
| C2 | 10 | 329 | fleet 2: 165, then fleet 3: 395 |
| R | 20 | 600 | fleet 4: 395, then fleet 5: 165 |

Runs: one pinned year at cycles 20000 and 30000.

## Predictions

Landing (TAKEOVER step 4, one player): `L = max(1, ⌊troops·⌊(Σ − D)·best/Σ⌋/best⌋)`,
with `best = Σ` and `troops = 560`.

| Case | H-drop (lane G) | H-player | H-seq |
|---|---|---|---|
| C: landed (0x007 to player 1) | Σ 466: **164** | S 467: 165 | 395 first: 329 vs 329, a tie, so the attackers win and 1 lands; then +165 = 166 |
| C: year-end population, after growth (player 0, G 15, hab 100) | 188 | 189 | 190 |
| C2: landed | **164** | 165 | 165 first: 137 < 329, repelled, P 192; then 395: 395·137/329 → 164 |
| R: defender loses `⌊P·Σ/D⌋` = Σ | 466, P 134 | 467, P 133 | 329 then 137: 466, P 134 |
| R: year-end population, after growth (player 1, G 15) | **154** | 152 | 154 |

The growth figures follow `KERNEL.md` "Population growth": `P < max/4`,
so `g = 1500`.
- C: from 164, 165 and 166 with carry 0, the results are 188, 189 and
  190 (carry 60, 75 and 90).
- R: 134 gives 154 (carry 10), and 133 gives 152 (carry 95).

So:
- C separates all three readings by one unit each.
- C2 checks that the order of the drops does not change H-drop's result.
- R separates per-drop floors from a per-player floor.

Messages expected:
- C and C2: 0x00c to player 0, and 0x007 to player 1, whose colonists
  field is the landed count.
- R: 0x001 to player 0 and 0x004 to player 1 (`MESSAGES.md`).
