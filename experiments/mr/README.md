# MR-1: following a fleet that its owner merges away the same year

Question: player A's fleet has a waypoint aimed at player B's fleet F, and
B merges F into another fleet Y at F's spot in the same year. Is A's order
applied, and what does A's fleet end up chasing? `ORDERS.md` "Targets
that moved, died or were captured", in its item on a fleet target merged
away during order replay, says (BINARY-ONLY) that the order
is never rejected, that the outcome is reached by one of two paths
depending on which player's orders are replayed first, and that either
way the follower normally ends up chasing Y.

**Replay order.** In a freshly started host run of a two-player game,
player 0's orders are replayed first (BINARY-ONLY: the shuffle's one
real draw is Random(2) on the stream's first value, and that value is
even for every seed). So one start covers both paths:

- at S1 the follower is player 0's, so the follower's order is replayed
  before the merge;
- at S2 the owner is player 0, so the merge is replayed before the
  follower's order.

**Setup.** `mr1.spec` on Combat Lab base2400 builds a prep year. After it,
at each spot F (stopped) and Y (moving on at warp 5) stand together, with
the other player's follower 50 ly away. The orders for the next year were
written by the original client from each player's `.M` file
(`tools/fleetlab/client-orders`, `mr1-p0.cmds` and `mr1-p1.cmds`):

- the follower: select it on the map, then shift-click F's spot;
- the owner: select F, Goto Y in "Other Fleets Here", then Merge F into Y.

**What the client wrote.** A shift-click on the map inserts a waypoint
after the selected one, aimed at the object there; at a spot holding F and
Y it named F, the lower-numbered fleet. Both followers got waypoint 1 aimed
at F, at warp 6. A shift-click on a fleet's own position wrote nothing, so
this run tests **waypoint 1**, not waypoint 0.

**Predictions, pushed before the runs** (private apparatus, 22:38:10Z;
runs 22:38:18Z), for the exact start and orders:

- elegy e1798ac: F1 and F2 gone; W1 ends at (1256, 1118) with its
  waypoint at (1265, 1100) on Y1; W2 at (1216, 1232) with its waypoint at
  (1225, 1250) on Y2; no events. All eight seed variants agree.
- lane G (`ORDERS.md` reading): neither order rejected, and both followers
  chase Y. At S1 removing F retargets the waypoint to Y, with no draws. At
  S2 the waypoint keeps F's stale id until the start-of-year check picks
  Y, the one fleet of the owner at those coordinates.

One pinned year at cycles 20000 and 30000. The two streams agree on
everything below.

| Spot | Observed | Verdict |
|---|---|---|
| S1: follower replayed first | F1 gone, Y1 has both ships. W1 ended at (1256, 1118). Its waypoint 1 is at (1265, 1100), Y1's end position, aimed at Y1 (a fleet target), warp 6. | CONFIRMED by prediction (Elegy and lane G) |
| S2: owner replayed first | F2 gone, Y2 has both ships. W2 ended at (1216, 1232). Its waypoint 1 is at (1225, 1250), aimed at Y2, warp 6. | CONFIRMED by prediction (Elegy and lane G) |
| Messages | Only one 0x03f per player; no refusal and no leader-gone message | MEASURED (not predicted) |
| The followers' own `.M` files | The waypoint is kept as a fleet target on Y at Y's position, not saved as deep space | MEASURED; Y was in view |

The two paths are not told apart by where the followers end. They differ
only in the random draws they use, and this start has no other random
event to show them.

Raw evidence: private apparatus, `evidence/mf1` (named MF-1 there).
