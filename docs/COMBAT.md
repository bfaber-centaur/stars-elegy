# Combat specification

This file states the J-RC3 battle rules as behavior: who fights, how the
board is set up, how tokens move, choose targets and fire, how damage is
applied, and what happens after a battle (salvage, repair, tech). It is
written for an implementer who works only from this public repository.

`PARITY.md` "Combat" holds the experiment records (CB-000..CB-019) these
rules come from, with the measured numbers. This file restates those
results as rules, links to them rather than copying the data, and adds the
rules that so far come only from white-box analysis of the original
program (private `stars-decomp`, promoted here as behavior only).

## Status of each rule

Every rule carries one status (as in `KERNEL.md`):

- **CONFIRMED** (with CB case ids): a white-box reading agrees with
  original-game oracle observations in the cases named. "Confirmed" covers
  that scope only.
- **BINARY-ONLY**: read from the original program, with no oracle
  observation yet. Expect most of these to hold, but treat them as
  predictions.
- **LEGACY BUG**: the original behaves in a way that looks unintended. The
  observable behavior is described plainly; Elegy decides whether to
  reproduce it.

The oracle corpus uses two players, tech 26 (except where a case says
otherwise), the Humanoid (JOAT) race and the "Combat Lab" universe
(`ORACLE.md`). Rules that depend on more players, other races or other
lesser racial traits are BINARY-ONLY unless a case says otherwise.

## Conventions

- Integers. Every division truncates toward zero unless the rule says
  otherwise. "ceil" is said explicitly where it is used.
- `rand(n)` is a uniform draw in `0..n−1`. Elegy has its own generator;
  this file says what is drawn, when and how often, not the original
  stream. "Random draws" below lists every draw a battle makes.
- Board squares are `(x, y)` with `x, y` in `0..9`. Distance is the
  Chebyshev distance `max(|dx|, |dy|)`.
- A **token** is one design's ships from one fleet (a stack), or a
  starbase. `ships` is the number of ships in it.
- Damage on a stack is stored as two numbers: `pct`, the percentage of its
  ships that are damaged, and `units`, the damage per damaged ship in
  1/500 of that design's armor (`0..499`).
- Battle plan fields: tactic, primary target, secondary target,
  attack-who, dump cargo. Tactic numbers in this file: 0 disengage,
  1 disengage if challenged, 2 minimize damage to self, 3 maximize net
  damage, 4 maximize damage ratio, 5 maximize damage.
- Target types: 0 none, 1 any, 2 starbase, 3 armed ships, 4 bombers and
  freighters, 5 unarmed ships, 6 fuel transports, 7 freighters.
- Attack-who: nobody, enemies, neutrals and enemies, everyone, or one
  named player.
- Relations are per player and need not be symmetric: friend, neutral or
  enemy.

## Where battles happen in the turn (BINARY-ONLY)

Battles are fought after movement and production, at the start of the
post-movement waypoint phase (step 6 of the turn order in `KERNEL.md`):
before bombing, before the post-movement unload/load tasks, mine sweeping
and repair. Repair later in the same turn skips every fleet that fought.

There is at most one battle per location per turn. A location is a set of
fleets at **exactly** the same x and y. Planets are not members of a
location on their own: a planet's owner takes part only through a starbase
orbiting it.

Locations are examined in the order of their first fleet, with fleets
ordered by owner and then by fleet number. The order only matters for the
random stream and for the plan-0 legacy bug below.

## Who fights (CONFIRMED in part; see each rule)

1. **Aggressors.** A fleet is an aggressor when its plan's primary target
   is not "none", its attack-who is not "nobody", and it is armed (has at
   least one beam weapon or torpedo; bombs do not count). CONFIRMED:
   - No battle when both sides attack nobody (CB-005, P-5).
   - No battle when the only side that attacks enemies is unarmed
     (CB-006).
2. **Only fleets start battles.** With no aggressor fleet at the location
   there is no battle, whatever the starbase there is armed with or its
   plan says. CONFIRMED: six lone-starbase configurations (CB-002 C9/C10,
   CB-003 S2, CB-004 S2, CB-006 both planets) and the Q-1 controls
   (CB-011..014 S2/S3).
3. **Attack sets.** Each aggressor's owner attacks every other player
   present at the location whom attack-who selects:
   - "enemies": players it considers enemies;
   - "neutrals and enemies": players it considers neutral or enemy;
   - "everyone": every other player;
   - a named player: that player.
4. **Starbases join.** A starbase at the location's planet puts its owner
   in the present set, armed or not. If the starbase is armed and the
   owner's battle plan 0 (the default plan) has an attack-who other than
   "nobody", plan 0 supplies the owner's attack set, by the same rule
   as a fleet.
   - CONFIRMED (CB-011, Q-1): player 1's armed fleet attacked "enemies"
     while player 1 considered player 0 neutral. Player 0's Laser Station
     had plan 0 "enemies", and a battle happened in which the station
     fired. There was no battle with an unarmed station, with an unarmed
     visitor, or with plan 0 "nobody".
5. **Retaliation and friends** (BINARY-ONLY in general), repeated until
   nothing changes:
   - A player attacked by someone attacks back.
   - A present player who is a friend of an involved player joins and
     takes on the attack sets of its involved friends.
   - CONFIRMED: a stack whose plan attacks nobody fires back once a
     battle has started (CB-002, CB-009; P-6).
6. **Involvement.** Players with a non-empty attack set, or who are
   attacked, are involved. The battle happens when two or more players
   are involved.
   - Every involved player's fleets at the location take part.
   - So does the starbase of an involved owner, armed or not. CONFIRMED
     for the unarmed case: CB-005, CB-011..013 S4/S5.
   - Uninvolved players present only observe.
7. **Token cap.** At most 256 tokens (BINARY-ONLY).
   - If the involved fleets need more, each player gets a quota of
     `255 / players` stacks, and fleets beyond their quota are left out.
   - Then left-out fleets are added back while room remains.
   - Players with a left-out fleet are told that some fleets missed the
     battle.
8. **Excluded fleets** (BINARY-ONLY): a fleet carrying a particular
   status flag is not grouped with the others. What sets that flag is not
   known.

### LEGACY BUG: plan 0 "everyone" or "a named player" at a starbase

When the starbase's owner has plan 0 attack-who **"everyone" or a named
player**, the attack set is not given to the starbase's owner. It is
given to another player, X. Plan 0 "enemies" and "neutrals and enemies"
work as intended. X is (BINARY-ONLY, consistent with CB-011..013):

- player 0, if the location examined just before this one had a battle;
- the owner of the last fleet in the previous location's fleet order, if
  that location had no battle (for a lone fleet, its owner);
- undetermined for the first location examined in a turn. The value is
  left over from earlier processing.

The attack set given to X is the one plan 0 describes for the starbase's
owner. "Everyone" means every present player other than the owner;
"player B" means B.

Observable consequences with two players: A owns the starbase, and B
visits with an aggressor fleet that does not itself attack A.

- "Everyone" always produces the same battle as "enemies". Whether
  X = A or X = B, both A and B are involved.
- "Player B" with X = A is the intended battle.
- "Player B" with X = B makes B its own attacker. The prediction is a
  battle record with one involved player and no shots (`combat-predictions`
  R-10, Open experiments).
- CONFIRMED in the X = A case: the plan-0 "everyone" (three random
  streams) and "player 1" (one stream) battles were identical to the
  "enemies" battle, in a turn where an earlier location had a battle
  (CB-012, CB-013).

## Board setup

### Start squares (CONFIRMED for two players, CB-001..CB-019)

The board is 10×10. Each involved player has one start square, chosen by
its rank among the involved players (lowest player number first). All of
that player's tokens, starbase included, start on it. With `n` involved
players (BINARY-ONLY for `n ≠ 2`):

| n | squares (x,y) by rank |
|---|---|
| 1 | (4,4) |
| 2 | (1,4) (8,5) |
| 3 | (4,1) (8,8) (1,8) |
| 4 | (1,1) (8,8) (1,8) (8,1) |
| 5 | (4,1) (6,8) (1,4) (8,4) (2,8) |
| 6 | (1,4) (8,5) (2,8) (7,1) (6,8) (3,1) |
| 7 | (1,1) (1,5) (2,8) (6,8) (8,6) (8,2) (5,1) |
| 8 | (1,3) (1,6) (3,8) (6,8) (8,6) (8,3) (6,1) (3,1) |
| 9 | (1,3) (8,6) (3,8) (6,1) (1,6) (8,3) (6,8) (3,1) (4,4) |
| 10 | (2,1) (5,1) (8,1) (1,4) (8,4) (4,5) (1,7) (8,7) (3,8) (6,8) |
| 11 | (1,3) (8,6) (3,8) (6,1) (1,6) (8,3) (6,8) (3,1) (3,4) (6,3) (6,6) |
| 12 | (1,4) (8,5) (2,8) (7,1) (6,8) (3,1) (1,6) (8,3) (1,2) (4,8) (5,1) (8,7) |
| 13 | (1,1) (1,3) (1,5) (1,7) (3,1) (5,1) (7,1) (8,3) (8,5) (3,8) (5,8) (7,8) (4,4) |
| 14 | (1,1) (1,3) (1,5) (1,7) (2,8) (4,8) (6,8) (8,8) (8,6) (8,4) (8,2) (7,1) (5,1) (3,1) |
| 15 | (1,1) (1,3) (1,5) (1,7) (2,8) (4,8) (6,8) (8,8) (8,6) (8,4) (8,2) (7,1) (5,1) (3,1) (4,4) |
| 16 | (1,1) (1,3) (1,5) (1,7) (2,8) (4,8) (6,8) (8,8) (8,6) (8,4) (8,2) (7,1) (5,1) (3,1) (3,3) (6,6) |

### Setup steps (BINARY-ONLY except as marked)

For each involved fleet, in location order:

1. The fleet is marked as having fought: it gets no repair this turn.
2. If its plan has "dump cargo", its minerals go to the planet's surface,
   or to deep-space salvage. Colonists are not dumped (inferred).
3. One token is created per design with ships in the fleet.

A starbase token is placed for the starbase of an involved owner (see "Starbases in battle").

Then the token order is shuffled: for `i = 0..n−1`, swap token `i` with
token `i + rand(n − i)`. Token order matters for movement ties, firing
order and target ties.

**Energy Dampener** (CONFIRMED, CB-002 C8): if any token in the battle
carries an Energy Dampener, every ship token's speed code is 4 lower
(at least 0). Starbases are unaffected. The dampener's own mass is its
part mass (the record matched the part-table sum; see `PARITY.md`,
"Resolved reconciliation").

### Token values (CONFIRMED, CB-000..CB-008 and the round-2 replays)

Per ship, from the design (computed fresh from parts: the game recomputes
armor, it does not trust a stored value):

- **Initiative**: hull initiative + 1 per Battle Computer, 2 per Battle
  Super Computer, 3 per Battle Nexus; at most 63.
- **Weapon initiative** (per weapon slot): min(63, part initiative +
  token initiative).
- **Weapon range**: the part's range; +1 on a starbase (reach only; see
  Beams).
- **Computer %**: start `c = 0`; for each Battle Computer (20), Battle
  Super Computer (30), Battle Nexus (50) and Multi Contained Munition (10)
  item: `c += (100 − c)·v/100`.
- **Jammer %**: start `J = 10000`; for each item `J = J·f/100` with
  f = Langston Shell 95, Mega Poly Shell 80, Alien Miner 70, Multi
  Function Pod 90, Jammer 10/20/30/50 → 90/80/70/50. Jammer = 0 with no
  such item, else min(95, 100 − (J + 50)/100). A starbase's jammer is
  reduced by a quarter (`jam − jam/4`) (BINARY-ONLY).
- **Capacitor %**: `C = 1000`, `C = C·(100 + v)/100` per Energy Capacitor
  (v 10) or Flux Capacitor (20), at most 2550; capacitor % = C/10.
  CONFIRMED: 2 Flux Capacitors and 1 Energy Capacitor give 132%.
- **Deflector %**: `D = 1000`, `D = D·90/100` per Beam Deflector;
  deflector % = D/10 (100 = none).
- **Shields**: sum of shield values, + 50 per Fielded Kelarium, + 100 per
  Mega Poly Shell. Regenerating Shields (RS): × 7/5.
- **Armor**: hull armor + armor parts, + 65 per Croby Sharmor and
  Langston Shell, + 50 per Multi Cargo Pod. RS: each armor part counts
  half. CONFIRMED (CB-007): 2 Mole-skin → 70 shields; a Destroyer with
  2 Tritanium → armor 250.
- **Target class**:
  - 3 armed (any beam or torpedo);
  - 4 bomber;
  - 6 fuel transport (Fuel Transport and Super-Fuel Xport hulls);
  - 7 has cargo capacity;
  - otherwise 5 unarmed.

  Target-type matching: "armed" matches class 3. "Bombers and
  freighters" matches 4 or 7. "Unarmed" matches 5, 6 or 7. "Fuel
  transports" matches 6. "Freighters" matches 7. "Starbase" matches
  starbases. "Any" matches all.
- **Tactic and targets**: armed tokens take tactic, primary and secondary
  from the fleet's plan. Unarmed tokens use tactic 0 (disengage).
- **Speed code**:

  `w − 4 + jets + 2·overthrusters + Multi Function Pods
   + (Enigma Pulsars + Alien Miners + 1)/2 − (mass/70)/engines`

  - `+2` for War Monger.
  - `−1` if the fleet dumped cargo and the design has cargo capacity.
  - Clamped to 0..8.
  - `w` = 10 for Interspace-10, Enigma Pulsar, Trans-Star 10,
    Trans-Galactic Mizer Scoop and Galaxy Scoop. Otherwise it is the
    highest warp ≤ 9 whose fuel-table entry is at most 120.
  - Mass = design mass + the stack's share of the fleet's cargo (by cargo
    capacity).
  - CONFIRMED by the designer (CB-000, 32/32), without the battle-only
    terms (cargo, WM, dump).

### Starbases in battle

- A starbase token has 1 ship, never moves, and is placed whenever its
  owner is involved, armed or not. CONFIRMED: CB-003/004 S1, CB-005,
  CB-011..013.
- **LEGACY BUG**: a starbase is always class 3 "armed", even when it has
  no weapons. So "unarmed" targets never match it, and "armed" or "any"
  do. CONFIRMED (CB-011..013 S4/S5, Q-4): frigates with primary
  "unarmed" and no secondary did not fire at an unarmed station; with
  primary "armed" they destroyed it.
- A starbase ignores plan 0 for targeting. It always uses primary any,
  secondary any, and tactic 5. CONFIRMED (CB-016, Q-3).
- Its existing damage carries into the battle as `units` with
  `pct = 100`.
- A planet whose starbase fought gets the "starbase fought" condition for
  repair (see Repair).

## Rounds

At most 16 rounds, numbered 0..15. Each round (BINARY-ONLY ordering,
consistent with every replayed record):

1. From round 1 on, regenerate shields (see RS).
2. The battle ends if at most one player still has live tokens.
3. Movement (below).
4. Each live token draws a fresh jitter `rand(15)`.
5. A player with no live token it is allowed to attack is out of the
   battle. The battle ends if at most one player is left.
6. Firing (below).

### Moves per round (CONFIRMED, CB-000..CB-008; P-7)

A token with speed code `s` gets `(s + 2)/4` moves in round `r`, plus 1 when:

- `s % 4 = 0` and `r` is even;
- `s % 4 = 1` and `r % 4 ≠ 2`;
- `s % 4 = 3` and `r % 4 = 0`.

The average is `(s + 2)/4` squares per round (½ … 2½). For example,
code 1 moves 1, 1, 0, 1 and code 5 moves 2, 2, 1, 2.

### Movement order (BINARY-ONLY)

Movement runs in three phases, `a = 3, 2, 1`. In phase `a`, every token
with at least `a` moves left moves one square.

Inside a phase, tokens go in **descending jittered weight**:
`W = mass + mass·(j − 7)·2/100`, where `j` is the token's current jitter
(0..14). Ties keep token order. Starbases never move.

### Disengaging (CONFIRMED, P-10, CB-003/004 D)

- A tactic-0 token has a counter that starts at 7. Each move it makes
  lowers the counter by 1. A move when the counter is 0 takes it off the
  board, so it leaves on its 8th move. It is then out of the battle,
  not destroyed.
- "Disengage if challenged" (tactic 1) becomes tactic 0 with a fresh
  counter of 7 the first time the stack takes armor damage (shield-only
  hits do not count). It keeps firing until it leaves.

### Choosing a square (BINARY-ONLY in general; CONFIRMED for one mover vs a station, CB-012 and CB-019)

For each single-square move, the token computes a **radius** and possibly
a **goal**:

1. Its **attackable enemies** are live tokens of players in its attack
   set. They must match its primary target type, or its secondary type
   if no live enemy matches the primary.
2. **Reach** = the token's longest weapon range + its moves left this
   round.
   - Tactic 3 or 5 uses the **shortest** weapon range instead when that
     is shorter than the longest. This is why tactics 3 and 4 end on
     different squares (CB-019).
3. For each attackable enemy, let `d` be its distance, plus 1 if that
   enemy has at least as many moves left as this token.
   - If some enemy has `d ≤ reach`, the radius is the token's moves left
     and there is no goal.
   - One exception applies when the token's longest range is exactly 3.
     An unshielded enemy then counts only if
     `d ≤ moves left + longest non-sapper beam range`, because sappers
     cannot hurt it.
4. Otherwise the radius is 1. The goal is the square of the nearest
   attackable enemy (by that `d`) that the token could damage. The first
   such enemy in token order wins ties. With no such enemy there is no
   goal.

Every square within the radius (and on the board) gets a score, described
below. **Lower is better.**

- Equal scores go to the square closer to the token, with no draw.
- Among equal scores at equal distance, the `k`-th such square found
  replaces the current pick when `rand(k) = 0`. Squares are scanned by
  `x` ascending, then `y` ascending.
- A goal, if there is one, replaces the pick.

If the pick is more than one square away, the token steps one square
toward it, using the scores of its 8 neighbours:

- If |dx| = |dy|, it takes the diagonal step, with no draw.
- If the pick is straight along a row or column, it takes the lowest of
  the three neighbours facing that way. Ties are broken by
  `rand(number tied)`, in scan order.
- Otherwise it compares the diagonal step with the straight step along
  the longer axis (y when |dy| ≥ |dx|). The lower score wins; on a tie,
  `rand(2) = 0` gives the diagonal.

A step that would leave the board leaves the token where it is.

### Square score (BINARY-ONLY)

The score of square `q` for token `T` is computed as follows:

1. For each live enemy `E` in `T`'s attack set, at distance `d` from `q`,
   consider the distances `E` could choose:
   - just `d` if `E` has fewer moves left than `T`;
   - otherwise `max(0, d − 1)` up to the farthest square of `E`'s
     3×3 neighbourhood from `q` (clipped to the board).
2. At each distance `x`:
   - `take(x)` = `E`'s estimated damage to `T` at `x`.
   - `give(x)` = `T`'s estimated damage to `E` at `x`, or 0 if `E` does
     not match `T`'s current target type.
3. `E` picks the `x` that is best for it: lowest
   `tacticScore(E's tactic, give = take(x), take = give(x))`, the later
   `x` on ties.
4. Over all enemies: `GIVE` = the **largest** `give` and `TAKE` = the
   **sum** of `take`, each at the distance its enemy picked.
5. Score = `tacticScore(T's tactic, GIVE, TAKE)`.

`tacticScore(tactic, give, take)`:

| tactic | score |
|---|---|
| 0, 2 | `take` |
| 1, 5 | `−give` |
| 3, 4 | `take` if `give = 0`, else `min(−1, −give·100/(take + 1))` |

Tactics 3 and 4 have the same score; they differ only through the reach
rule above. Tactic 0 adds 2 per token of its own player on `q`, and
subtracts 1 when `q` is its current square.

**Damage estimate** from attacker `A` to target `B` at distance `x`:

- Without "ignore range": 0 if `x` > `A`'s longest range.
- "Ignore range" is used for `take` when `T`'s tactic is 0.
- Otherwise, for each weapon slot that reaches (`x ≤` part range, +1 for
  a starbase), or every slot when ignoring range:

**Beam slot.** `v = damage × count`, then:

1. `× capacitor/100`.
2. If `x > 0`: `v = v + (x·v)/(−10)/r`. Here `r` includes the starbase
   +1, unlike real fire.
3. `× B's deflector/100`.
4. A sapper is capped at `B`'s shield per ship × `A`'s ships.
5. Out of reach (only when ignoring range):
   `v = max(count, v/(x + 10 − r))`.
6. The slot adds `A's ships × v`.

**Torpedo slot.** Simulate `N = ships × count × 200` torpedoes:

1. `H` = the hits that the salvo rule gives for `N`.
2. Estimate = `damage·H/200`.
3. If `B` has shields, add `damage·(N − H)/1600`.
4. Out of reach: the same division as for beams.
5. The slot adds the estimate.

**Cap.** Without "ignore range", the total is at most `B`'s toughness:
`(armor + shields)·ships`, less its existing damage (at least 1).

## Firing (CONFIRMED by replay: CB-001..CB-019, every hit record)

For each initiative level from the highest to the lowest weapon
initiative present:

- Tokens act in **reverse token order**, while at least two players are
  still in the battle.
- A token fires each of its weapon slots whose weapon initiative equals
  the level.
- The slot's `N = ships × count`.

**Eligible targets** are tokens that:

- are live;
- belong to a player in the firer's attack set;
- are within the slot's reach (part range, +1 on a starbase);
- match the firer's primary target type, or the secondary type if no
  target matches the primary.

### Target choice (CONFIRMED, CB-009 K4–K7, Q-6)

The firer picks the eligible target with the highest attractiveness. The
first in token order wins ties, and a score of 0 is never chosen.

**Cost.** Take the target design's current cost (resources + boranium)
× ships.

- Multiply by 100 if that is below 100000. Otherwise use 10^7.
- The cost reflects the owner's discounts and miniaturization
  (BINARY-ONLY).

**Toughness.**

- `A` = armor × ships, minus existing damage, at least 1. The existing
  damage is computed as `units·armor/10`, then `·pct/10`, then
  `·ships/500`, truncating after each division.
- `S` = shield × ships.

**Beams.** Cost × the target's deflector/100, then:

- normal beam: `cost·100/(A + S + 1)`, at least 1;
- sapper: 0 if `S < 1`, else `ceil(cost·100/S)`.

**Torpedoes.** Let `a` be the accuracy after jammer `j` and computer `c`:

- if `c < j`: `a = acc − (j − c)·acc/100`;
- otherwise: `a = acc + (c − j)·(100 − acc)/100`.

This is the hit chance below without its minimum of 1. Score 0 if
`a ≤ 0`. Otherwise:

- `X = A·200/a`;
- `Y = S·100/(a/2 + (100 − a)/8)`;
- `Z = (A − Y·a/200)·100/(m·a)`, where `m` = 2 for missiles, else 1;
- `eff = min(X, Y + Z)`;
- score = `cost/eff`, at least 1; 0 if `eff ≤ 0`.

CONFIRMED consequences (CB-009):

- A 5-ship stack is chosen before a 3-ship stack of the same design.
- The more expensive design is chosen at equal armor.
- An already damaged stack is chosen before a fresh one.
- The lower token index is chosen between identical stacks.

### Beams (CONFIRMED, CB-001, CB-002, CB-010..CB-016; P-12, P-14, Q-7)

`R = ships × damage × count`. Repeat:

1. Choose a target.
2. `dp = R × capacitor/100 × target deflector/100`.
3. If the distance `x > 0`, `dp = (100 − x·10/range)·dp/100`.
   - `x·10/range` is an integer, so a range-3 weapon loses 3% at
     distance 1, 6% at 2 and 10% at 3.
   - **`range` is the part's own range, without the starbase +1.** So a
     Laser Station hits at 80% at distance 2 (CB-011..013, CB-016).
4. Apply `dp` to the target (Damage). A sapper hits shields only.
5. If the target died and damage `L` is left over, the next target
   receives `R' = min(R − 1, R·L/dp)`, recomputed from step 1 (deflector
   and dropoff again). Otherwise the slot is done. CONFIRMED (CB-010):
   59 of 59 hits; carrying `L` itself mismatched 8.

**Gatling** (Gatling Gun, Mini Gun, Gatling Neutrino Cannon; CONFIRMED,
CB-002, CB-003, CB-005; P-13):

- One shot hits **every** eligible target in token order.
- Each target takes `ships × damage × count × capacitor/100 × that
  target's deflector/100`.
- No range dropoff and no carry-over.

**Sappers** (CONFIRMED, CB-002; P-15): damage shields only. They make no
hit on a target without shields.

### Torpedoes and missiles (CONFIRMED, CB-001, CB-002, CB-009; P-17..P-21, Q-8, Q-14)

Missiles are Jihad, Juggernaut, Doomsday and Armageddon. The other
torpedo parts are torpedoes.

**Hit chance `p`** from accuracy `acc`, firer computer `c` and target
jammer `j`:

- if `c > j`: `p = 100 − (100 − (c − j))·(100 − acc)/100`;
- otherwise: `p = acc·(100 − (j − c))/100`;
- in both cases at least 1.

**Hits `H` out of `N` torpedoes:**

- if `p ≥ 100`, all hit;
- if `N > 200`, `H = N·p/100` exactly, with no random draw. CONFIRMED
  only for `N = 202` (CB-001: 90/125/103/72 hits; identical across
  reruns);
- otherwise each torpedo hits on `rand(100) < p`: `N` draws.

Per salvo, while torpedoes remain:

1. Choose a target. Let `d` = the part's damage. `d` is doubled for a
   missile against a target with total shields < 1. CONFIRMED (CB-002,
   P-20).
2. **Decide how many torpedoes this target takes** (`n`):
   - If the target has at least `N` ships, or `H·d` is at most its
     remaining armor `A`, then `n = N`, with `H` hits and `N − H`
     misses.
   - Otherwise `n` is the smallest value from `ships` to `N` for which
     the damage is enough. With:
     - `hits = ceil(n·H/N)`;
     - `misses = n − hits`;
     - `S' = max(0, S − misses·d/8)`;
     - `armorDmg = hits·d/2` (or `hits·d − S'` when `S' < hits·d/2`);

     the condition is `armorDmg ≥ A`.
3. **Misses** do `misses·d/8` to shields only. They are recorded only
   against a target with shields. CONFIRMED (CB-009 K8, Q-14): 14 Beta
   misses did 21.
4. **Hits** do `hits·d/2` to shields first. A further `hits·d/2` goes
   to armor directly; shield damage that gets past the shields is added
   to it.
5. **One kill per torpedo**: hits kill at most `n` ships, and any
   damage left after that limit is lost. CONFIRMED (CB-009 K1, Q-8): 202
   Jihads killed 202 ships per salvo with armor for 272.
6. `N −= n`; continue with the next target.

## Damage (CONFIRMED by replay; P-16, P-22, P-23, Q-7)

Applying `dp` (and, for torpedoes, an armor-only part `extra`) to a ship
stack with per-ship shield `s`, stack shield `S = s·ships`:

1. **Shields.**
   - If `S > dp`: `s = (S − dp)/ships`, `dp = 0`.
   - Otherwise: `dp −= S`, `s = 0`.
   - Shield-only damage against `S = 0` does nothing and is not
     recorded.
2. If nothing is left for armor, stop.
3. **Armor.** `dp += extra`.
   - A tactic-1 stack becomes tactic 0 with counter 7.
   - Let `damaged = max(1, ships·pct/100)` and
     `per = max(1, units·armor/500)`.
4. **Kills.** Already-damaged ships die first, at `armor − per` each.
   Then the others die at `armor` each, while `dp` suffices (and the kill
   limit allows).
5. **Spread** over the survivors when `dp` remains:
   - If some survivors were already damaged: `dp = ceil((dp +
     damagedLeft·per)/survivors)`.
   - Otherwise: `dp = dp/survivors` (rounded down).
   - At least 1 either way.
   - Then `units = ceil(dp·500/armor)` (1..499) and `pct = 100`. Every
     surviving ship is now equally damaged.
6. With no `dp` left: `pct = ceil(damagedLeft·100/survivors)`, `units`
   unchanged.
7. **Leftover** for beam carry: whatever `dp − extra` remains, only when
   the whole stack died.

**Starbases** (CONFIRMED in part, CB-011..015, Q-5):

- `total = dp + extra + units·armor/500`.
- If `total < armor`, `units = total·500/armor`, at least one step more
  than before. CONFIRMED: an unarmed Space Station with 400 shields went
  through 90, 190, … 490 per 500, then died at the next hit.
- Otherwise the starbase is destroyed. The planet no longer has one, and
  ships and packets queued for building there are lost (BINARY-ONLY).
- Destroying an Alternate Reality race's starbase leaves the planet
  uninhabited (BINARY-ONLY).

**Regenerating Shields** (CONFIRMED, CB-007/008, 39 hits): at the start
of each round after the first, a token whose shields are above 0 regains
`max/10`, up to its maximum. A token whose shields reached 0 never
regenerates.

## Random draws in a battle

What a battle draws, in order. All draws are uniform.

1. **Setup:** one `rand(15)` jitter per ship token, as the token is
   created. Starbase tokens draw none.
2. **Shuffle:** `rand(n − i)` for `i = 0..n−1`.
3. **Each round:**
   - movement draws: square-choice and step ties (see "Choosing a
     square");
   - a `rand(15)` jitter per live token;
   - one `rand(100)` per torpedo in each salvo of ≤ 200 torpedoes.
4. **Square scores:** in the original these can also draw, because the
   torpedo estimate simulates `ships × count × 200` torpedoes. That is
   exactly 200 for a single ship with one torpedo in the slot, which
   goes down the random path (BINARY-ONLY quirk; Elegy can compute the
   expected value instead).
5. **After the battle:** tech-learning attempts (below); salvage with no
   minerals (below).

Beam damage, gatlings, kills, damage spread and salvos of more than 200
torpedoes draw nothing.

`MEASURED` in the original: with the stream pinned, reruns of the same
file give byte-identical battle records (`PARITY.md`, round 2 method),
and one-mover battles replay square by square from these rules
(CB-012, CB-019).

## After the battle

### Salvage (CONFIRMED, CB-001 B1; CB-011..013 S6/S7, Q-13)

Per kill event, per mineral: a third of the destroyed ships' design
mineral cost (× ships), plus their share of the fleet's cargo, or all of
it if the fleet died. Then:

- **At a planet:** the planet's surface gains `× 8/10` if it has a
  starbase, else `× 5/10`. No salvage object is created.
- **In deep space:** a quarter is lost (`S − S/4`). The rest goes into
  one salvage object per battle, capped at 30000 kT. If all minerals of
  a new salvage object would be 0, each gets `rand(10)` (BINARY-ONLY,
  inferred to be a token amount).

### Repair (CONFIRMED, CB-017, 10 locations × 2 turns; Q-12)

Repair happens later in the same turn as battles. A fleet that fought this turn gets no repair.
Otherwise each damaged stack's `units` drop by `r + f` per turn (to 0 if
smaller), and `pct` is kept:

| Fleet situation | r |
|---|---|
| moved this turn | 5 (BINARY-ONLY) |
| stationary in deep space | 10 |
| orbiting a planet it does not own | 15 |
| at its own planet with no starbase, or whose starbase fought this turn | 25 |
| at its own planet with a starbase without a dock (Orbital Fort) | 40 |
| at its own planet with a dock (Space Dock or larger) | 100 |

- Interstellar Traveler doubles `r` (BINARY-ONLY).
- `f` = 50 if the fleet has a Super-Fuel Xport, else 25 if it has a Fuel
  Transport, else 0. `f` is added to every stack.
- A starbase that did not fight this turn repairs 50 units (IS 75)
  (BINARY-ONLY).

### Tech from battle (CONFIRMED in part, CB-018, Q-11)

Destroyed designs raise the battle's "seen" tech in each field to their
tech requirements.

A tech attempt, for one player:

1. If the player has already gained from a battle this turn, nothing
   happens and no draws are made.
2. `rand(100)`; below 50, nothing happens.
3. Up to 13 tries. Each try draws `rand(13)` for a Mystery Trader item.
   The item is given if:
   - it appeared among the destroyed ships with some chance `c`;
   - the player does not have it;
   - `rand(100) < c`.

   A success ends the attempt.
4. Otherwise up to 6 tries of `rand(6)` for a field. The first field
   where the player's level is below the seen level gains research equal
   to the **cost of its next level**. Under slow tech that is half the
   doubled cost, i.e. the normal cost. This ends the attempt.
5. A success (step 3 or 4) marks the player as having gained this turn.

With no trader items in play and exactly one field behind, the chance is
`½ · (1 − (5/6)^6) ≈ 0.33` per attempt.

Research gained this way raises the level **in the same turn**: research
level-ups are processed after battles. CONFIRMED (CB-018): with weapons 3
and 0% research, 4 of 6 distinct random streams ended the turn at
weapons 4, and 2 stayed at 3. The accumulators read 0, and the control
without a battle stayed at 3.

Who makes an attempt (BINARY-ONLY in detail):

- In a two-player battle with two tokens, each participant makes an
  attempt when the battle was in deep space, at an unowned planet, or at
  its own planet. This includes a participant that lost nothing and
  destroyed nothing. Not at another player's planet.
- In larger battles, participants make an attempt under the same
  location rule, and probably only when ships other than their own were
  destroyed; this condition is not fully settled.
- A player that is not in the battle makes an attempt when the battle was
  at its own planet.

## Open experiments

Round 3 (stars-decomp `docs/combat-predictions.md` R-8..R-10) is being
run; results will update the statuses above.

- **R-8**: CB-019 repeated at six pinned streams for tactics 3, 4 and 5.
  It tests the reach rule, the square tie rules and tactic 5 closing to
  short range, square by square.
- **R-9**: tech from battle at the defender's own planet (station vs
  frigates), exact per stream. It tests the attempt condition at a planet
  and the draw order after a battle.
- **R-10**: plan 0 "player B" after a lone B fleet earlier in the turn.
  It tests the LEGACY BUG's predicted one-player battle.

Not yet tested:

- the movement order by jittered weight, and any battle with several
  moving tokens on both sides (e.g. a CB-018 replay);
- three or more players, start squares for `n ≠ 2`, and friends joining;
- the token cap;
- the tech-attempt condition in larger battles, and for players outside
  the battle;
- Mystery Trader items from battle;
- queued ships lost with a starbase; AR starbase loss;
- the "moved" repair rate, starbase repair, IS repair;
- salvage at more than one point; dump cargo;
- War Monger and cargo in the speed code.

The dampener mass question (19 vs 23) is closed: 19 is the game's value
(`PARITY.md`, "Resolved reconciliation").

## Sources

- Oracle: CB-000..CB-019 (`PARITY.md` "Combat", `experiments/cbNNN/`),
  with raw records in private `stars-oracle-apparatus` (`evidence/cb/`,
  `evidence/cb2/`).
- White-box readings: private `stars-decomp` (combat notes, prediction
  rounds P, Q and R, the hit replay checker and the one-mover replay that
  reproduce the CB observations listed above).
