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

## Results of the stored-research cases

Cycles 20000 and 30000 agreed.

| case | levelled | stored after (Fe.. fields: energy, weapons, propulsion, construction, electronics, biotech) |
|---|---|---|
| `gr-ctl-weapons` | weapons → 6 | 0,0,0,0,0,0 |
| `gr-ctl-con` | construction → 6 | 0,0,0,0,0,0 |
| `gr-prop` | **weapons** → 6 | 0,0,0,850,0,850 |
| `gr-con` | **energy** → 6 | 0,850,0,0,0,850 |

- **MEASURED (2 of 2 streams):** research already stored is levelled
  field by field from energy to biotech, whatever the current field. The
  cyclic order from the field after the current one failed in both
  cases. Exactly one field levelled each time, and the others kept 850,
  10 short of the new cost 860, as predicted.
- These cases add no research in the year, so they test the order of the
  check, not how a year's Generalized Research shares are added.

## Follow-up with research flowing (committed before its runs)

Calibration `gr-cal` (every field at 5, research 100%, no queue,
propulsion current, nothing stored): one year added 18 to propulsion and
6 to every other field (35 resources).

`gr-prop-flow` and `gr-con-flow` repeat `gr-prop` and `gr-con` with
research 100% and no queue, and each chosen field holding 844, so each
reaches exactly 850 only with this year's 6.

Predictions:
- If the shares are all added and then checked in the order measured
  above: weapons (`gr-prop-flow`) and energy (`gr-con-flow`).
- If each field is checked as its share is added, starting after the
  current field: construction and biotech.
- In every case exactly one field levels; the others end at 850 with 10
  short. Stored values after the year are recorded.
