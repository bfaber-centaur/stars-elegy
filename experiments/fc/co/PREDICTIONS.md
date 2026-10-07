# CO follow-ups: predictions by the Combat-oracle lane, written before the runs

Turn orders' CO-01..06 predictions are on the turn-orders branch (`experiments/fo/client-orders.md`). These are the extra cases this lane added.

## CO-05b: Merge Fleets with both stacks damaged

CO-05 (one damaged stack) cannot separate the two candidate units rules. With only the damaged ships carrying units, ΣD·units / D_count and the task path's units both give 100. CO-05b damages both stacks with FO-07 A's numbers. At merge time, X has 2 ships at 101 units on 50% and Y has 2 at 100 on 50%, so D = 1 per stack.

- Task-path rule (FO-07 A, measured): units = ceil(201 / 4) = 51, 50%. After the merge year's repair: **41 units on 50%**.
- Turn orders' direct-order rule (units over the damaged count): 201 / 2 = 100.5. After repair that is **90 or 91 units**, with the percent 50% (2 damaged of 4).

## CO-06 path change

The first CO-06 runs found the fleet panel's Merge (Merge Fleets) disabled for the 16000-ship fleets, so the client wrote no order. The re-run moves all 16000 ships with the two-fleet exchange (a move-ships record, not the `0x25` merge). Turn orders' boundary prediction is unchanged: 32767 or fewer is kept, and 32768 or more empties the slot.

## CO-06 controls (after the first exchange runs)

The client's Ship Transfer stopped the destination at 32766, and the host stored **32765** for every total from 32766 up. Two controls separate "the host clamps the move at 32765" from "the host loses one ship":

- 16000 + 16765 (32765): prediction **32765 kept**, fleet 1 gone.
- 16000 + 16000 (32000): prediction **32000 kept**.

## CO-07, CO-07b, CO-08: notes before the runs (predictions are Turn orders')

Seen in the client before the runs (CO-07 base, 2026-10-07):
- Edit Selected Design is **disabled** for the Freighter (4 ships use it) and for the starbase design in use at the homeworld. It is **enabled** for a design used only by a queue entry ("Queued", 0 of 0). So Turn orders' CO-08 prediction A holds for designs that ships or a starbase use. Prediction B (does the host overwrite or refuse?) is reachable only for a queued-only design, and CO-08 runs that.
- A ship design can't be a starbase (starbases have their own designs), so CO-07's "starbase of design D" can't be built. CO-07b instead deletes the starbase design that the homeworld's starbase uses.
