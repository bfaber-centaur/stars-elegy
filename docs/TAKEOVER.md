# Takeover specification: bombing, invasion, colonization and capture

Behavioral specification of the J-RC3 rules by which planets change hands
or lose population to another player: orbital bombing, colonist drops and
ground combat, colonization, what a captured planet keeps, and where each
happens in the year. It also covers the waypoint tasks that move cargo or
ships between owners (transport drops, scrap, remote mining, merge,
transfer). It is written for an implementer working only from this public
repository and describes what happens, not how any file encodes it.

`PARITY.md`, section "Planet Takeover", holds the experiment records
(TK-001 to TK-007; per-case values in `experiments/tk/README.md`). This file
restates them as rules and adds rules that so far come only from white-box
analysis of the original program (private `stars-decomp`, promoted here as
behavior only). Part statistics (bomb kill rates, installation kills,
defense coverage, costs) belong in the public components table. Parts are
named here; numbers appear only where a rule needs a worked example.

## Status of each rule

- **CONFIRMED**: a white-box reading agrees with original-game oracle
  observations (TK case ids, `T-n` = prediction ids in
  `experiments/tk/README.md`). Vectors given for it are ground truth.
- **BINARY-ONLY**: read from the original program, with no oracle
  observation yet. Treat these as predictions; they are listed under Open
  experiments.
- **LEGACY BUG**: confirmed or read behavior that looks like an accident of
  the original implementation rather than a design intent. Implement it
  for parity, isolated so it can be switched off.

"Confirmed" covers the measured scope only: two players with the same JOAT
race (growth 15%), target planets at 100% habitability, the defender at
energy tech 3 to 5, one year per run.

## Conventions

- Population `P` is in **units of 100 colonists**, the unit the game
  stores. Colonists carried by a fleet are counted in the same units here.
- `P'` is a planet's population after this year's growth (`KERNEL.md`,
  Population growth).
- Divisions truncate unless stated. `round(x)` rounds halves up.
- `rand(n)` is a uniform draw in `0..n−1` from the game's generator.
  Bombing draws up to three numbers per bombed planet; capture draws for
  tech and artifacts; everything else here is deterministic.
- Kill rates are in tenths of a percent (permille): Cherry Bomb 25 = 2.5%.

## Where each task happens in the year (CONFIRMED where marked)

This refines `KERNEL.md` "Turn order" steps 2 and 6.

1. Orders, including manual cargo transfers, are applied.
2. **Before movement**, for fleets already at their waypoint 0:
   unloads (including colonist drops on other players' planets), scrap,
   colonize; then all queued colonist drops are resolved (ground combat,
   new colonies); then loads and merges; then cargo
   gifted to other players moves.
3. Movement; production and population growth.
4. Battles, then **bombing** (after every battle at every location).
5. **After movement**, for fleets at their new waypoint 0: unloads
   (including invasions by arriving transports), colonize, remote mining,
   mine laying; then queued drops are resolved; then the second research
   level-up check (`KERNEL.md`); then loads, merges and fleet transfers.

Consequences, all CONFIRMED (TK-001, TK-002, TK-003):

- A transport **already in orbit** with "unload colonists" invades before
  growth. 100 attacking units against 87 left 20, which then grew as the
  attacker's colony to 23 (T-5).
- A colony ship **already in orbit** with a colonize order colonizes
  before growth: 25 became 28 the same year. One that **arrives**
  colonizes after growth and ends the year with exactly the 25 it carried
  (T-1).
- Bombing uses `P'` and comes before arriving transports land. Every
  bombing and arrival case matched only when computed on `P'`.
- Research done this year applies to this year's bombing: the defender
  reached energy 5 during the year and its defenses then covered as Missile
  Batteries (T-8).
- A starbase destroyed in this year's battle no longer protects the
  planet. Bombing (T-2) and arrival invasions go ahead the same year.

### Order inside a phase (CONFIRMED, TK-114, TK-201; manual transfers BINARY-ONLY)

- **Fleet order.** Every per-fleet step (unloads, scrap, colonize, loads,
  merges, transfers, bombing triggers) walks fleets in **fleet order**: by
  owner, then by fleet number (the same order as `COMBAT.md`). Each fleet
  carries out its whole waypoint-0 task before the next fleet starts.
- **Drop resolution order.** Each drop joins a queue in the order it was
  made. When drops are resolved, the queue is walked from the front, and
  the first unresolved entry's planet is resolved with all of that
  planet's entries together. Planets are therefore resolved in the order
  of their first queued drop. Before movement, the queue starts with
  colonists given to foreign planets by manual cargo transfers in the
  orders (step 1), then the drops made by fleets in fleet order.
  CONFIRMED (TK-201 A): fleets 0, 1 and 12 dropping on planets 14, 3 and 8
  were resolved 14, 3, 8 (capture messages in that order), not in planet
  order. The manual-transfer part needs crafted orders and stays
  BINARY-ONLY.
- **"At the start of this phase".** Each of the two waypoint phases (step
  2, and steps 4–5 together) records, for every planet, whether it is
  owned, **before anything else in that phase**. For the after-movement
  phase that is before battles and bombing. It is not the owner at the
  start of the year: a planet colonized before movement and bombed empty
  the same year counts as owned for the after-movement drop, so an
  arriving freighter's unload colonizes it (as in T-4). A planet that was
  unowned when the after-movement phase began refuses the unload.

## Orbital bombing

### Who bombs (CONFIRMED, T-3, T-19, T-20)

A planet is bombed by a player when all of these hold:

- the planet is owned by another player (unowned planets are never
  bombed);
- the planet has **no starbase** of any kind (an unarmed Orbital Fort is
  enough to prevent it: T-3);
- at least one of that player's fleets in orbit has a battle plan whose
  "attack who" setting covers the planet's owner. "Nobody" never does.
  "Enemies" covers enemies only. "Enemies and neutrals" covers anyone who
  is not a friend. "Everyone" covers anyone, friends included. "Player
  *i* only" covers player *i* only, whatever the relation. Measured: with
  players enemies, "nobody" and "attacker itself only" did not bomb, and
  "player 1 only", "everyone" and "enemies" did; with players neutral,
  "enemies" did not bomb, but "player 1 only" and "everyone" did; with
  players friends, "everyone" bombed.

Nothing else is checked: not whether the fleet moved, fought or has fuel,
and not whether the fleet with the attacking plan has bombs.

**All of one player's fleets at the planet bomb as one** (CONFIRMED, T-20,
TK-005). Once one fleet qualifies, every bomb on every fleet that player has
in orbit there is summed into a single pass, whatever the other fleets'
plans and whichever fleet comes first. A Laser Frigate with an attacking
plan and no bombs made a bomber fleet with plan "nobody" bomb. Two fleets
of 5 Cherry each are one pass of 10 Cherry.

**Bombing order** (CONFIRMED: TK-201 B across planets, TK-113 across players). Bombing walks fleets in fleet order
(owner, then fleet number). The first fleet that qualifies at a planet
triggers its owner's single pass there, which is applied at once with its
random draws (factories, defenses, population); that owner's other fleets
at the planet are then skipped. So planets are bombed in the order of their
triggering fleets, not in planet order, and all of a lower-numbered
player's passes come before any of a higher-numbered player's. Several
players at one planet bomb it in player-number order, each against what
the previous one left. Once the planet is emptied it is unowned, and later
passes skip it.

### Bomb totals (CONFIRMED for the parts named, T-10..T-18)

For one player's pass, sum over every bomb item:

- **Normal bombs** (Lady Finger, Black Cat, M-70, M-80, Cherry, LBU-17,
  LBU-32, LBU-74, Hush-a-Boom): kill rate `A += kill`, installation kills
  `I += inst`. Lady Finger, Black Cat, M-70, M-80 and Cherry also add a
  minimum kill `M += 3` units each; the others add none.
- **Smart bombs** (Smart, Neutron, Enriched Neutron, Peerless,
  Annihilator): `Π *= (1 − kill/1000)`, starting from `Π = 1`; they kill
  no installations. `S = min(1000, round(1000 − 1000·Π))`.
- **Retro Bomb**: `R += 1` per bomb (CONFIRMED, T-16).
- **Multi Contained Munition** (a beam weapon) also counts as a normal
  bomb: `A += 20`, `I += 5`, `M += 3` per item (CONFIRMED, T-18).
- **Orbital Construction Module** counts as a bomb with only a minimum
  kill: `M += 20` per module (CONFIRMED, T-17).

Normal kill rates add (10 Cherry = 25%, not `1 − 0.975¹⁰`), and smart kill
rates multiply.

### Planetary defenses against bombs (CONFIRMED, T-6..T-9, TK-301, TK-302)

Coverage uses the planet owner's **best** planetary defense at its
**current** energy tech, not the one it built. Coverage per defense is
`c` permille (SDI 10, Missile Battery 20, Laser Battery 24, Planetary
Shield 30, Neutron Shield 38; all five CONFIRMED by the planet panel's
coverage in CS-001, `COMPONENTS.md`). The counted defenses are `n = min(installed,
operable defenses)` (`KERNEL.md`, Caps: `min(max defenses, 1000,
ceil(P'/25))`). If the owner has no defenses or no defense part, nothing
is reduced.

```text
s      = (1 − c/1000)^n        stored in single precision
sSmart = (1 − c/2000)^n        smart bombs see half the coverage
A = round(A·s)   M = round(M·s)   S = round(S·sSmart)
I = round(I·(1 − (1 − s)/2))   installations see half the coverage
```

Bombing never destroys defenses through `s`; defenses are lost only as
installation kills.

Vectors (100 SDI, 20 Cherry; defender at 100% habitability):
`P'` 1000 → 666 (40 counted); `P'` 100 → 42 (4 counted, the minimum
decides); 20 Smart on 1000 → 812, defenses unchanged. With Missile
Batteries the same cases give 777, 45 and 846. On a 1000 planet with 100
defenses (40 counted), 20 Cherry leave 811 with Laser Batteries and 852
with Planetary Shields, and 20 Smart leave 858 and 874 (TK-301, TK-302).

### Applying the pass (CONFIRMED, T-10..T-16; random parts MEASURED)

Installations first, when `I > 0` and `T = mines + factories + defenses >
0` (installed counts, not operable):

1. factories lose `⌊I·F/T⌋`, plus 1 if `rand(T) < (I·F mod T)`, at most F;
2. defenses lose `⌊I·D/T⌋`, plus 1 if `rand(T) < (I·D mod T)`, at most D;
3. mines lose the rest, `I − factories lost − defenses lost`, at most the
   mines there. When the two rounded-up kills together exceed `I`, the rest
   is negative and mines lose nothing; they never increase and never go
   below 0. Example: `I = 1`, one factory and one defense, no
   mines: each can lose 1 with chance ½, so 2 installations can die from
   `I = 1`. CONFIRMED (TK-202, 12 streams): with `I = 1` on mines 1,
   factories 20, defenses 20, the 72 planet outcomes were 21 × mines 0 with
   nothing else lost, 40 × one factory or one defense lost and mines kept,
   and 11 × one factory **and** one defense lost with mines still 1, never
   2. With `I = 3` the mines went to 0 only when exactly one factory and
   one defense were lost (7 of 24).
   The bombing message reports `factories lost + defenses lost + rest`
   with the negative rest included, so it can understate: two
   installations destroyed by `I = 1` are reported as 1 (LEGACY BUG,
   CONFIRMED; `MESSAGES.md`).

A draw is made only when its remainder is non-zero.

Population, when `P' > 0`:

1. smart kill `k1 = ⌊P'·S/1000⌋`, at most `P' − 1`: smart bombs alone
   never empty a planet;
2. normal kill on the rest: `x = (P' − k1)·A`; `k2 = ⌊x/1000⌋`, plus 1 if
   `rand(1000) ≤ x mod 1000`, drawn only when the remainder is non-zero
   (so the chance is `(r + 1)/1000`);
3. `k = k1 + k2`; if `A > 0` and `k = 0` then `k = 1`; `k = max(k, M)`;
   `k = min(k, P')`.

The order of random draws is factories, defenses, population.

Vectors: 10 Cherry on 920 → 690; 1 Lady Finger on 10 → 7 (the minimum
3); 1 LBU-17 on 10 → 9 (no minimum); 20 Peerless on 1150 → 412 and on 1 →
1; 10 Smart + 10 Cherry on 921 → 606; LBU-32 on 1000 with mines 30 and
factories 30 → pop 997, mines 16, factories 16. Random: Hush-a-Boom on 50
→ 48 or 49, never 47; LBU-17 on mines 20 / factories 10 → factories 5 or
4, mines always the rest of 16. Observed frequencies are in `PARITY.md`.

**Retro bombs** (CONFIRMED, T-16): `R = R − ⌊(1 − s)·R/2⌋`, at most 500.
Each environment axis moves toward its original value by up to `R`
clicks, **each axis separately** (the clicks are not shared). 3 Retro on
55/47/52 with original 50/50/50 → 52/50/50; the original is kept.

A planet whose population reaches 0 is **emptied**; see Capture.

## Colonist drops and ground combat

### Unloading colonists on another player's planet (CONFIRMED, T-4, T-28, T-29)

When a fleet unloads colonists on a planet it does not own:

- the planet is unowned and was unowned at the start of this phase:
  nothing lands, and the fleet keeps its colonists (message to the fleet
  owner);
- the planet has a starbase: refused, and the fleet keeps its colonists;
- the fleet owner is Alternate Reality: refused (CONFIRMED, T-33);
- otherwise the colonists leave the fleet and are queued as a drop. If the
  planet is owned, the drop is an invasion. If the planet was owned at the
  start of the phase but has been emptied since, for example by bombing
  this year, the drop is a colonization. It needs no colony module: a
  freighter colonized a planet bombed empty that year with all 50 units it
  carried (T-4).

The player relation is not checked. Unloading colonists on a **friend's**
planet invades it exactly as an enemy's (T-29, order set in the file; the
UI may not offer it).

Fuel is never unloaded to or loaded from a planet (CONFIRMED: MG-002,
MG-004, MG-006). With a planet as the waypoint target, every fuel action is
ignored: it moves no fuel, sends no message, and does not debit the fleet.
That holds for own planets with or without a starbase and for unowned
planets, and it includes "load optimal" below. Minerals in the same order
still move (MG-006-A: 20 kT ironium unloaded; 100 fuel stayed aboard).

**Minerals** unloaded on a planet the fleet's owner does not own (another
player's, whatever the relation, or an unowned one) are added to that
planet's surface, and the fleet loses them (CONFIRMED, TK-201 C–E: 50 kT
ironium onto an enemy planet without and with a starbase, and onto an
unowned planet, each surface 0 → 50, fleet 0, message 0x02d). Only cargo to
another player's **fleet** checks the relation: nothing moves to an enemy's
fleet.

**Unloading in deep space** (a waypoint that is not a planet, fleet or
salvage; CONFIRMED, TK-201 F): minerals are **destroyed**. The fleet loses them,
the owner gets the usual "unloaded" message, and no salvage object is made.
Colonists are refused: the fleet keeps them and the owner gets a failure
message. Fuel does not move, with no message and no debit (CONFIRMED,
MG-006-E/F: an unload-all and a load-optimal fuel order both kept 300). In
TK-201 F a freighter unloading 50 kT ironium and 50 colonists in deep space
got 0x02d for the ironium, then 0x165 and 0x04e; it kept the colonists, the
ironium was gone, and no object appeared. Only scrapping a fleet in deep space leaves
salvage (Other waypoint tasks).

### Unload and load amounts (CONFIRMED, FO-01..05, TK-114, TK-301)

A transport order sets, per cargo type (ironium, boranium, germanium,
colonists, fuel), one action and an amount `v` (kT; colonists in units of
100). With `C` = the fleet's cargo of that type and `A` = what the target
holds (planet surface minerals, or the planet's population for colonists):

| Action | Phase | Amount moved |
|---|---|---|
| unload all | unload | `C` |
| unload exactly `v` | unload | `min(v, C)` |
| load all | load | `min(A, free space)` |
| load exactly `v` | load | `min(v, A, free space)` |
| fill to `v`% | load | up to `v`% of capacity |
| wait for `v`% | load | as fill, and the fleet waits until met |
| set amount to `v` | either | `v − C`: load if positive, unload if negative |
| set waypoint to `v` | either | `A − v`: load the excess, or unload the shortfall |

Unload actions run in the first unload phase that reaches them and are then
cleared, so they happen once; load actions persist until satisfied.

"Load exactly" vectors (TK-301, TK-302, before movement): 30 colonists
from a 100 planet leave 70, which then grows; 40 ironium asked with 25 on
the surface loads 25; 300 asked with 500 on the surface and a 210 kT hold
loads 210 and leaves 290.

**Load optimal** (fuel only; CONFIRMED in MG-003 and MG-006) acts only when
waypoint 0 targets a fleet or deep space. Let *need* be the estimated fuel
for the leg to the next waypoint.

- **Fuel below the need, before movement.** No fuel is loaded. The owner
  gets 0x03c with the shortfall, or 0x03d with capacity and need when the
  tank is smaller than the need. The fleet **does not move** this year.
- **Fuel above the need.** The surplus is unloaded to the target fleet
  (0x02d). Deep space takes none, so nothing happens there.
- **No further waypoint.** All fuel counts as surplus. A target fleet takes
  all of it (FO-02 Q). Deep space takes none.
- **Planet target.** Nothing happens (see above).
- The order never loads fuel.

On a planet the fleet's owner owns, unloaded colonists are added to the
population at once, with no cap. Before movement that is **before** this
year's growth, so they grow this year; after movement they do not.
Unloaded minerals join the surface the same way. Loading colonists
subtracts them from the population, and nothing stops a load from taking
every colonist (CONFIRMED, TK-201 G). The planet then stays owned with
population 0 until this year's growth, where it is lost like any other
empty planet (message 0x040 or 0x023, `MESSAGES.md`). In TK-201 a "load
all" took all 50 from player 0's planet 12 and from its homeworld 17; both
were unowned at the end of the year. These own-planet rules belong with
`KERNEL.md` production; they are given here until KERNEL covers
transport.

### Ground combat (CONFIRMED, T-21..T-25)

All drops queued for one planet in one phase are resolved together.

1. `s` is the planet owner's bombing survival factor (above; 1 when the
   planet is unowned or has no defenses). Against troops it is
   `s' = s + (1 − s)/4`: defenses are 75% as effective as against bombs.
2. Each attacking player `p` has `troops[p]` (units), and its strength is
   `strength[p] = ⌊⌊troops[p]·k/100⌋·s'⌋`, with `k = 110`. For War Monger
   `k = 165` (CONFIRMED, T-24), and for Alternate Reality `k = 0`
   (BINARY-ONLY; an AR drop lands only by colonizing an unowned planet,
   where `Σ = 0` lands every colonist anyway, T-33).
   `Σ` is the sum of all strengths.
3. If the planet is owned, the defender strength is `D = P` (×2 for Inner
   Strength, CONFIRMED, T-24).
   - `D > Σ`: every attacker dies, and the planet loses `⌊P·Σ/D⌋`. 200
     against 110 leaves 90.
   - `D ≤ Σ` (**a tie goes to the attackers**): the planet is emptied
     (Capture, below) and the attackers resolve as for an empty planet,
     with `D` subtracted.
4. Empty-planet resolution, with `D = 0` for an unowned planet. A single
   attacking player `w` lands
   `max(1, troops[w]·⌊(Σ − D)·best/Σ⌋/best)`, where `best =
   strength[w]`. If `Σ = 0`, it lands all its troops.

Vectors: 100 units (strength 110) against 100 → 9; against 110 → 1; 600
against 500 with 20 SDI (strength 569) → 72; 300 against 200 with 10 SDI
(strength 310) → 106. With 20 Missile Batteries, the 600 attackers had
strength 495 < 500, and the defender kept 5. With 20 Laser Batteries the
same drop has strength 469 and the defender keeps 31; with 20 Planetary
Shields, strength 434 and 66 kept (TK-301, TK-302).

### Several players dropping at once (LEGACY BUG, CONFIRMED, T-32)

When more than one player drops on the same planet in the same phase, the
winner is picked by a scan over players in **index order**. Each player
whose strength is **greater than or equal to** the current best becomes
the new best, and the old best becomes `second`. A strength **equal** to
the best also sets a tie flag, which a later strictly greater strength
clears.

- If the tie flag is set at the end, nobody lands. The planet stays empty,
  and every dropping player loses its colonists. Colony ships are consumed
  and their minerals delivered.
- Otherwise the winner lands as in step 4, then reduced by
  `·(best − second)/best` **only if `second > 0`**, and at least 1.

Because `second` only ever holds a **lower-index** player's strength, a
lower-index winner is never reduced by a higher-index rival, while a
higher-index winner is. Measured with colony ships: player 0 25 vs
player 1 12 → player 0 with 25; player 0 12 vs player 1 25 → player 1
with 12 (reduced by `(27 − 13)/27`); 25 vs 25 → nobody, and the planet
received both ships' minerals.

## Colonization (CONFIRMED, T-1, T-30, T-31; requirements T-39, TK-201 H)

A colonize order succeeds when the fleet orbits a planet that is
**unowned now**, carries colonists, and has at least one ship whose design
has a Colonization Module or an Orbital Construction Module. Otherwise it
fails with a message, and the fleet is kept. There is **no habitability
check**: a red planet was colonized and its population then declines per
`KERNEL.md` (T-31). The order is tried **once**, in the first waypoint
phase that reaches it: before movement for a fleet already in orbit, after
movement for one that arrives. A failure ends the order (Colonize is tried
once, below).

On success:

- The **whole fleet** is consumed, not just the colony ship.
- The planet's surface gains, per mineral, `⌊3·C/4⌋`, where `C` is the
  summed cost of every ship in the fleet. Each ship's cost is its design
  cost for the owner **this year**, after miniaturization (`COMBAT.md`,
  Design cost). Mineral cargo is added on top. CONFIRMED: Colony Ship hull +
  Long Hump 6 + Colonization Module left 18/6/17 kT at tech 3 and 4/1/5 at
  tech 26, which are exactly `⌊3/4⌋` of 25/9/23 and 6/2/7 (T-30). This is
  also the first direct oracle check of the miniaturization rounding.
- The colonists become a queued drop resolved as above. An uncontested
  colony ship lands all its colonists.
- The new colony gets the owner's default production queue. Alternate
  Reality skips the first three default items, and Claim Adjuster skips
  the fifth and sixth. The colony also gets the owner's default "only
  leftover to research" setting, and an Alternate Reality colony gets a
  starbase of the owner's first starbase design (all CONFIRMED, T-26,
  T-33).

## Capture: what a planet keeps (CONFIRMED, T-21, T-26, T-27)

A planet that loses its whole population (to bombing, ground combat,
starvation, a packet or an AR starbase loss) is emptied:

- **kept**: mines, factories (both may exceed what the new owner can
  operate), surface minerals, concentrations, current and original
  environment, and the population growth carry (37 before growth, 42
  after growth and capture: T-27; see `KERNEL.md` Population growth);
- **lost**: owner, population, defenses (0), planetary scanner (none),
  production queue, starbase, mass-driver destination, and the
  "only leftover to research" setting.
- A Claim Adjuster owner's planet returns its current environment to its
  original values when emptied (CONFIRMED, TK-116: 50/50/50 back to
  55/47/52 when a JOAT attacker captured it). The game then stores no
  separate original values, because they are equal. If the new owner is
  also a Claim Adjuster, its end-of-year automatic terraforming (`KERNEL.md`
  Turn order, step 7) runs later the same year and can move the environment
  straight back toward the new owner's ideal. In TK-108 a CA attacker's
  capture ended the year at 50/50/50 (MEASURED in that one case; the CA
  terraforming rule itself is not yet in `KERNEL.md`).

A captured planet then belongs to the winning player as a new colony
(Colonization, above). Additionally:

- the old owner is told (CONFIRMED: message 0x007, `MESSAGES.md`);
- the new owner makes one **tech attempt**, exactly as in `COMBAT.md`, Tech
  from battle, steps 1–5 (MEASURED, TK-115: gains only in a field where the
  old owner was ahead, never more than one level a year; the draw order is
  BINARY-ONLY). The "seen" levels are the **old owner's current
  levels** in each field, and no Mystery Trader item has a chance, so step 3
  always makes its 13 `rand(13)` draws and gives nothing. The attempt
  shares the "already gained this turn" mark with battles and scrapping:
  a player that gained this turn makes no draws. Only a capture of an
  owned planet makes an attempt, not a colonization of an unowned one. On
  that planet the draws come after the ground combat (which draws nothing)
  and before the artifact draws below;
- a planet with an ancient artifact gives research points (see Ancient
  artifacts, below).

The production queue and the leftover setting after a capture are the
new owner's defaults, as for a colony (CONFIRMED, T-26).

### Ancient artifacts (CONFIRMED, TK-303, TK-304, TK-306; amounts MEASURED)

A planet may hold an ancient artifact (new games place them only with
random events on, `UNIVERSE.md`). When random events are on, the artifact
is found at the end of a drop resolution on that planet if the planet has
an owner afterwards:

- a colony on an unowned planet (TK-303 A2, A3);
- a capture (TK-306 C1);
- an invasion the defender beat off: the **defender** finds it (TK-306 C2).

The finder gets `100 + rand(301)` research points in a random field
`rand(6)` (any of the six, energy included), and the artifact is gone.
When the planet's population after the landing is below 1,000 colonists,
the points are scaled by `pop/1000` (TK-303 A3: a 500-colonist colony got
53 to 196 in six streams, against 122 to 272 for a 2,500-colonist colony).
The message is 0x05e (`MESSAGES.md`), after that planet's landing
messages. The points join the field's research before this year's
level-ups, so they can raise a level the same year (TK-306: player 1 went
from construction 3 to 4 with 392 points).

Draw order on that planet (BINARY-ONLY): the field, then the points,
after any capture tech attempt.

Slower tech does **not** halve the points: TK-304 (slower tech) gave the
same field and points as TK-303 in all six streams (LEGACY BUG in the
binary reading: the halving is computed after the points are added and is
never used).

No artifact is found by an owned planet with no landing (TK-306 C3), or by
an unload onto one's own planet (TK-306 C4); both keep the artifact. With
random events off nothing happens (BINARY-ONLY).

### The homeworld mark after capture (CONFIRMED in one run, T-41)

Each year, after fleet movement (`KERNEL.md` Turn order, step 3.6), the
game clears every planet's homeworld mark. It then sets the mark again on
the planet that each player's own record names as its homeworld. Only
new-game creation writes that record; no later step changes it. So:

- a captured homeworld **keeps** the homeworld mark under its new owner,
  and with it the mining floor that the mark gives (`KERNEL.md` Mining);
- the old owner gets no new homeworld, even while it holds other planets;
- the new owner keeps its own homeworld too, so it can hold two marked
  planets;
- the mark stays even when the planet is unowned, or when the player who
  started there is dead.

Prediction T-41 (MG-005, `experiments/mg`): a player 0 transport in orbit
of player 1's homeworld captures it before movement. After the year, the
planet belongs to player 0, is still marked as a homeworld, and player 1's
record still names it.

Result (MG-005, cycles 20000, apparatus `evidence/mg/mg005`): as predicted.
Planet 8 was owned by player 0 and still marked as a homeworld. Player 1's
record still named planet 8, and player 0's homeworld 17 stayed marked.
Both cases left open there are CONFIRMED by TK-201 (cycles 20000 and
30000). Player 1 lost its homeworld 8 while keeping other planets: planet
8 kept the mark under player 0, and player 1's record still named it, with
no other player 1 planet marked. Player 0's homeworld 17 was emptied by
loading every colonist (above): it was unowned and still marked at the end
of that year **and of the next**, and player 0's record still named 17.

## Design parts dropped when the year is generated (CONFIRMED in one setting)

When the original game generates a year, it re-checks every ship design
against its owner's tech. A slot whose part the owner **lacks the tech
for** is emptied, the design is written back without it, and ships of that
design act without it. Race-restricted parts (Retro Bomb, which only Claim
Adjuster may build; the Orbital Construction Module, Alternate Reality only)
and the twelve Mystery Trader parts (among them Hush-a-Boom and Multi
Contained Munition) are **not** removed by this check, even when the owner
could not have picked them, and they work.

Measured with a JOAT owner at tech 3 in every field: Cherry, Smart,
Peerless, LBU-17 and LBU-32 were removed. Lady Finger (within tech),
Hush-a-Boom, Retro, the Orbital Construction Module and the Multi
Contained Munition stayed and bombed. At tech 26 nothing was removed. This
agrees with SC-021 (a scanner above the owner's tech was removed).

For Elegy this matters only when designs come from outside the UI
(imported files, edited states): such designs keep parts the owner could
never have chosen. Whether Elegy accepts or rejects them is a project
choice; parity is "keep and use".

## Other waypoint tasks (CONFIRMED, T-34, T-35, FO corpus)

- **Scrap** (T-34): before movement only. A fleet that arrives with a scrap order
  is scrapped at the start of the next year's waypoint phase. Per mineral,
  with `C` = the fleet's cost:
  - at a planet with a starbase: `4C/5` (`9C/10` if the planet's owner has
    Ultimate Recycling);
  - at a planet without a starbase: `C/3` (`9C/20` with Ultimate
    Recycling);
  - in deep space: `C/3` left as salvage.

  Mineral cargo is added on top. Ultimate Recycling is the **planet
  owner's** trait. Colonists join the planet only if the fleet owner owns
  it. Scrapping at a starbase gives the **planet owner** one tech attempt,
  as in battle (`COMBAT.md`, Tech from battle): the "seen" levels are the
  highest tech each field's requirement reaches among the scrapped ships'
  hulls and parts. CONFIRMED (TK-203, 12 cycle settings): a Scout with Long
  Hump 6 (propulsion 3) scrapped at each of two starbases of a player at
  tech 0 gave that player propulsion 1 in 8 settings (7 at the first
  starbase, 1 at the second after the first gave nothing; predicted chance
  0.555), never more than one level and never another field; the gain
  replaced 0x141 by 0x13d naming propulsion. A planet without a starbase
  gave no attempt (0x140). The scrapping fleet's owner gains nothing.

  Mystery Trader parts (MEASURED, TK-305, 12 cycle settings): a fleet of
  12 bombers (12 designs, each with 2 Hush-a-Boom) scrapped at three
  starbases of a player at tech 0. At the first starbase the player got
  the Hush-a-Boom in 5 settings (0x13c), a level in 5 (electronics,
  propulsion, construction, biotechnology twice; 0x13d) and nothing in 2;
  the second and third starbases never gave anything (0x141), because a
  gain blocks further attempts that year and, in the two settings without
  a gain, the later attempts failed too. Energy never came up. The model
  (`COMBAT.md`, Tech from battle, step 3: the part's chance is the
  number seen, here 24%, on each of 13 `rand(13)` picks) predicts the part
  in about 21% of passing attempts and an attempt passing half the time;
  10 of 12 first attempts passed and 5 of 10 gains were the part. Both are
  above the model (about 2% and 4% likely by chance); see Open
  experiments.
- **Remote mining** (T-35): after movement only, by a fleet that did not move
  this year, at an unowned planet; the order stays. An arriving miner
  therefore mines nothing the year it arrives.
- **Merge with fleet** (FO-03): in both load phases; the ordering fleet
  merges into the target own fleet.
- **Transfer fleet** (FO-04, FO-05): last task of the year. A fleet
  carrying colonists is refused.
- **Cargo to another player's fleet** (`PARITY.md`, Another player's
  fleet): nothing moves when the receiver's relation toward the giver is
  enemy; colonists are never given to another player's fleet.

### Colonize is tried once (CONFIRMED, TK-113)

A failed colonize order is **not retried**. Whatever the reason (not
orbiting a planet, planet owned, no colonists, no colony module), the fleet
gets the failure message and then the "completed its assigned orders"
message, and its waypoint task is cleared to none. The fleet stays in orbit
with its cargo.

So a planet emptied in the same phase does not help a colony ship whose
order failed on it. In TK-113 players 0 and 2 dropped 150 each on a
planet of 100: a tie, so the planet was emptied and nobody landed. Player
0's colony ship at that planet had already failed with "planet owned". It
kept its 25 colonists and its task was cleared, both when it was in orbit
(before movement) and when it arrived (after movement). The planet stayed
unowned with no minerals. stars-elegy #34 described a retry in the load
phase. That reading was wrong.

## Randomness

| Draw | Rule |
|---|---|
| installation kill roundings, population kill rounding | Bombing |
| tech learned on capture or scrap at a starbase | Capture, Scrap (same sequence as `COMBAT.md`) |
| artifact field and points | Capture |

Ground combat, colonization, scrap minerals and retro bombing are
deterministic. The draws of a year come in this order (BINARY-ONLY): drop
resolutions before movement (planet by planet, as in "Order inside a
phase"), then battles, then bombing passes in fleet order, then drop
resolutions after movement. Random-stream pinning for experiments:
`ORACLE.md`.

## Open experiments

Rounds 1–4 (TK-001..TK-306), the FO corpus and the MG runs measured every
other rule here. What is left:

- Manual cargo transfers to another player's planet or fleet. They are
  legal client orders but cannot be put in a host file, so they wait on
  client automation (client-orders, combat oracle lane).
  Predictions TK-401 to TK-410 are in `experiments/tk/manual-transfers.md`.
- Why Mystery Trader parts came from scrapping more often than the model
  predicts (TK-305). A larger sample, or replaying the random stream with
  the known draw counts, would tell a wrong model from an unlucky one.
- The draw order of a whole year (drops, battles, bombing, capture tech)
  as seen through the random stream; only the bombing part is measured.
- Alternate Reality `k = 0` in a contested drop (an AR invasion is refused
  before strength matters, so legal orders do not reach it).

## Sources

- `PARITY.md` "Planet Takeover" and `experiments/tk/README.md`: TK-001 to
  TK-306, every case and value; raw files in private
  `stars-oracle-apparatus` `evidence/tk/`, `evidence/tk2/`,
  `evidence/tk3/` and `evidence/tk4/`.
- White-box reading: private `stars-decomp` `docs/takeover.md` (§10 is
  the reconciliation with TK) and `docs/takeover-predictions.md`.
- Related specs: `KERNEL.md` (turn order, growth, caps, research),
  `COMBAT.md` (battles, design cost, tech gained), `SCANNING.md`.
