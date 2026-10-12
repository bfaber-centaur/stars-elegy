# CB-055: does target choice use a dropped part's cost?

`COMBAT.md` "Parts the game drops from a design": the cost of a design
with a part its hull slot does not take is computed before the part is
dropped in the year the game first reads the design, and without it from
the next year. CB-054 confirmed this for salvage. This case tests target
choice, which uses the same cost (`COMBAT.md` "Target choice").

Combat Lab base, deep space at (1020,1230), mutual enemies, tech 26 in
every field for both players.

- Player 1 has two designs, armor 25 each and no shields:
  - `Deflector Hauler`: Small Freighter, Quick Jump 5, Beam Deflector in
    the shield-or-armor slot (dropped when read). Cost (resources +
    boranium) 8 in the year the design is read, 6 after.
  - `Tank Hauler`: Small Freighter, Quick Jump 5, Fuel Tank. Cost 7.
- Player 0 has one frigate, plan "Max Any"; the freighters use plan
  "Nobody".
- `y1`: the frigate starts at the freighters (battle in year 1). `y2`: it
  starts 40 ly away at warp 5 (battle in year 2, from the original's own
  year-1 output).
- `-a`: the Deflector Hauler is fleet 0 and the Tank Hauler fleet 2. `-b`:
  the reverse, so token order cannot decide the result.

## Predictions (pushed before the runs)

From Elegy's model (elegy #160, e35c871, merged as 5c63346; extended with the
fleet orders before the runs in the private apparatus): the frigate's
first shot targets the Deflector Hauler in `y1` and the Tank Hauler in
`y2`, in both fleet orders.

## Round 1: one ship each, Laser frigate (`cb055-*.spec`)

Cycles 20000, 30000, 50000. **Undecided.** At every shot exactly one
freighter was within the Laser's range of 1, so target choice never had
two candidates: the fleeing freighters' moves decided which one was hit.
The first target was the Tank Hauler at 20000 and the Deflector Hauler at
30000 and 50000, the same in all four setups of a stream.

## Round 2: stacks of 15, Colloidal Phaser frigate (`cb055r2-*.spec`)

The frigate carries a Colloidal Phaser (range 3), and each freighter
fleet is 15 ships, so both stacks are more likely to be in reach at the
first shot. Both stack costs scale by 15 and both armor terms are
25 × 15: the Deflector Hauler stack is worth 120 in year 1 and 90 in year
2, the Tank Hauler stack 105. Only a battle's first shot counts, and only
when both stacks are in reach; after a hit, the damaged stack's lower
armor term favours it. Predictions for round 2 were pushed before it ran.

Cycles 20000, 30000, 50000, 12000, 40000 (20 battles):

| setup | first shot with both stacks in reach | battles |
|---|---|---|
| `y1-a` | Deflector Hauler | 5 of 5 |
| `y1-b` | Deflector Hauler | 4 of 4 (at 50000 the Tank stack was out of reach) |
| `y2-a` | Tank Hauler | 5 of 5 |
| `y2-b` | Tank Hauler | 4 of 4 (at 50000 the Tank stack was out of reach) |

- **CONFIRMED (18 of 20 battles; the other 2, `y1-b` and `y2-b` at
  cycles 50000, had the Tank stack out of reach at the first shot):** target choice uses the
  design cost with the dropped part in the year the game first reads the
  design, and without it from the next year. In each battle the first
  shot came in round 4 with both stacks at distance 3.
- The `y2` setups had no battle in year 1, and their year-1 host files
  held `Deflector Hauler` without the Beam Deflector (mass 29).
- Every battle's salvage object was written with the skip-decay mark set
  (`OBJECTS.md` "Salvage"). The salvage amounts depend on which ships each
  stream destroyed and are not part of the result.
- Raw evidence: apparatus `evidence/cb055` (private).
