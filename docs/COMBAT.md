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

## Battle plans

A player has between 1 and 16 battle plans, numbered 0..15 without gaps.
The client stops at 15: its copy button does nothing once a player has
15 plans (MEASURED twice as BP-L in the BP-1..BP-2 client runs; the host
kept 15). A 16th plan reaches
the host only through crafted orders (BINARY-ONLY).
Each plan has a name and the fields listed under "Conventions". Every
fleet names one of its owner's plans. A starbase always fights with its
owner's plan 0.

**Starting plans** (MEASURED, UG01..UG21: every player of every new game,
2 to 16 players, single-human and multi-human). Every player starts with
the same five plans:

| plan | name | tactic | primary | secondary | attack-who | dump cargo |
|---|---|---|---|---|---|---|
| 0 | Default | 4 maximize damage ratio | 3 armed ships | 1 any | neutrals and enemies | no |
| 1 | Kill Starbase | 4 maximize damage ratio | 2 starbase | 3 armed ships | neutrals and enemies | no |
| 2 | Max-Defense | 3 maximize net damage | 3 armed ships | 4 bombers and freighters | neutrals and enemies | no |
| 3 | Sniper | 1 disengage if challenged | 5 unarmed ships | 0 none | neutrals and enemies | no |
| 4 | Chicken | 0 disengage | 1 any | 0 none | neutrals and enemies | no |

Starting fleets use plan 0 (`UNIVERSE.md`). A ship built into a new fleet
also gets plan 0 (MEASURED: CB-047-ctl, 2 runs, and over 40 new fleets in
the round-7 ship-launch runs, `PARITY.md` "Round 7"; BINARY-ONLY in
general).
Ships split off keep their source fleet's plan (`ORDERS.md`).

**"Default" always attacks "neutrals and enemies"** (MEASURED: UG01..UG21
in fresh runs, and BP-2, three single-player games created one after
another in one client session). The original's plan setup also has a
rule that sets "Default" to "everyone" in a single-human game, but it
reads a game setting that every way of creating a game clears first, so
it never takes effect (BINARY-ONLY reading). Elegy has no such rule.

**Adding, replacing and deleting** (CONFIRMED for deletion, BP-1;
BINARY-ONLY otherwise). Validation of the fields is in `ORDERS.md`
("Battle-plan fields").

- A definition for an existing plan number replaces that plan.
- A new plan takes the next number (the current count). The 17th plan is
  refused.
- A definition whose number is beyond the next free one (above the
  current count) is refused. The order is dropped and the plans are
  unchanged (BINARY-ONLY).
- Deleting plan `k` moves every later plan down by one number. Every
  fleet of that player whose plan number is `k` or higher has it lowered
  by one. So a fleet on a later plan keeps the same plan, and a fleet on
  the deleted plan moves to the plan just before it, `k − 1` (BP-1: with
  plans 0..6 and fleets on 3, 5, 2 and 6, deleting plan 3 left six plans
  and the fleets on 2, 4, 2 and 5, the later plans keeping their fields).
  The client
  asks for confirmation first when some fleet uses plan `k`. It never
  offers to delete plan 0.

**Order validation** (BINARY-ONLY unless marked; Elegy's choices for
values only crafted orders can carry are marked "Elegy").

- **Plan limit.** The host holds at most 16 plans, because the plan
  number in an order has room only for 0..15. The client stops at 15
  (MEASURED, BP-L in the BP-1..BP-2 client runs). Elegy enforces the
  host's 16; the 15 is a client limit.
- **Fields the host checks.** The host refuses a tactic above 6 and a
  primary or secondary target above 8. So 6 and 8, one past the legal
  sets (tactics 0..5, target types 0..7), get through. Elegy refuses
  anything outside the legal sets, as `ORDERS.md` states for
  battle-plan fields.
- **Attack-who is not checked.** The host stores any value the order
  carries (0..31). The client offers only nobody, enemies, neutrals and
  enemies, everyone, and each other player in the game; it never offers
  the player itself or a player who is not in the game. In battle a
  named player is the value minus 4.
  - A plan naming a player who is not in the game attacks no one through
    that choice: no such player is ever present.
  - A plan naming its own owner marks that owner as its own target.
    Tokens never fire at their own side, but how this mark enters the
    choice of who fights at a location was not traced.
  - Elegy refuses both.
- **Names.** The client limits a plan name to 31 characters and checks
  nothing else (an empty name is not refused; inferred from the dialog).
  The host stores the name the order carries with no length or content
  check. Its plan record has room for 31 characters, so a longer crafted
  name overruns it. Elegy refuses a name longer than 31 characters.

## Where battles happen in the turn (CONFIRMED in part; see each rule)

Battles are fought after movement and production, at the start of the
post-movement waypoint phase (step 6 of the turn order in `KERNEL.md`):
before bombing, before the post-movement unload/load tasks, mine sweeping
and repair. Repair later in the same turn skips every fleet that fought.

- After production: a starbase destroyed in battle loses the ship items
  of its queue, but a ship built that year still fights (CONFIRMED,
  CB-047).
- Before bombing: a starbase destroyed in this year's battle no longer
  protects its planet from the same year's bombing (CONFIRMED, T-2).
- Before the second research level-up check: research gained from a
  battle becomes a level in the same year (CONFIRMED, CB-018, CB-021).
- Before repair, which skips fleets that fought (CONFIRMED, CB-017).
- The order relative to the unload/load tasks and mine sweeping is
  BINARY-ONLY.

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
   least one beam weapon or torpedo; bombs do not count). CONFIRMED (CB-005, CB-006):
   - No battle when both sides attack nobody (CB-005, P-5).
   - No battle when the only side that attacks enemies is unarmed
     (CB-006).
2. **Only fleets start battles.** With no aggressor fleet at the location
   there is no battle, whatever the starbase there is armed with or its
   plan says. CONFIRMED: six lone-starbase configurations (CB-002 C9/C10,
   CB-003 S2, CB-004 S2, CB-006 both planets) and the Q-1 controls
   (CB-011..014 S2/S3).
3. **The procedure** (BINARY-ONLY in its details; the steps confirmed
   by oracle cases are marked). For one location:
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

      CONFIRMED (CB-033): a player that only considered a participant a
      friend joined the battle with that friend's set.
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
7. **Token cap** (CONFIRMED, CB-039 and CB-042..CB-044: exact token
   counts and left-out fleets, two streams each). At most 255 tokens.
   - Count the stacks of every fleet of a player in `P`, plus 1 for a
     starbase token. If that is at most 255, everything fights.
   - Otherwise each involved player gets a quota of `255 / n` stacks
     (integer division; `n` is the size of `Q`). The starbase counts
     toward the total but not toward its owner's quota.
   - **First pass**, over the location's fleets in this order: the
     location's first fleet (the lowest by owner, then fleet number),
     then all the others from the highest to the lowest (by owner, then
     fleet number). A fleet joins, with all its stacks, if its owner's
     count plus its stacks is at most the quota. Otherwise it is left
     out, and the pass goes on to the next fleet.
   - **Second pass**, only if the total is below 255, in the same order:
     each left-out fleet whose stacks still fit (total plus its stacks at
     most 255) is added back whole.
   - CB-039 (140 one-ship fleets each, `n = 2`, quota 127): player 0's
     first fleet, then player 1's fleets 139..12 and player 0's fleets
     139..14 joined. That is 254 stacks; the second pass added player 1's
     fleet 12, for 255. Player 0's fleets 1..13 and player 1's fleets
     0..11 sat out.
   - CB-042 (three players with 100 one-ship fleets each, quota 85): 85
     each, for 255. Player 0's fleets 1..15 and players 1 and 2's fleets
     0..14 sat out.
   - CB-043 (at player 1's planet with an armed Orbital Fort; 140 and 131
     fleets, one of them with three designs): 127 stacks each plus the
     Fort. Player 0's fleets 1..13 and player 1's fleets 0..5 sat out.
   - CB-044 (CB-039 with player 1's fleet 12 holding two designs): 255
     tokens, 127 and 128. Player 1's fleet 12 sat out and fleet 11
     fought.
   - Players with a left-out fleet are told that some fleets missed the
     battle, except in a 2-player battle, where neither player is told
     (LEGACY BUG, CONFIRMED: CB-039 left 25 fleets out with no message;
     in the three-player CB-042 each player with left-out fleets was
     told). Elegy reproduces this behind its legacy-bug switch; the
     message is 0x180 in `MESSAGES.md`.
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
- **Not determined** for the first location examined in a turn
  (BINARY-ONLY). The value is left over from earlier processing, so the
  binary alone does not fix it. In CB-022 "no lone fleet" (two random
  streams) it was neither 0 nor 1. In CB-035, a 16-player game, it was
  never a player of the game in 36 of 36 runs, with and without other
  fleets and moving fleets elsewhere. When X is not a player, the write
  lands outside the attack sets, and no effect of it was observed.
  - **Elegy's chosen rule:** at the first location of a turn, plan 0
    "everyone" or "a named player" contributes nothing.

CONFIRMED for the previous-location rule: X = 3 after a battle-less
location whose last fleet was player 3's (CB-035-prev3), and X = 0 after a
location with a battle (CB-035-prevbattle).

Step 4 for X's own aggressor fleets runs after this. An "everyone" fleet of
X replaces X's set.

Observable consequences with two players: A owns the starbase, and B visits
with an aggressor fleet that attacks "enemies" while B considers A neutral.

| X | plan 0 "everyone" or "player B" | Status |
|---|---|---|
| A | A attacks B: an ordinary battle, the same as "enemies" | CONFIRMED (CB-012 three streams, CB-013; the previous location had a battle) |
| B | B's set names only B among the present players. `Q = {B}`, `n = 1`, `P = {A, B}`: a **one-player battle** | CONFIRMED for "player 1" and for "everyone", byte-identical records (CB-022, two streams each) |
| not a player of the game | no battle: nobody's set names a present player | MEASURED (CB-022 "no lone fleet", "player 1"; two-player game. CB-035, 16 players, 36 runs) |
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

### Start squares (CONFIRMED for one to six involved players)

The board is 10×10. Each player in the battle's player list `P` has one
start square, and all of that player's tokens, starbase included, start on
it. The square is chosen by the player's rank in `P` (lowest player number
first, from 0) and by `n`, the number of involved players (the size of
`Q`). Read the table below row after row as one flat list; the square is
entry `n(n−1)/2 + rank`. When `P` has more players than `Q`, the rank runs
past row `n` into the next row. CONFIRMED for `n = 2` (CB-001..CB-021) and
for `n = 1` with two players in `P`: (4,4) and (1,4) (CB-022), for
`n = 3` (CB-031, CB-032, CB-034), `n = 4` and `n = 6` (CB-036) and
`n = 5` (CB-033). CONFIRMED for a rank past row `n` (CB-036: an
uninvolved starbase owner with `n = 2` took (1,4), the involved players
(8,5) and (4,1)).

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

### Setup steps (BINARY-ONLY except as marked; dump cargo CONFIRMED, CB-025)

For each involved fleet, in location order:

1. The fleet is marked as having fought: it gets no repair this turn.
2. If its plan has "dump cargo" and it carries any minerals, all three
   minerals are dumped (CONFIRMED, CB-025, at a planet and in deep space).
   Colonists and fuel stay aboard.
   - At a planet, the planet's surface gains the full amount; the
     `× 8/10` and `× 5/10` factors of "Salvage" do not apply.
   - In deep space, the full amount goes into this battle's salvage
     object, with no quarter lost. The dump happens at setup, before any
     ship is destroyed, so it is the first addition to that object. The
     object then exists even if nobody is destroyed. Kill events add to
     it afterwards as described in "Salvage".
3. One token is created per design with ships in the fleet.

A starbase token is placed for the starbase of an involved owner (see "Starbases in battle").

Then the token order is shuffled: for `i = 0..n−1`, swap token `i` with
token `i + rand(n − i)` (CONFIRMED by the exact replays CB-041, CB-042,
CB-044, CB-046 and CB-048..CB-051; see "Random draws in a battle").
Token order matters for movement ties, firing
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
- **Tactic and targets**: primary and secondary come from the fleet's
  plan. Only an armed token (class 3) takes the plan's tactic; every
  other class (bomber, unarmed, fuel transport, freighter) uses tactic 0
  (disengage), whatever the plan says. A token with no weapons also has
  its primary target set to none, so it scores against its secondary.
  MEASURED (CB-049, 6 streams): an unarmed Medium Freighter stack under
  a plan with tactic 3, primary any, secondary none is recorded with
  tactic 0, primary none, secondary none, and its moves replay with those
  values. BINARY-ONLY for the other classes.
- **Speed code**:

  `w − 4 + jets + 2·overthrusters + Multi Function Pods
   + (Enigma Pulsars + Alien Miners + 1)/2 − (mass/70)/engines`

  - `+2` for War Monger.
  - `−1` if the fleet dumped cargo and the design has cargo capacity.
  - Clamped to 0..8.
  - `w` = 10 for Interspace-10, Enigma Pulsar, Trans-Star 10,
    Trans-Galactic Mizer Scoop and Galaxy Scoop. Otherwise it is the
    highest warp ≤ 9 whose fuel-table entry is at most 120.
  - Mass is per ship: design mass + `C · c / F`, truncated. `C` is the
    fleet's total cargo, `c` the cargo capacity of one ship of this
    design, and `F` the fleet's total cargo capacity. So a stack's share
    is spread over its ships (CONFIRMED, CB-038: 1 kT in a fleet of two
    Medium Freighters left each at mass 69, code 2; 1 kT in a one-ship
    fleet gave 70, code 1). A design without cargo capacity adds nothing.
  - CONFIRMED by the designer (CB-000, 32/32) without the battle-only
    terms. War Monger `+2` and the cargo term are CONFIRMED in battle
    (CB-038, six stacks, two streams; CB-045, two streams: a Medium and a
    Small Freighter sharing 140 kT weighed 174 and 69, and three Medium
    Freighters weighed 139 each with 212 kT and 140 with 213 kT, so the
    share is truncated per ship). The dump term is CONFIRMED by
    CB-025.

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
consistent with every replayed record; movement then the jitter draw,
steps 3 and 4, CONFIRMED by the exact replays (CB-041, CB-049 and others) under
"Choosing a square"):

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
   - This check only decides whether the battle ends now (CONFIRMED,
     CB-033: a player found out kept firing for 13 rounds).
     A player found out here keeps its tokens: they still fire in step 6
     and move next round. Nobody stays out: the check starts again from
     the players with live tokens every round.
   - This only shows when a player found out still has a target that is
     alive. While every attack set is symmetric (A names B exactly when
     B names A), a player found out can only name players with no live
     tokens, so it has nothing to fire at. Retaliation makes the sets
     symmetric; only a player that joins through friends (step 8 of the
     procedure) can name a player that does not name it back.
6. Firing (below).

### Moves per round (CONFIRMED, CB-000..CB-008; P-7)

A token with speed code `s` gets `(s + 2)/4` moves in round `r`, plus 1 when:

- `s % 4 = 0` and `r` is even;
- `s % 4 = 1` and `r % 4 ≠ 2`;
- `s % 4 = 3` and `r % 4 = 0`.

The average is `(s + 2)/4` squares per round (½ … 2½). For example,
code 1 moves 1, 1, 0, 1 and code 5 moves 2, 2, 1, 2.

### Movement order (CONFIRMED, CB-030; exact replays CB-041, CB-042, CB-044, CB-046)

Movement runs in three phases, `a = 3, 2, 1`. In phase `a`, every token
with at least `a` moves left moves one square.

Inside a phase, tokens go in **descending jittered weight**:
`W = mass + mass·(j − 7)·2/100`, where `j` is the token's current jitter
(0..14). Ties keep token order. Starbases never move.

The exact replays (see "Choosing a square") reproduced the order of every
move, including battles of 255 identical one-ship tokens where only the
jitter separates them.

### Disengaging (CONFIRMED, P-10, CB-003/004 D, CB-025, CB-034)

- A tactic-0 token has a counter that starts at 7. Each move it makes
  lowers the counter by 1. A move when the counter is 0 takes it off the
  board, so it leaves on its 8th move. It is then out of the battle,
  not destroyed.
- Every move the token is given counts, including one where it stays on
  its square (CONFIRMED, CB-034: six stays on one square, each with a
  move record, counter 6 … 1). The counter is lowered before the square is
  chosen, so the result of the move does not matter.
  - A lone tactic-0 token rarely stays put. Its own square scores `+2`
    for itself and `−1` for being current, a net `+1` worse than a
    neighbour with the same `TAKE`. A neighbour with the same score at
    the same distance is picked at random. So it stays only if every
    neighbour on the board has a `TAKE` at least 1 higher than its own
    square (a tie goes to the closer square, its own).
  - Out of an enemy's reach, `take` usually does not change with distance.
    The out-of-reach estimate is floored at the slot's count (see
    "Damage estimate"), and for most weapons the divided value is
    already below that floor a few squares out. Then every square away
    from the enemies scores the same, and the token walks to a random
    neighbour on each move, sometimes towards the enemies (CB-032: a
    Runner facing two stacks of 2 Laser Destroyers changed square on all
    8 moves in 6 streams). A Laser (`v = 20`, `r = 1`) is at the floor of
    2 for every `x ≥ 2`.
  - A stay therefore needs both a real per-square gradient and a square
    whose every neighbour is closer to some enemy: for example, the
    corner farthest from enemies in two different directions, where
    each enemy slot's divided estimate drops by at least 1 per square at
    those distances. Large torpedo stacks do this (torpedo estimates have
    no dropoff), as can neighbouring squares crowded by the token's own
    player. CB-034 used CB-032's squares with stacks of Delta
    Torpedo Destroyers whose target types missed the Runner, so they never
    moved: the Runner went to (9,9) and stayed there for six moves.
- "Disengage if challenged" (tactic 1) becomes tactic 0 with a fresh
  counter of 7 the first time the stack takes armor damage (shield-only
  hits do not count). It keeps firing until it leaves. CONFIRMED (CB-049,
  6 streams): the tactic-1 Shield DD stack switched at its first armor
  damage, its action records show the fresh counter from then on, and
  every later move replays as tactic 0. Without the switch,
  5 of the 6 replays fail. A starbase never switches (BINARY-ONLY).

### Choosing a square (CONFIRMED by exact replay, CB-041, CB-042, CB-044, CB-046, CB-049..CB-051; one mover CB-012, CB-019, CB-020, CB-021)

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

**Exact replays.** Every battle below was replayed from its random stream
with this section, "Square score", "Movement order" and the draws in
"Random draws in a battle"; shots were taken from the record. Every move
of every round came out on the recorded square, in the recorded order,
with every tie draw in place:

- CB-041 (40 runs): two movers, a tactic-5 Destroyer stack and tactic-0
  Super Freighters, against a Fort.
- CB-046 (40 runs): beam Destroyers against torpedo Destroyers and
  against shielded, armed Mini Morphs.
- CB-042 (2 streams): three mutually hostile players, 255 one-ship
  Laser Frigates, 2,032 moves and about 7,800 tie draws.
- CB-044 (2 streams): two players, 255 one-ship Laser Frigates, 1,611
  moves and about 8,700 tie draws.
- CB-049 (6 streams): seven moving stacks on tactics 1 to 4 (one
  becoming 0 under fire, one unarmed on 0), primary types that match
  some enemies and none, weapons of ranges 1, 3 and 4 on one design,
  sappers, capacitors, deflectors and shields; 133 moves and 579 tie
  draws.

To check that CB-049 exercises a rule, the replay was rerun with that
rule removed or changed, and counted how many of the 6 streams still
replay. These broke at least one stream, so each is CONFIRMED by it:

| changed rule | streams still replaying |
|---|---|
| no `rand(100)` draws inside the torpedo estimate | 0 |
| tactics 3 and 4 scored like tactic 2, or like tactic 5 | 0 |
| every enemy counted as matching the target type | 0 |
| no out-of-reach division | 0 |
| tactic 1 never switching to 0 | 1 |
| reach using the longest range for tactics 3 and 5 | 2 |
| no out-of-reach floor | 3 |
| no sapper cap | 3 |
| no capacitor or deflector | 4 |
| the range-3 exception counting sapper ranges | 5 |
| no range-3 / shielded-enemy exception at all | 5 |

CB-049 did not exercise two rules, so round 8 tested each with a setup
built for it, and every move replays (6 streams each):

- CB-050: the torpedo estimate's shield term. A shielded tactic-0 stack
  facing a Jihad Missile stack and an Upsilon Torpedo stack that cannot
  target it went to (9,9) and stayed for 7 moves. Without the term it
  would alternate between (9,9) and (8,9), which is what the unshielded
  control (CB-050-ctl) did.
- CB-051: the fallback from the primary to the secondary target type. A
  stack with primary "starbase" (none on the board) and secondary
  "armed ships" moved toward the enemy's armed stack from its first
  move; without the fallback it would never move. A "freighters, else
  any" stack switched to "any" once the freighter left, so the test is
  made again on every move.

### Square score (CONFIRMED by the exact replays CB-041 to CB-051 listed under "Choosing a square")

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
2. If `x > 0` and `r > 0`: `v = v + (x·v)/(−10)/r`. Here `r` includes
   the starbase +1, unlike real fire. With `r = 0` (a ship's range-0
   beam, reached only when ignoring range) there is no dropoff
   (BINARY-ONLY).
3. `× B's deflector/100`.
4. A sapper is capped at `B`'s shield per ship × `A`'s ships.
5. Out of reach (only when ignoring range):
   `v = max(count, v/(x + 10 − r))`.
6. The slot adds `A's ships × v`.

**Torpedo slot.** Simulate `N = ships × count × 200` torpedoes:

1. `H` = the hits that the salvo rule gives for `N`.
2. Estimate = `damage·H/200`.
3. If `B` has shields, add `damage·(N − H)/1600`.
4. Out of reach: the same division and floor as for beams,
   `max(count, estimate/(x + 10 − r))`.
5. The slot adds the estimate.

**Cap.** Without "ignore range", the total is at most `B`'s toughness:
`(armor + shields)·ships`, less its existing damage (at least 1).

The replays exercised every step above: the beam estimate
with capacitor, dropoff, deflector, sapper cap and the out-of-reach
division and floor; the torpedo estimate, including its random hits
(see "Random draws in a battle"); the cap with shields; the sum and
maximum over many enemies of two other players; the target-type test on
`give`; every row of the tactic table; the tactic-0 own-token and
current-square terms; and the torpedo shield term (CB-050).

## Firing (CONFIRMED by replay: CB-001..CB-021, every hit record)

For each initiative level from the highest to the lowest weapon
initiative present:

- Tokens act in **reverse token order**, while at least two players are
  still in the battle.
  - "Still in" here means having a live token; attack sets do not count
    (BINARY-ONLY). It is checked again before each token acts, so kills
    earlier in the round count. Once only one player has live tokens,
    no further token fires in this round and the battle ends after it.
    This changes nothing that can be observed: that player has no live
    enemy to fire at, and the next round would end the battle before
    anything is recorded.
  - Tokens of a player that round step 5 found out still act; they fire
    at whatever their own attack set allows.
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

- For a starbase token this is the starbase design's plain owner cost
  (CONFIRMED, CB-027). The starbase build-cost rule of `COMPONENTS.md` (ISB or
  AR `c − c/5`, then halved) applies only to what production charges;
  target choice does not use it.

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

### Design cost

A design's cost, for its owner, is its hull's cost plus `count ×` each
part's cost, in four components (resources, ironium, boranium,
germanium). Each hull and part cost is the owner cost of
[`COMPONENTS.md`](COMPONENTS.md), "Cost for an owner": miniaturization,
then the race adjustment, then Bleeding Edge Technology doubling, with
the base costs in `data/components.json`. That section is CONFIRMED
(CS-001) and is the rule to implement; it includes two cases this file
used to leave out:

- Bleeding Edge Technology never doubles terraform or planetary items.
- Claim Adjuster pays half the resources for terraform items.

In combat the design cost is used only for target choice ("Cost" above).
Oracle evidence from combat is indirect: target choice among designs of
different cost in CB-009 (Humanoid JOAT at tech 26). Colony-ship minerals
in TK T-30 (`TAKEOVER.md`, Colonization) match the base cost and
miniaturization exactly at tech 3 and 26, including the rounding of the
reduction.

### Beams (CONFIRMED, CB-001, CB-002, CB-010..CB-016; P-12, P-14, Q-7)

`R = ships × damage × count`. Repeat:

1. Choose a target.
2. `dp = R × capacitor/100 × target deflector/100`.
3. If the distance `x > 0` and the part's range is above 0,
   `dp = (100 − x·10/range)·dp/100`.
   - A range-0 beam (Blackjack, Bludgeon, Blunderbuss) has no dropoff
     (CONFIRMED, CB-026). On a starbase its reach is 1, and it hits at full
     damage at distance 1.
   - `x·10/range` is an integer, so a range-3 weapon loses 3% at
     distance 1, 6% at 2 and 10% at 3.
   - **`range` is the part's own range, without the starbase +1.** So a
     Laser Station hits at 80% at distance 2 (CB-011..013, CB-016).
4. Apply `dp` to the target (Damage). A sapper hits shields only.
5. If the target died and damage `L` is left over, the next target
   receives `R' = min(R − 1, R·L/dp)`, recomputed from step 1 (deflector
   and dropoff again). Otherwise the slot is done. CONFIRMED (CB-010):
   59 of 59 hits; carrying `L` itself mismatched 8. CB-042 (two
   three-player streams, 255 one-ship tokens): every hit replayed,
   including the carried hits. The carried amount belongs to that one
   shot; a token's next shot starts again from `R`.

**Gatling** (Gatling Gun, Mini Gun, Gatling Neutrino Cannon; CONFIRMED,
CB-002, CB-003, CB-005; P-13):

- One shot hits **every** eligible target in token order.
- Each target takes `ships × damage × count × capacitor/100 × that
  target's deflector/100`.
- No range dropoff and no carry-over.

**Sappers** (CONFIRMED, CB-002; P-15): damage shields only. They make no
hit on a target without shields.

### Torpedoes and missiles (CONFIRMED, CB-001, CB-002, CB-009, CS-003; P-17..P-21, Q-8, Q-14)

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

The draws are CONFIRMED by the CB-049 replay (6 streams). Each of its 87
torpedo targets got its hits from the stream, `N` draws for the
torpedoes still unfired, and the resulting misses matched every miss
record. In 4 salvos the torpedoes left after a kill went on to a second
target with fresh draws, and every later move stayed in step with the
stream.

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
3. **Misses** do `misses·d/8` to shields only, if that is above 0.
   CONFIRMED (CB-009 K8, Q-14): 14 Beta misses did 21. A target without
   shields left takes nothing from misses, and no miss record is written
   for it (CONFIRMED, CB-009, 2 runs: salvos with 163 and 172 misses on
   an unshielded stack wrote no miss record, and every hit replays).
4. **Hits.** Let `h = hits·d/2`, truncated once for the whole group of
   hits. `h` goes to shields first, and a further `h` goes to armor
   directly; shield damage that gets past the shields is added to it. The
   total is therefore `2·h`, which is 1 less than `hits·d` when
   `hits·d` is odd. CONFIRMED (CS-003-C2): one Alpha Torpedo hit
   (`d = 5`) did 4.
   - A hit record is written for every target the salvo reaches, even
     with 0 hits. A 0-hit record changes nothing (CONFIRMED once, CB-049:
     the 0-hit record after a miss record left the target as it was). This
     accounts for the no-change records with flag 0x80 that CS-003-C2
     saw on an unshielded target, one per missed shot (7 for the Alpha
     Torpedo, 12 and 11 for the missiles). They are hit records, not
     miss records.
   - A torpedo hit record carries the miss records' flag 0x80 exactly
     when it does no armor damage, which means 0 hits. On a
     shielded target an all-miss salvo therefore writes two 0x80
     records on that target: the miss record first, then the 0-hit hit
     record. CONFIRMED (CB-049): reading the first as the hit record
     drops the misses' shield damage, which is what made one later
     cycles-7000 hit look wrong; read in this order, every CB-049 hit
     replays.
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
- Otherwise the starbase is destroyed. The planet no longer has one.
  Ship items in its production queue are removed; planetary items
  stay (CONFIRMED, CB-047, two streams: a queue of 50 Destroyers
  then 20 factories kept only the factories, while the control without
  attackers kept both). Production comes before battles, so a ship built
  that year still fights. Packets queued there are lost too
  (BINARY-ONLY).
- Either way, **no damage is left over** after a hit on a starbase. A
  beam stops there, even after destroying it. CONFIRMED (CB-052, 6
  streams): a one-slot phaser stack put 234 into an Orbital Fort with 100
  armor. Its fire action held only the Fort's record, though an enemy
  stack sat on the same square in range; that stack was first hit by the
  next round's shot. CB-041 agrees with a 2-point overkill.
- Destroying an Alternate Reality race's starbase leaves the planet
  uninhabited (CONFIRMED, CB-041: 17 of 17 streams).

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
   (CONFIRMED quirk, CB-049: the replays fail in all 6 streams without
   these draws). The expected value `200·p/100` is the natural
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

The order of draws 1 to 3 is CONFIRMED by the exact replays (CB-041,
CB-042, CB-044, CB-046, CB-048..CB-051). Each run's stream was located
from its setup draws alone: the recorded starting jitters and the
shuffled token order. Every movement tie, jitter and torpedo draw after
that fell in place, round after round, including the estimate's draws
in item 4.

## After the battle

### Battle record (CONFIRMED, CB-031)

The battle record goes to every player in the battle's player list `P`
(the players with tokens on the board) and to no one else. A player that
was present only as an observer gets no record. CB-031-obs: in 12
streams the observer's file held no record of the battle.

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
- Fuel is shared the same way, but by **fuel capacity**: the fleet
  loses `F · Σ lost ships·fuel capacity / Σ ships before·fuel capacity`
  (truncated), with `F` the fleet's fuel (CONFIRMED, CB-023). Fuel capacity is
  the design's: hull fuel plus fuel tanks and similar parts.
  - `F` is the fuel the fleet holds when the battle is fought: after this
    year's movement and refuelling, including what fuel transports and
    fuel generators added that year (`KERNEL.md`, "Turn order", steps 3
    to 6). CONFIRMED (CB-023): Fuel Transports raised a fleet from 600 to
    1000 before its battle, and the share of 1000 matched the observed
    207.
- Each kill event takes its share from what the fleet holds at that
  moment, so a fleet hit several times loses a share each time.
- Only minerals become salvage. The lost ships' share of fuel and
  colonists is destroyed.

Then:

- **At a planet:** the planet's surface gains `× 8/10` if it has a
  starbase, else `× 5/10`. No salvage object is created.
- **In deep space** (BINARY-ONLY in detail; the 30000 kT overflow
  CONFIRMED, CB-040): a quarter is lost
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
    split proportionally. CB-040: 36098 kT of ironium and 50 kT of
    germanium went into one object of 30000 ironium (3000 steps) and a
    second of 6098 ironium and 50 germanium.

### Repair (CONFIRMED, CB-017, 10 locations × 2 turns; Q-12)

Repair happens later in the same turn as battles. A fleet that fought this turn gets no repair.
Otherwise each damaged stack's `units` drop by `r + f` per turn (to 0 if
smaller), and `pct` is kept:

| Fleet situation | r |
|---|---|
| moved this turn | 5 (CONFIRMED, CB-024) |
| stationary in deep space | 10 |
| orbiting a planet it does not own | 15 |
| at its own planet with no starbase, or whose starbase fought this turn | 25 |
| at its own planet with a starbase without a dock (Orbital Fort) | 40 |
| at its own planet with a dock (Space Dock or larger) | 100 |

- Inner Strength doubles `r`; `f` is not doubled (CONFIRMED, CB-024).
- `f` = 50 if the fleet has a Super-Fuel Xport, else 25 if it has a Fuel
  Transport, else 0. `f` is added to every stack.
- A starbase that did not fight this turn repairs 50 units, or 75 for
  Inner Strength (CONFIRMED, CB-024).

### Tech from battle (CONFIRMED in part, CB-018, CB-021, Q-11)

Destroyed designs raise the battle's "seen" tech in each field to their
tech requirements.

A tech attempt, for one player:

1. If the player has already gained from a battle this turn, nothing
   happens and no draws are made.
2. `rand(100)`; below 50, nothing happens.
3. Up to 13 tries. Each try draws `rand(13)` for a Mystery Trader item
   index `k`. If item `k` has a chance `c > 0` in this battle and the
   player does not have it, a second draw `rand(100)` is made, and
   `rand(100) < c` gives the item. A success ends the attempt. Otherwise
   (including `c = 0` or an item already owned, which make no second
   draw) the next try follows. The chances are under "Mystery Trader
   chances" below.
4. Otherwise up to 6 tries of `rand(6)` for a field. The first field
   where the player's level is below the seen level gains research equal
   to the **cost of its next level**. Under slow tech that is half the
   doubled cost, i.e. the normal cost. This ends the attempt.
5. A success (step 3 or 4) marks the player as having gained this turn.

With no trader items in play and exactly one field behind, the chance is
`½ · (1 − (5/6)^6) ≈ 0.33` per attempt.

**Mystery Trader chances** (CONFIRMED, CB-048: 20 streams and a 12-stream
control, `PARITY.md` "Round 7"; consistent with CB-046 per stream,
below). Every item's chance is 0 when the battle starts. Each
time a hit destroys at least one ship of a token, every slot of that
token's design that holds a Mystery Trader part adds the slot's part count
to that item's chance, up to 25 (`c = min(25, c + count)`). So the chance
counts kill events, not ships killed, and a design reaches 25 only after
several kill events or with many parts. The hull never counts, so the
Mystery Trader hulls never get a chance in battle. The item indices `k`:

| `k` | item | `k` | item |
|---|---|---|---|
| 0 | Multi Cargo Pod | 7 | Multi Contained Munition |
| 1 | Multi Function Pod | 8 | (a hull: never in battle) |
| 2 | Langston Shell | 9 | Enigma Pulsar |
| 3 | Mega Poly Shell | 10 | (a hull: never in battle) |
| 4 | Alien Miner | 11 | Jump Gate |
| 5 | Hush-a-Boom | 12 | (a hull: never in battle) |
| 6 | Anti Matter Torpedo | | |

With chances `c_k`, one attempt gains an item with probability about
`½ · (1 − (1 − Σc_k/1300)^13)`; at most 25 per item keeps this small.

CB-046 (36 streams): six Destroyers with two Anti Matter Torpedoes each
died in four kill events (chance 8), and three armed Mini Morphs with
five Mystery Trader part types died in two (chances 6, 2, 2, 2 and 4).
No item was gained in any stream. Every move of these battles was
replayed from its stream, and the draws after each battle predict no item
in all 36: where the gate passed, every `rand(100)` for a chanced item
was at or above its chance. The closest draws were 7 for the Enigma
Pulsar (chance 4), 10 for the Multi Function Pod (2) and 11 for the Multi
Cargo Pod (6). So chances of 8, 11 and 12 or more for those items are
ruled out. Counting ships killed instead of kill events (chances 6, 3
and 9) is not. The `cb046-bio` control (the same 12 battle streams with
the attacker at biotechnology 3) gained biotechnology in exactly the two
streams the replay predicts (12000 and 50000 cycles), which pins the
attempt's place in the stream. So the observations agree with these
rules but do not yet show a nonzero chance working.

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

Who makes an attempt (BINARY-ONLY in detail). After the battle, every
player of the game is considered once, in player-number order, so the
draws come in that order.

- **Participants** (players in the battle's player list):
  - Location rule: only when the battle was in deep space, at an
    unowned planet, or at the participant's own planet. There is no
    attempt at another player's planet. CONFIRMED by CB-021 (the
    attacker at the defender's planet makes no attempt).
  - When `n = 2` (two involved players), only a participant that still
    has something after the battle (a ship, or its starbase alive). A
    participant that lost nothing and destroyed nothing does attempt.
    CONFIRMED by the round-2 CB-012 chain (a player that lost nothing at
    its own planet). A wiped-out participant makes no attempt:
    CONFIRMED by CB-029 (12 of 12 streams). A participant whose starbase
    was destroyed but whose ships survived does attempt (CB-041, a
    non-AR owner at its own planet: replayed per stream, below).
  - When `n` is not 2 (one involved player, or three or more), every
    participant makes an attempt, whatever it lost or destroyed.
    CONFIRMED by CB-031-n3 (a wiped-out player gained in 5 of 12 streams).
  - If the battle destroyed an Alternate Reality starbase, no
    participant makes an attempt. CONFIRMED by per-stream replay
    (CB-041): every move of every CB-041 battle with Super Freighters
    was reproduced from its random stream (40 runs, 12 distinct
    streams per race). The draws after each battle predict the JOAT
    owner's result in all 12 streams: one gain, in the one stream where
    the predicted draws succeed. In 4 of the 9 AR streams where the Fort
    died, an attempt would have gained, and the AR owner gained in none.
  - Nothing is destroyed in some of these battles; the attempt still
    makes its draws (step 2 onwards), and the field step then finds no
    field behind.
- **Players not in the battle:**
  - A player makes an attempt when the battle was at its own planet.
  - **LEGACY BUG (CONFIRMED, CB-031-obs, CB-037).** Otherwise, the game means to give an
    attempt to observers: players present at the location but not in the
    battle, and the owner of a planet there without a starbase. That
    owner's bit is in the observer set even when the owner is also a
    participant (CONFIRMED, CB-037-owner); a participant never gets the observer
    attempt itself, but its bit still counts for other players. It tests
    the player's **number** against the observer set instead of the
    player's bit: player `i` qualifies when `i AND observers ≠ 0`, where
    `observers` has bit `j` set for observer `j`. Player 0 never
    qualifies; player 1 qualifies when player 0 is an observer, player 2
    when player 1 is, player 3 when player 0 or 1 is, and so on. A
    qualifying player also needs a fleet at the location. The location
    rule does not apply here. CB-037: with observers {1, 2, 3}, player 1
    never gained in 8 streams while players 2 and 3 did; player 3 gained
    with observers {1, 3} (the owner's bit) and never with {3}.

## Open experiments

Rounds 3 to 6 (CB-020..CB-047) are done. Every rule they tested is
tagged with its result. The misses were the predictions, not the rules:
CB-032 (explained under "Disengaging"), the CB-035 retaliation
prediction, the CB-038 two-ship stack, the CB-039 total and split, the
CB-041 JOAT control (chance, per the replay), and CB-046 (no Mystery
Trader item; the chances were small and the replay predicts no gain in
every stream). The one CB-042 hit per stream that did not replay was a
checker defect (it reused an earlier shot's carried amount), not a rule.

Round 7 (CB-048, CB-049) confirmed Mystery Trader items from battle
(10 of 20 streams gained, the one-fleet control 1 of 12, and the replay
named exactly the gaining streams and items) and the movement rules for
tactics 1 to 4 with mixed designs (every move in 6 streams). The one
CB-049 hit that did not replay was again a checker defect (record
pairing; see "Torpedoes and missiles").

Round 8 (CB-050, CB-051) confirmed the torpedo estimate's shield term
and the fallback to the secondary target type. The battle-plan runs
confirmed deletion (BP-1), measured the client's 15-plan limit (BP-L),
and found "Default" never set to "everyone" (BP-2; see "Battle plans").

Not yet tested:

- the exact plan-0 value X at the first location of a turn (only that it
  was never a player; Elegy's chosen rule is above);
- salvage at more than one point;
- the host's 16-plan limit, which needs crafted orders.

The firing live-token recheck has no observable effect (see "Firing").

The dampener mass question (19 vs 23) is closed: 19 is the game's value
(`PARITY.md`, "Resolved reconciliation").

## Sources

- Oracle: CB-000..CB-022 (`PARITY.md` "Combat", `experiments/cbNNN/`),
  with raw records in private `stars-oracle-apparatus`.
- White-box readings: private `stars-decomp` (combat notes, prediction
  rounds P, Q and R, the hit replay checker and the one-mover replay that
  reproduce the CB observations listed above).
