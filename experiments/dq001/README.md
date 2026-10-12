# DQ-001: the client's saved default template and the default-queue record

`ORDERS.md` "The player's default queue" (#158) says the original client
compares its own saved default production template with the player's
stored default when it saves an order file, and adds the default-queue
record (block type 46) carrying the template when they differ. RG-002
showed only the empty case. This case runs all three outcomes, with a
colony founded in the same year.

The predictions were pushed to the private apparatus (`evidence/dq001`,
35b976a, 17:39:52Z) before any run. The raw files are in that directory
too. How the client's template is stored stays private; this record says
only what the template held.

## Setup

Combat Lab base, `dq001.spec`:
- Player 0 (human) has the game default queue auto mines 10, auto
  factories 10, leftover off.
- A Colony Ship with 25 kT of colonists starts 40 ly north of unowned
  planet 19, at warp 5 with a colonize task there.

Steps:
1. A settle year (2400 → 2401, pinned, no orders) gives the player's file.
   The ship is then 15 ly away.
2. The original client opens that file and saves with no orders
   (`tools/fleetlab/client-orders`, with `CLIENT_INI` setting the client's
   template).
3. Year 2 (2401 → 2402, pinned) runs with that order file. The ship
   arrives and colonizes.

Variants of the client's saved template:
- **A:** none.
- **B:** equal to the game default.
- **C:** auto defenses 10, leftover on.

## Results (all as predicted)

| Variant | Record in the order file | Player 0 default after year 2 | Planet 19 after year 2 |
|---|---|---|---|
| A | empty (no items, leftover off) | empty, leftover off | colonized, empty queue |
| B | none | auto mines 10, auto factories 10, leftover off | colonized, queue auto mines 10, auto factories 10 |
| C | auto defenses 10, leftover on | auto defenses 10, leftover on | colonized, queue auto defenses 10 |

Status: CONFIRMED, one run per variant. Two more runs saved without a
template, through a driver mistake, and behaved as A. So the record is
applied before colonization in the same year. The client wrote no other
order in any variant. The new colony's leftover setting is not shown in
the files read.
