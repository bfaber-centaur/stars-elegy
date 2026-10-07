# Combat specification

This file states the J-RC3 battle rules as behavior: who fights, how the
board is set up, how tokens move, choose targets and fire, how damage is
applied, and what happens after a battle (salvage, repair, tech). It is
written for an implementer who works only from this public repository.

`PARITY.md` "Combat" holds the experiment records (CB-000..CB-022) these
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
3. **The procedure** (BINARY-ONLY in its details; CONFIRMED where
   marked). For one location:
   1. **Present set `P`**: the owner of a starbase at the location's
      planet, armed or not, plus the owner of every fleet at the location.
   2. **Attack sets** start empty. Each player has one.
   3. **Starbase plan 0.** If the starbase is armed and its owner's battle
      plan 0 (the default plan) has attack-who "enemies" or "neutrals and
      enemies", the owner's set gets every player the owner considers an
      enemy (or neutral or enemy). Plan 0 "everyone" or "a named player":
      see the LEGACY BUG below.
   4. **Aggressor fleets**, in location order, add to their owner's set:
      - "enemies": every player the owner considers an enemy;
      - "neutrals and enemies": every player it considers neutral or enemy;
      - a named player: that player;
      - "everyone": the set is **replaced** by all players except the
        owner.

      These sets may name players who are not present; only present
      players matter below.
   5. If there is no aggressor fleet, there is no battle (rule 2).
   6. **Attacked set `Q`** = every present player named in some player's
      attack set. If `Q` is empty, there is no battle.
   7. **Retaliation**: one pass over the players in player-number order.
      For player `i`: if `i`'s set names someone in `Q`, add `i` to `Q`.
      Then, if `i` is in `Q`, add to `i`'s set every player whose set names
      `i`. CONFIRMED: a stack whose plan attacks nobody fires back once a
      battle has started (CB-002, CB-009; P-6).

      The pass covers **every player in the game, present or not**, and
      so do the sets read in step 6 (BINARY-ONLY).
      - Steps 3 and 4 only fill the sets of present players. So an absent
        player's set can be non-empty only through the plan-0 LEGACY BUG,
        when X is a player of the game who is not at this location.
      - Then X joins `Q` and counts toward `n`, which shifts the start
        squares. X has no tokens, though, so it takes no part in the
        fighting.
   8. **Friends**: passes over the location's fleets, in order, until a
      pass changes nothing. For a fleet whose owner `p` is in `P` but not
      in `Q`, rebuild `p`'s set as the union of the sets of `p`'s friends
      that are in `Q`, taken in player order. If a friend is already named
      in the set being built (two of `p`'s friends fight each other), the
      set becomes empty and the rebuild stops. Then:
      - if the set is empty, `p` leaves `P` and only observes;
      - otherwise `p` joins `Q`.
4. **Who is in the battle.** The battle happens when `Q` is non-empty
   after these steps.
   - The battle's **player list is `P`**: every fleet of a player in `P`
     and the starbase of a starbase owner in `P` become tokens.
   - The **number of involved players `n` is the size of `Q`**.
   - Normally `Q` and `P` coincide and `n ≥ 2`. But a starbase owner with
     no fleet at the location is never visited by step 8. So it stays in
     `P` (its starbase is a token) even when it attacks nobody and nobody
     attacks it. Then `P` is larger than `Q`.
   - The plan-0 LEGACY BUG can make `n = 1`, and a battle still happens
     (CB-022).
   - CONFIRMED for an unarmed starbase whose owner is involved: it is a
     token (CB-005, CB-011..013 S4/S5).
5. **Starbases join, never start.** CONFIRMED (CB-011, Q-1): player 1's
   armed fleet attacked "enemies" while player 1 considered player 0
   neutral. Player 0's Laser Station had plan 0 "enemies", and a battle
   happened in which the station fired. There was no battle with an
   unarmed station, with an unarmed visitor, or with plan 0 "nobody".
6. **During the battle**, a player's attack set is the one these steps
   produced. It does not change.
7. **Token cap.** At most 256 tokens (BINARY-ONLY).
   - If the involved fleets need more, each player gets a quota of
     `255 / players` stacks, and fleets beyond their quota are left out.
   - Then left-out fleets are added back while room remains.
   - Players with a left-out fleet are told that some fleets missed the
     battle.
8. **Excluded fleets** (BINARY-ONLY): a fleet carrying a particular
   status flag is not grouped with the others. What sets that flag is not
   known.

### LEGACY BUG: plan 0 "everyone" or "a named player" at a starbase (CONFIRMED, CB-011..013, CB-022)

When the starbase's owner (A) has plan 0 attack-who **"everyone" or a
named player**, step 3 writes the attack set into the set of another
player, X, instead of A's. Plan 0 "enemies" and "neutrals and enemies"
work as intended.

What is written into X's set:

- "everyone": X's set is **replaced** by all players except A. If
  X ≠ A, this includes X itself and does not include A.
- "player i": player i is **added** to X's set.

X depends on what the game examined just before this location in the same
turn:

- **Player 0**, if the previous location examined had a battle.
- **The owner of the last fleet in that location's fleet order**, if it had
  no battle. For a lone fleet, X is that fleet's owner.
- **Not determined** for the first location examined in a turn. The value
  is left over from earlier processing. In CB-022 "no lone fleet" (two
  random streams) it was neither 0 nor 1. An X that is not a player in the
  game has no effect: plan 0 then contributes nothing.

Step 4 for X's own aggressor fleets runs after this. An "everyone" fleet of
X replaces X's set.

Observable consequences with two players: A owns the starbase, and B visits
with an aggressor fleet that attacks "enemies" while B considers A neutral.

| X | plan 0 "everyone" or "player B" | Status |
|---|---|---|
| A | A attacks B: an ordinary battle, the same as "enemies" | CONFIRMED (CB-012 three streams, CB-013; the previous location had a battle) |
| B | B's set names only B among the present players. `Q = {B}`, `n = 1`, `P = {A, B}`: a **one-player battle** | CONFIRMED for "player 1" and for "everyone", byte-identical records (CB-022, two streams each) |
| not a player of the game | no battle: nobody's set names a present player | MEASURED (CB-022 "no lone fleet", "player 1"; two-player game) |
| C, a player of the game who is not present | C's set names B (or, for "everyone", every player but A). So `Q = {B, C}` and `n = 2`. B attacks C back, but C has no tokens. Squares come from `n = 2` (A rank 0 at (1,4), B rank 1 at (8,5)), and the battle ends after round 0's movement with no shots | BINARY-ONLY |

The one-player battle runs as an ordinary battle with `n = 1`:

- **Squares.** Start squares come from the flattened table (see Start
  squares). A (rank 0) gets (4,4) and B (rank 1) gets (1,4).
- **Round 0.** B's armed stack has no attackable enemy (its only target is
  itself), so it stays where it is. A's set is empty, so A is out after
  the movement phase, and the battle ends.
- **Result.** The record has no movement or fire actions (CB-022).

Like any battle, it uses the setup draws and one round's jitter draws, and
the fleets count as having fought for repair (BINARY-ONLY for these
side effects).

## Board setup

### Start squares (CONFIRMED for two players, CB-001..CB-021)

The board is 10×10. Each player in the battle's player list `P` has one
start square, and all of that player's tokens, starbase included, start on
it. The square is chosen by the player's rank in `P` (lowest player number
first, from 0) and by `n`, the number of involved players (the size of
`Q`). Read the table below row after row as one flat list; the square is
entry `n(n−1)/2 + rank`. When `P` has more players than `Q`, the rank runs
past row `n` into the next row. CONFIRMED for `n = 2` (CB-001..CB-021) and
for `n = 1` with two players in `P`: (4,4) and (1,4) (CB-022). BINARY-ONLY
for other `n`.

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
  The product runs over every item, so two Flux Capacitors in one slot
  count twice. CONFIRMED only for one Flux and one Energy Capacitor (in
  different slots): 132% (CB-002 C4, the "Cap DD"). Several of one kind
  is BINARY-ONLY: 2 Flux + 1 Energy would give 158%.
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
5. Players are checked in player-number order. A player is out of the
   battle when its attack set names no player that is still in. Only the
   attack set counts, not target types. A player removed earlier in the
   same check no longer counts for later players. The battle ends if at
   most one player is left.
   - A player's set can name itself, which only happens through the
     plan-0 LEGACY BUG. That self-entry counts in this check, and only
     here.
   - Targeting, movement scores and firing always skip the token's own
     player's tokens, whatever its set says.
   - In the one-player battle the self-entry keeps B in while A drops
     out. The battle then ends either way, so the outcome matches CB-022
     (BINARY-ONLY).
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

### Choosing a square (BINARY-ONLY in general; CONFIRMED for one mover vs a station, CB-012, CB-019, CB-020, CB-021)

For each single-square move, the token computes a **radius** and possibly
a **goal**:

1. Its **attackable enemies** are live tokens of players in its attack
   set. They must match its primary target type, or its secondary type
   if no live enemy matches the primary.
2. **Reach** = the token's longest weapon range + its moves left this
   round.
   - Tactic 3 or 5 uses the **shortest** weapon range instead when that
     is shorter than the longest. This is why tactics 3 and 4 end on
     different squares (CB-019, CB-020).
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

1. For each live token `E` of a player in `T`'s attack set, at distance
   `d` from `q`, consider the distances `E` could choose. `E`'s own attack
   set is not consulted: `E` counts even if it would not attack `T`.
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

## Firing (CONFIRMED by replay: CB-001..CB-021, every hit record)

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

**Cost.** Take the target design's current cost (resources + boranium,
see "Design cost") × ships.

- Multiply by 100 if that is below 100000. Otherwise use 10^7.

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

### Design cost (BINARY-ONLY)

A design's cost is computed for its owner, in four components (resources,
ironium, boranium, germanium). It is the hull's cost plus, for each slot,
`count ×` that part's cost. For the hull and each part:

1. Start from the part's base cost.
2. **Miniaturization.**
   - Let `m` be the smallest of `level − requirement` over the six fields
     in which the part has a requirement above 0.
   - If the part has no requirement, `m` is the owner's lowest level in
     any field.
   - If `m > 0`, let `d = 4·min(m, 19)`, at most 75. With Bleeding Edge
     Technology, `d = 5·min(m, 19)`, at most 80.
   - Each nonzero component `c` becomes `c − round(c·d/100)`, rounding
     halves up, and at least 1.
3. **Race.** The first case that matches applies, and no other:
   - Interstellar Traveler, stargates: `c − c/4`.
   - War Monger, beams, torpedoes and bombs: `c − c/4`.
   - Inner Strength, beams, torpedoes and bombs: `c + c/4`.
   - Cheap Engines, engines: `c − c/2`.
4. **Bleeding Edge Technology.** If `m ≤ 0` and the part has a
   requirement, every component is doubled. One game-wide flag, not
   identified, suppresses this.

Divisions truncate. The only oracle evidence is indirect: target choice
among designs of different cost in CB-009 (Humanoid JOAT at tech 26).

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

**Hits `H` out of `N` torpedoes.** `H` is computed afresh for each target
the salvo reaches. `N` is the number of torpedoes still unfired, and `p`
uses that target's jammer. With `N ≤ 200`, each target therefore gets its
own `N` draws.

- if `p ≥ 100`, all hit;
- if `N > 200`, `H = N·p/100` exactly, with no random draw. CONFIRMED
  only for `N = 202` (CB-001: 90/125/103/72 hits; identical across
  reruns);
- otherwise each torpedo hits on `rand(100) < p`: `N` draws.

Per salvo, while torpedoes remain:

1. Choose a target, then compute `H` for it. Let `d` = the part's
   damage. `d` is doubled for a
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
   - If the stack has no damage (`units = 0`): `damaged = 0`, `per = 0`.
   - Otherwise `damaged = max(1, ships·pct/100)` and
     `per = max(1, units·armor/500)`.
   - CONFIRMED by CB-001 B3: 90 Beta hits on one undamaged 3650-armor
     Hulk record 148/500. Counting a phantom damaged ship would give 149.
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
  than before. CONFIRMED (CB-011..013 S5):
  - The unarmed Space Station has 400 shields and 500 armor. The first
    hit came at distance 1 (90% dropoff) for 90, then 100 per hit.
  - Shields took 90 + 100 + 100 + 100.
  - The fifth hit put its last 10 into shields and 90 into armor (90/500).
  - Then 190, 290, 390 and 490; the next hit (total 590) destroyed it.
- Otherwise the starbase is destroyed. The planet no longer has one, and
  ships and packets queued for building there are lost (BINARY-ONLY).
- Either way, **no damage is left over** after a hit on a starbase. A
  beam stops there, even after destroying it (BINARY-ONLY).
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
4. **Square scores:** in the original these can also draw. The torpedo
   estimate simulates `ships × count × 200` torpedoes, which is exactly
   200 for one ship with one torpedo in the slot. Then the estimate makes
   200 `rand(100)` draws, so it is random, and it shifts later draws
   (BINARY-ONLY quirk). The expected value `200·p/100` is the natural
   deterministic replacement. It differs from the original only in that
   one case.
5. **After the battle:** tech-learning attempts (below); salvage with no
   minerals (below).

Beam damage, gatlings, kills, damage spread and salvos of more than 200
torpedoes draw nothing.

`MEASURED` in the original: with the stream pinned, reruns of the same
file give byte-identical battle records (`PARITY.md`, round 2 method),
and one-mover battles replay square by square from these rules
(CB-012, CB-019, CB-020, CB-021).

## After the battle

### Salvage (CONFIRMED, CB-001 B1; CB-011..013 S6/S7, Q-13)

Per kill event, per mineral: a third of the destroyed ships' design
mineral cost (× ships), plus the destroyed ships' share of the fleet's
cargo. The share is computed as follows (BINARY-ONLY):

- If the whole fleet died, the share is all of the fleet's cargo.
- Otherwise the cargo moved is `C · Σ lost ships·cargo capacity /
  Σ ships before·cargo capacity`, with `C` the fleet's total cargo.
- That amount is split per mineral as `cargo_i · moved / C` (truncated).
  Any remainder goes 1 kT at a time over ironium, boranium, germanium
  and colonists, one pass, only to types still holding cargo.
- Only minerals become salvage. The lost ships' share of fuel and
  colonists is destroyed.

Then:

- **At a planet:** the planet's surface gains `× 8/10` if it has a
  starbase, else `× 5/10`. No salvage object is created.
- **In deep space** (BINARY-ONLY in detail): a quarter is lost
  (`S − S/4`).
  - The rest goes into this battle's salvage object. Every kill event
    in the battle adds to it.
  - No salvage object is placed exactly on a planet's position.
  - If all three minerals of an addition are 0, each becomes `rand(10)`.
    This is redrawn until the total is above 0.
  - **The 30000 kT limit** is counted in 10 kT steps: an object holds at
    most 3000 steps, and adding `m` kT of one mineral uses `ceil(m/10)`
    steps. When an addition happens, the object's existing minerals are
    taken out and re-added with the new ones. Minerals are added in the
    order ironium, boranium, germanium.
  - A mineral that does not fit fills the object to exactly 3000 steps
    with `10 × free steps` kT of that mineral. A **new salvage object**
    is then created at the same position.
  - The remainder of that mineral is added in a new pass (ironium,
    boranium, germanium again) into the new object, and so are the
    minerals not yet added. Nothing is lost to the limit, and nothing is
    split proportionally.

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

### Tech from battle (CONFIRMED in part, CB-018, CB-021, Q-11)

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

Research gained this way raises the level **in the same turn**. After
battles, the post-movement waypoint phase checks research level-ups a
second time (`KERNEL.md`, "Turn order", step 6).

CONFIRMED (CB-018): with weapons 3 and 0% research, 4 of 6 distinct
random streams ended the turn at weapons 4, and 2 stayed at 3. The
accumulators read 0, and the control without a battle stayed at 3.

CONFIRMED per stream (CB-021, R-9): a station defending its owner's
homeworld against three frigates. The gain came in exactly the three
streams predicted from this draw order, and the frigates' squares
matched in all six.

Who makes an attempt (BINARY-ONLY in detail):

- In a two-player battle with two tokens, each participant makes an
  attempt when the battle was in deep space, at an unowned planet, or at
  its own planet. This includes a participant that lost nothing and
  destroyed nothing. There is no attempt at another player's planet.
  CONFIRMED by the exact replays: CB-021 (the attacker at the defender's
  planet makes no attempt) and the round-2 CB-012 chain (a player that
  lost nothing at its own planet does attempt).
- In larger battles, participants make an attempt under the same
  location rule, and probably only when ships other than their own were
  destroyed; this condition is not fully settled.
- A player that is not in the battle makes an attempt when the battle was
  at its own planet.

## Open experiments

Round 3 (R-8 to R-10, CB-020..CB-022) is done. Every prediction held
except the R-10 "everyone" control, which the LEGACY BUG section now
explains.

Not yet tested:

- the movement order by jittered weight, and any battle with several
  moving tokens on both sides (e.g. a CB-018 replay);
- the plan-0 value X on the first location of a turn (not 0 or 1 in
  CB-022; unexplained), and a starbase owner in the player list but not
  involved (start-square rank past row `n` with `n ≥ 2`);
- design-cost race adjustments and Bleeding Edge doubling;
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

- Oracle: CB-000..CB-022 (`PARITY.md` "Combat", `experiments/cbNNN/`),
  with raw records in private `stars-oracle-apparatus`.
- White-box readings: private `stars-decomp` (combat notes, prediction
  rounds P, Q and R, the hit replay checker and the one-mover replay that
  reproduce the CB observations listed above).
