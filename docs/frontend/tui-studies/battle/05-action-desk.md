# B5 · Action desk

Illustrative replay, not a mechanics specification. E-numbers order recorded events; plot cells and shield units are schematic. Only player-visible records are shown. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DENEB IV / 2443       ACTION DESK       Homeward vs Sable       AFTER E017 / 063                          PAUSED     │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  STACK REGISTER                       Counts at cursor; starting counts are not fleet strength ratings.              │
│  ID   SIDE  DESIGN        NAME / OBSERVATION       START   NOW   LOST   CELL   LAST RECORD     DETAIL                │
│  A03  own   Mako          3rd Beam Wing               14    14      0     c5   017 fires       selected actor        │
│  A12  own   Kestrel       High Window                  8     8      0     e2   013 fires       next: moves           │
│  A09  own   Tender        Carry the Light              4     4      0     b7   011 moves       cargo not shown       │
│ >B07  foe   Needle        observed                    12    10      2     f5   017 hit         selected receiver     │
│  B02  foe   Thorn         observed                     6     6      0     g7   014 moves       no change             │
│  B11  foe   Lantern       observed                    10    10      0     h3   013 hit         no ships lost         │
│                                       TOTAL         54    52      2                                                  │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  EVENT LEDGER                                            │ WATCH / B07                                               │
│  E     ACTOR  ACTION    TARGET   OBSERVED OUTCOME        │ Needle / enemy stack / visible combat record              │
│  011   A09    moves     --       a7 → b7                 │                                                           │
│  012   B11    moves     --       h2 → h3                 │ FIELD                 BEFORE 017     AFTER 017            │
│  013   A12    fires     B11      no ships lost           │ ships                         12            10            │
│  014   B02    moves     --       g6 → g7                 │ shield readout                46            12            │
│  015   A03    moves     --       b5 → c5                 │ plot cell                     f5            f5            │
│  016   B07    moves     --       f4 → f5                 │ armor readout           unreported    unreported          │
│ >017   A03    fires     B07      ships -2; shield -34    │ battle plan             unreported    unreported          │
│  018   A12    moves     --       e2 → e3 [next]          │                                                           │
│  019   B11    fires     A12      no ships lost           │ UNREPORTED ≠ ZERO                                         │
│  020   A09    moves     --       b7 → c7                 │ Enemy fields appear only if disclosed.                    │
│                                                          │                                                           │
│  rows 011–020 / 063     Future labels: ON                │ [Pin B07]   [Follow last change]                          │
│ ─────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────── │
│  LOCATOR / schematic cells       b       c       d       e       f       g       h                                   │
│                      row 2      ·       ·       ·      A12      ·       ·       ·                                    │
│                      row 3      ·       ·       ·       ·       ·       ·      B11                                   │
│                      row 5      ·      A03      ·       ·     [B07]     ·       ·                                    │
│                      row 7     A09      ·       ·       ·       ·      B02      ·                                    │
│                      Other rows empty at this cursor. No movement or range scale implied.                            │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  Scope: ALL STACKS / ALL RECORDS          No filters suppressing losses.          Cursor lock: AFTER RECORD          │
│  Tab region    ↑/↓ row    ←/→ event    / filter    P pin watch    Space play                               Esc close │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: dense operations-console inspection, led by a stack register and numerical ledger rather than a battlefield.
- Strong: identity, force composition, event history, and missing knowledge are simultaneously inspectable.
- Risk: the reader must join three tables mentally; useful for auditing but potentially joyless for ordinary replay.
- Steal: a persistent watch with literal “unreported” values instead of empty cells or misleading zeroes.

[Gallery](../README.md)
