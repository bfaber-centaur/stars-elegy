# FS-1 prediction: the fleet slot of 0x05b

Pre-run record. It is written and pushed before any run of this start,
and it is never edited after the runs.

## Question

`MESSAGES.md` "Object ids in slots" keeps a contradiction open. The
second slot of 0x05b (a fleet scrapped in deep space) does not always
carry the owner in bits 9 and up. These values were read from the
preserved raw evidence:

| Run | Fleet scrapped | Its ships' design | Slot 2 |
|---|---|---|---|
| SV-1 | player 0 fleet 0 | 0 | 0 |
| SV-1 | player 0 fleet 1 | 0 | 1 |
| SV-1 | player 1 fleet 0 | 0 | 0 |
| WF-04 wf-gone | player 1 fleet 0, with a player 0 waypoint aimed at it | 1 | 512 |
| RG-002 year 1 | player 0 fleet 6 | 0 | 6 |
| tk2/tk111 | player 0 fleet 7 | 12 | 6151 = 12·512 + 7 |

In tk111 the at-planet scrap messages (0x059, 0x05a, 0x05c, 0x05d) also
carried 12·512 + n in their first slot for player 0's fleets 0 to 8, and
every one of those fleets was 30 ships of design 12. Lane D's candidate
readings:

- **A:** bits 9 and up hold owner·512 only when something else, such as
  another fleet's waypoint, holds the fleet's full id at scrap time.
- **B:** a stale constant in bits 9 and up, shared by every fleet
  message in the year.
- **C:** the fleet record's raw id or flags word, which depends on fleet
  state.
- **D:** something set by the recipient, the processing order or the
  player count.

The table above suggests a fifth reading, which was found while
preparing this record and is inferred from the six values only:

- **E:** the slot is design·512 + fleet number, where design is the
  index of the fleet's ship design. That is the pair a message needs to
  name the fleet ("Scout #3"). All six values fit E. Only WF-04, with
  design 1 owned by player 1, also fits an owner reading.

## Start

Spec: `fs1.spec`, a state edit on Combat Lab base2400 (CB, 2 players).
The players are enemies at the base's tech 3. Every ship design is a
Scout (one Long Hump 6), apart from two Medium Freighters used as
followers. The designs differ only in name and design index. Each
scrapping fleet has a scrap task on waypoint 0. Each deep-space fleet
is at least 46 ly from every planet and 57 ly from every other case.

| Case | Fleet | Ships (design: count) | Where | Followed by |
|---|---|---|---|---|
| a | 0/3 | 5:1 | deep space (1100,1200) | nobody |
| b | 1/0 | 0:1 | deep space (1200,1240) | nobody |
| c | 1/1 | 0:1 | deep space (1300,1250) | 0/9, whose waypoint 1 is aimed at it |
| d | 1/2 | 3:1 | deep space (1060,1160) | nobody |
| e | 1/4 | 3:1 | deep space (1380,1180) | its own owner's 1/5, whose waypoint 1 is aimed at it |
| f | 0/6 | 2:1 and 7:1 | deep space (1200,1080) | nobody |
| m | 0/8 | 15:1 | deep space (1100,1350) | nobody |
| p | 0/7 | 9:1 | at player 0 planet 0, with no starbase | nobody |
| q | 1/6 | 4:1 | at player 1 planet 2, with no starbase | nobody |

The followers 0/9 and 1/5 are Medium Freighters (design 11), 100 ly
from their targets at warp 4, so neither arrives.

Start hashes (sha256):
- base `CB.HST`: 6094ce75695562f902c02ee0edc2ea39eb715711e7c85e490321afe4d91c2a3d
- `fs1.spec`: f9f7809ffd9fd820c0dbf9d4c185c08d71d84005dfa3f13011cf11ae4af9c98f
- the start it builds: c671a4715506d5427598d65b9066d317d7a3e9b3ec06471f7997c426d1cabf85

Runs: one pinned year at cycles 20000, 30000 and 14000. Read every
message in both player files with `tools/fleetlab/events.py`. Record
each scrapped fleet's record from the start host file (`combatlab
dump`: id, owner, ships, b2, b3, b5).

## Predictions (E)

Slot 2 of 0x05b, sent to the fleet's owner:

| Case | Predicted (E) | Owner reading (A) |
|---|---|---|
| a | 2563 = 5·512 + 3 | 3 |
| b | 0 | 0 |
| c | 1 | 513 |
| d | 1538 = 3·512 + 2 | 2 |
| e | 1540 = 3·512 + 4 | 4 or 516 |
| f | 1030 = 2·512 + 6 (the first and lowest design in the fleet) | 6 |
| m | 7688 = 15·512 + 8 | 8 |

The first slot of the at-planet scrap message (0x059 or 0x05a), sent to
the fleet's owner:

| Case | Predicted (E) |
|---|---|
| p | 4615 = 9·512 + 7 |
| q | 2054 = 4·512 + 6 |

Also:
- Each 0x05b's first slot holds the new salvage's object id
  (0x2000 + owner·512 + number), as in SV-1.
- 0x028 goes to player 0 with (9, 513), and to player 1 with (5, 516),
  as in WK-1 and WK-2.
- Each case's result is the same in all three streams.

## Alternatives and how they would show

- **A:** c gives 513 (and e perhaps 516), while a, d, f, m and p carry
  no design bits.
- **B:** every fleet slot in a stream carries the same bits 9 and up.
- **C:** the values follow the fleet records' state bytes or the
  follow/target state, not the design.
- **D:** the bits differ between player 0's and player 1's messages
  for fleets with the same design.
- **E, other naming rule:** f gives 3590 = 7·512 + 6 (the last or
  highest design). This design cannot tell "first" from "lowest",
  because the record lists design 2 first.

This is CB with 2 players only. The player-count part of D rests on
RG-002 (7 players, design 0, value 6) and is not retested here. Each
case is scored on its own observation. If a prediction fails, the
observed outcome is recorded as MEASURED.
