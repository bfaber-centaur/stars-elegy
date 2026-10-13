# MV-1 prediction: an enemy minefield centred on a planet with no scanner

Pre-run record. It is written and pushed before any run of this start,
and it is never edited after the runs.

## Question

In RG-004, two of player 6's fields were each centred exactly on a
player 0 planet with no planetary scanner. Both were laid that year by a
player 6 fleet in orbit there, and player 0 knew of both (MEASURED, 2
restarts). Elegy treats an owned planet with no scanner as a range-0
viewer. Two readings fit:

- **H-coloc:** the planet itself sees what sits exactly at its position.
- **H-fleet:** player 0 learned of the field by seeing the laying fleet
  in orbit.

There is a counter-case in RG-002/RG-003. Player 3's field 2 contains
player 6's planet 6, which has no scanner, off centre at d² 1280. That
field stayed unknown to player 6 in 15 restarts.

## Start

Spec: `mv1.spec`, a state edit on Combat Lab base2400 (`combatlab
build`). The fields are written directly into the host file. Only case
L's field is laid by a fleet.

The two players are enemies. Player 1 has tech 26. Player 0, the
viewer, keeps the base's tech 3 except electronics 0, to keep its
planetary scanner's range short. Which scanner that tech gives is
inferred, not checked; any range up to 150 ly reaches no other field at
R/4. Player 0's only planetary scanner is at control
S's planet 13. The homeworld 17 and every other case planet have
scanner none. Player 0 has no fleets and no starbases outside its
homeworld. The case planets hold 1000 population at environment
50,50,50, with no mines, factories or defenses. Player 1 owns every
field. Each field starts known only to player 1 (known mask 2, seen
mask 0). No player 1 fleet exists except L's layer, which uses battle
plan "Nobody".

| Case | Player 0 planet (position) | Player 1 field: centre, mines | d² from the planet to the centre | Laying fleet |
|---|---|---|---|---|
| Z | 18 (1324,1192) | 0: (1324,1192), 400 | 0 | none |
| D1 | 7 (1166,1382) | 1: (1167,1382), 400 | 1 | none |
| D1280 | 6 (1166,1017) | 2: (1198,1033), 1600 | 1280 | none |
| N | none | 3: (1200,1250), 400 | (deep space) | none |
| S | 13 (1249,1354), with a planetary scanner | 4: (1259,1354), 25 | 100 (outside the field, radius 5) | none |
| L | 1 (1071,1087) | laid this year by 1/0 in orbit | 0 | 1/0, Mini Mine Layer with 2 Mine Dispenser 40, lay task on waypoint 0, years 0 |

Each field holds only its own case planet. N's field and S's hold no
planet. In D1 the planet lies inside the field (radius 20) at d² 1. The
nearest other planet is 47 ly or more from a field centre. The nearest
player 0 planet outside a case is the homeworld, 111 ly or more away.
Planet 13's scanner is 86 ly or more from every other field.

Start hashes (sha256):
- base `CB.HST`: 6094ce75695562f902c02ee0edc2ea39eb715711e7c85e490321afe4d91c2a3d
- `mv1.spec`: 06df2f4f22a648693e981c4e3914593feab51c68969d9bf0d48d692d0b22fde7
- the start it builds: 4736e6f5d552bf0c1b35b852c1bb85016bd030f2581dd774f2d94a23b6d076e9

Runs: one pinned year at cycles 20000, 30000 and 14000. After the year,
read each field's known and seen masks in the host file, and the objects
and fleets in player 0's file.

## Predictions (H-coloc)

- **Z:** field 0 is known to player 0. Its known mask holds bit 0 (it
  reads 3), and player 0's file lists the field.
- **D1, D1280, N:** fields 1, 2 and 3 stay unknown to player 0. Their
  known masks do not hold bit 0, and player 0's file does not list them.
- **S:** field 4 is known to player 0 (its known mask reads 3), and
  player 0's file lists it. This is the control: a field written into
  the host file is scanned like any other. OB-018 already showed that for
  fleet scanners (`PARITY.md` "Universe objects (S-17, S-18, S-19, IT
  gates, SD detection: CONFIRMED)").
- **L:** the new field at planet 1 is known to player 0, and player 0's
  file lists player 1's fleet 1/0 at planet 1.
- Each case's result is the same in all three streams.

If a field is gone after the year in a stream (decayed or swept), that
case is not exercised in that stream. It is reported and not scored.

## Reading the outcome, fixed in advance

- **If S is known,** existing fields are scanned each year. Z then
  decides it: known means H-coloc, unknown means H-fleet (or H-none if L
  is also unknown).
- **If S is unknown,** existing fields may be checked only when they are
  created or change. Then a negative Z cannot tell H-fleet from that
  reading, and Z is reported as not discriminating.

## Alternatives

- **H-fleet:** Z is unknown and L is known. The planet does not see the
  field. Seeing the laying fleet does.
- **H-none:** Z and L are both unknown. That contradicts RG-004, and the
  contradiction would be kept.
- **H-inside:** D1 or D1280 is known as well. Any planet inside a field
  would then see it, which would contradict the RG-002/RG-003
  counter-case.
- **Range above 0:** D1 is known and D1280 is not. The planet's range-0
  view would then reach at least 1 ly.

Each case is scored on its own observation. If a prediction fails, the
observed outcome is recorded as MEASURED. Packets and salvage at d² 0 are
not covered.
