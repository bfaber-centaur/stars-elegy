# CO follow-ups: predictions by the Combat-oracle lane, written before the runs

Turn orders' CO-01..06 predictions are on the turn-orders branch (`experiments/fo/client-orders.md`). These are the extra cases this lane added.

## CO-05b: Merge Fleets with both stacks damaged

CO-05 (one damaged stack) cannot separate the two candidate units rules. With only the damaged ships carrying units, ΣD·units / D_count and the task path's units both give 100. CO-05b damages both stacks with FO-07 A's numbers. At merge time, X has 2 ships at 101 units on 50% and Y has 2 at 100 on 50%, so D = 1 per stack.

- Task-path rule (FO-07 A, measured): units = ceil(201 / 4) = 51, 50%. After the merge year's repair: **41 units on 50%**.
- Turn orders' direct-order rule (units over the damaged count): 201 / 2 = 100.5. After repair that is **90 or 91 units**, with the percent 50% (2 damaged of 4).

## CO-06 path change

The first CO-06 runs found the fleet panel's Merge (Merge Fleets) disabled for the 16000-ship fleets, so the client wrote no order. The re-run moves all 16000 ships with the two-fleet exchange (a move-ships record, not the `0x25` merge). Turn orders' boundary prediction is unchanged: 32767 or fewer is kept, and 32768 or more empties the slot.
