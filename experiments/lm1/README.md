# LM-1: the second word of a lay-mines task

Question: a lay-mines waypoint task stores order words. The first is the
years word (0 = this year only, 5 = indefinitely; `OBJECTS.md`
"Laying", Duration). All 6 of RG-002's computer-player lay-mines orders also
store a second word, and all 6 are (5, 5) (MEASURED). The one client-written lay-mines order on record (DS-1)
carries no second word, Combat Lab specs before LM-1 wrote none, and
Elegy's vectors drop it. Does the second word change what the host does?

**Prediction, pushed before the runs** (private apparatus 77f1dad,
committed 2026-10-13T03:22:37Z; runs started 03:22:45Z): H0, the second
word has no effect (Elegy ignores it), with the durations taken from
`OBJECTS.md`, and H-S, the word is stored unchanged.

**Setup.** `lm1.spec` (`combatlab build` on Combat Lab base2400, using the
`lay Y:W` task form). Seven stationary player-0 Layers (Mini Mine Layer,
2 Mine Dispenser 40) in deep space, far apart. Stored words (years,
second): fleets 0, 1 and 2 have (5,0), (5,5) and (5,9); fleets 3 and 4
have (1,0) and (1,5); fleets 5 and 6 have (0,0) and (0,5). Three chained
pinned years (2400 to 2403) at cycles 20000 and again at 30000. Both
streams were identical in every year.

**Results.**

| Fleets | Years word | Field after 2401, 2402, 2403 | Task | Status |
|---|---|---|---|---|
| 0, 1, 2 | 5 | 160, 310, 460 | kept all three years | H0 CONFIRMED by prediction |
| 3, 4 | 1 | 160, 310, 300 | laid in 2401 and 2402, gone after 2402 | H0 CONFIRMED by prediction |
| 5, 6 | 0 | 160, 150, 140 | laid in 2401 only, gone after it | H0 CONFIRMED by prediction |

- Within each row the fleets matched in every year, including the messages
  (0x0c3 and then 0x0c4 per laying fleet, naming only the fleet).
- H-S CONFIRMED: the second word stayed 0, 5 or 9 while the task
  continued. The years word of fleets 3 and 4 went from 1 to 0 after the
  first year.

**Not tested:** a second word on a moving layer (half laying), on an SD
race, or with an odd value in the years word.

Raw evidence: private apparatus, `evidence/lm1`.
