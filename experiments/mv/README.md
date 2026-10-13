# MV-1

## MV-1: an enemy minefield centred on a planet with no scanner

Question (lane D, from RG-004's minefield known_to lines): does an owned
planet with no scanner know an enemy minefield centred exactly on it, or
did player 0 in RG-004 learn of such fields by seeing the fleet that
laid them in orbit?

Predictions: `PREDICTION.md`, pushed alone in 4d0d451. The activity API
shows the push at 2026-10-13T14:30:28Z, and the runs started at
14:30:47Z. Spec: `mv1.spec` (a state edit; every field but L's is
written into the host file). Raw evidence: private apparatus
`evidence/mv1`. One pinned year at cycles 20000, 30000 and 14000. Every
result line is the same in all three streams; the raw host and player
files differ between streams. No field was lost.

| Case | Setup | Host known mask after (start 2) | In player 0's file | Result |
|---|---|---|---|---|
| Z | field 0 centred on scannerless planet 18, d² 0, no fleet | 3 | yes | CONFIRMED by prediction |
| D1 | field 1, scannerless planet 7 inside at d² 1 | 2 | no | CONFIRMED by prediction |
| D1280 | field 2, scannerless planet 6 inside at d² 1280 | 2 | no | CONFIRMED by prediction |
| N | field 3 in deep space | 2 | no | CONFIRMED by prediction |
| S | field 4, 10 ly from planet 13's planetary scanner | 3 | yes | CONFIRMED by prediction |
| L | field 5 laid this year by 1/0 in orbit at scannerless planet 1 | 3 | yes, and fleet 1/0 at planet 1 | CONFIRMED by prediction |

The control S was known, so a field already in the host file is scanned
again each year. By the reading fixed in the pre-run record, Z then
decides: an owned planet with no scanner sees a minefield centred
exactly on it, without any fleet (co-location). At d² 1 it does not,
although the planet is inside the field.

MEASURED, not predicted:
- In the host file, each field's seen word ends equal to its known mask
  (3 for Z, S and L; 2 for the others). It was 0 in the start.
- In player 0's file, Z's and S's fields show known 3, L's field
  (laid this year) shows known 1, and all three show seen 1.

Scope: player 0 at tech 3 with electronics 0; standard fields; one year.
Packets and salvage at d² 0 are NOT RUN.
