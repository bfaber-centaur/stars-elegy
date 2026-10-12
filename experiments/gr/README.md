# GR-ORDER: in which order are fields levelled up in one check?

Question from the engine sprint: when several fields can level in the
same year, in which order does the host take them? The order matters
because a level raises the cost of every other field's next level
(`KERNEL.md` "Level cost": `base[L] + 10·(sum of the six levels)`), so a
field that is just at its cost before another levels is 10 short after.
RG-001 year 4 (player 3, Generalized Research, electronics current)
levelled biotech before energy, which several orders fit.

Combat Lab base, `combatlab build` per spec. Player 0: Generalized
Research (`lrt 0 0x0010`), every field at 5 (sum 30), so the next level
costs `550 + 300 = 850` in every field, and **860 once any field has
levelled**. The chosen fields hold exactly 850. The research budget is 0%
and planet 17's queue is 1023 Scouts with 20000 kT of each mineral, so no
resources reach research: the year adds nothing, and only the stored 850s
can level.

| case | current field | fields holding 850 |
|---|---|---|
| `gr-prop` | propulsion | weapons, construction, biotech |
| `gr-con` | construction | energy, weapons, biotech |
| `gr-ctl-weapons` | propulsion | weapons |
| `gr-ctl-con` | propulsion | construction |

Pinned at cycles 20000 and 30000.

## Predictions (committed before the runs)

- Controls: the one field levels to 6, its stored research drops to 0.
  If it does not level, the setup does not work (the year's checks need
  research to run, or the budget is not 0) and the order cases are not
  read.
- In `gr-prop` and `gr-con` exactly **one** field levels (to 6, stored 0);
  the other two stay at 5 with 850 stored, 10 short of 860.
- Which one, by candidate order:

| order | `gr-prop` | `gr-con` |
|---|---|---|
| **cyclic from the field after the current one** (the coordinator's) | **construction** | **biotech** |
| energy to biotech | weapons | energy |
| backwards from the field before the current one | weapons | weapons |
| biotech to energy | biotech | biotech |

  The two cases together tell the four orders apart.
- Every field's level and stored research after the year is recorded.
