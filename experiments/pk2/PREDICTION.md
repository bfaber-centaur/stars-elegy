# PK-2 prediction: packet settings on a starbase rebuilt after a loss

Pre-run record. It is written and pushed before any run of these starts,
and it is never edited after the runs.

## Question

PK-1 (`PARITY.md` "Packet settings after a starbase is destroyed
(MEASURED, PK-1)") showed that a starbase rebuilt after a loss does not
bring back the old destination. The speed was not observable there,
because the battle destroyed the rebuilt starbase again. Whether the old
settings are cleared at destruction or kept but not written is
UNRESOLVED.

In RG-003, a computer player lost the starbase at planet 84 in year 5 and
rebuilt it in year 8 as an Orbital Fort with a single Mass Driver 7. The
next start state shows packet warp 7 with no destination. That player
set no packet speed after year 5, so the 7 did not come from an order.
What sets packet settings when a starbase is rebuilt? The candidates:

- **H-rated (a):** the rated warp of the new design's driver, with no
  destination.
- **H-fixed (b):** a fixed default, the same for every design.
- **H-left (c):** the settings from before the loss, kept somewhere not
  shown while there is no starbase.

## Start

Two state edits on Combat Lab base2400 (`combatlab build`).
`pk2.spec` builds year 1, and `pk2-y2.spec` builds year 2 from the
year-1 result at cycles 20000. Player 0 has tech 26 and these starbase
designs, all Orbital Forts:

| Slot (item) | Design | Driver |
|---|---|---|
| 0 (16) | Fort | none |
| 1 (17) | Launch 10 | Ultra Driver 10 |
| 2 (18) | Launch 5 | Mass Driver 5 |
| 3 (19) | Launch 7 | Mass Driver 7 |
| 4 (20) | Launch 8 | Super Driver 8 |
| 5 (21) | Launch 12 | Ultra Driver 12 |

Every test planet except F starts year 1 with a Launch 10 starbase and
packet destination planet 17 at warp 10. In the built start these are
starbase bytes `1 0 18 24`. On six planets, ten player 1 Laser
Destroyers (plan "Enemies") destroy the starbase in year 1. Nothing is
queued in year 1.

Year 2 makes two state edits:
- It replaces every fleet with one stationary player 1 Laser Destroyer
  at (1400,1400), 107 ly or more from every planet.
- It sets each queue below to one starbase with its first unit 99% done.
  No client order can set 99% progress.

No packet destination or speed is set in either year.

| Case | Planet | Year 1 | Year 2 queue |
|---|---|---|---|
| R5 | 4 | Launch 10 destroyed | Launch 5 |
| R7 | 6 | Launch 10 destroyed | Launch 7 |
| R8 | 1 | Launch 10 destroyed | Launch 8 |
| R12 | 11 | Launch 10 destroyed | Launch 12 |
| R0 | 15 | Launch 10 destroyed | Fort (no driver) |
| R10 | 18 | Launch 10 destroyed | Launch 10 |
| K | 3 | Launch 10 kept | nothing |
| U | 9 | Launch 10 kept | Launch 5 (replaces Launch 10, no loss) |
| F | 13 | no starbase, ever | Launch 5 |

The start hashes (sha256) are as follows:
- base `CB.HST`: 6094ce75695562f902c02ee0edc2ea39eb715711e7c85e490321afe4d91c2a3d
- `pk2.spec`: d4ad6b6fa1f0fad0bb2d8f0e3cebffb6b807337d16f6f3ebde91faf5578a9504
- the year-1 start it builds: a547a15ee686153e582276e5f0639627e2c26e05e779fbe71c09ee267e3bc904

Runs:
- Year 1 runs as one pinned year at cycles 20000, 30000 and 14000.
- Year 2 is built from the cycles-20000 year-1 host file. It also runs at
  20000, 30000 and 14000.
- Read each planet's starbase bytes in the host file and in player 0's
  file after each year, plus player 0's messages.
- Decode: destination = byte 2 | (byte 3 & 3) << 8, minus 1 (0 = none).
  Warp = ((byte 3 >> 2) & 15) + 4, where raw 0 (warp 4) means "unset".

## Preconditions (year 1)

- At R5, R7, R8, R12, R0 and R10, the starbase is destroyed. After the
  year these planets have no starbase.
- K and U keep destination 17 at warp 10.

If a starbase survives at a planet in the cycles-20000 stream, that case
is not exercised. It is reported and not scored.

## Predictions (year 2; H-rated)

- **R5, R7, R8, R12, R10:** each rebuilt starbase has no destination, and
  its warp equals its driver's rating: 5, 7, 8, 12 and 10 respectively.
- **R0:** the Fort has no destination and a warp field of raw 0 (decoded
  warp 4, "unset").
- **F:** as R5, with no destination and warp 5.
- **U:** destination 17 at warp 10 is kept. PD-1 found that replacing a
  standing starbase keeps the settings.
- **K:** unchanged, at destination 17 and warp 10.
- Player 0 gets 0x0cd once for each of the eight starbases built.
- The host file and player 0's file agree.
- Each case's result is the same in all three streams.

## Alternatives

- **H-fixed (b):** R5, R7, R8, R12, R0 and R10 all show the same warp,
  whatever the driver.
- **H-left (c):** the R cases show destination 17 at warp 10, or warp 10
  with no destination.
- **H-rated, clamped:** the warp equals the rating but is capped (for
  example, R12 at 10 or lower).
- **R0:** a Fort with no driver gets a warp other than raw 0.
- **F differs from R5:** a first build and a rebuild after a loss are
  handled differently.
- **U changes:** replacement with no loss takes the new driver's
  rating, unlike PD-1.

Each case is scored on its own observation. If a prediction fails, the
observed outcome is recorded as MEASURED.
