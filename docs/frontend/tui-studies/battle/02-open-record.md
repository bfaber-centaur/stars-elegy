# B2 · Open record

Illustrative replay, not a mechanics specification. E-numbers order recorded events; plot cells and shield units are schematic. Only player-visible records are shown. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DENEB IV / 2443      Replay record          Homeward vs Sable                               PAUSED / E017 of 063     │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  EVENT / VERTICAL HISTORY                  │ SELECTED RECORD                                        PLAYER VIEW      │
│                                            │                                                                         │
│   011  A09 moves                           │ E017   A03 → B07   FIRE                                                 │
│    │                                       │                                                                         │
│   012  B11 moves                           │ Actors                                                                  │
│    │                                       │   A03  3rd Beam Wing / Mako              14 ships                       │
│   013  A12 fires on B11                    │   B07  Needle                           12 → 10 ships                   │
│    │                                       │                                                                         │
│   014  B02 moves                           │ Observed changes                  BEFORE          AFTER                 │
│    │                                       │   B07 ship count                      12             10     -2          │
│   015  A03 moves                           │   B07 shield readout                  46             12    -34          │
│    │                                       │   B07 plot cell                       f5             f5      =          │
│   016  B07 moves  f4 → f5                  │   A03 ship count                      14             14      =          │
│    │                                       │                                                                         │
│  >017  A03 fires on B07  ─────────────────→│ This record reports a shot and its outcomes.                            │
│    │   2 ships lost                        │ It does not explain target choice or damage calculation.                │
│    │                                       │                                                                         │
│   018  A12 moves [next recorded]           │ PREVIOUS RELEVANT RECORD                                                │
│    │                                       │   E016  B07 moved into f5 from f4.                                      │
│   019  B11 fires on A12                    │   Adjacent in history; not proof of why A03 fired.                      │
│    │                                       │                                                                         │
│   020  A09 moves                           │ LOCAL POSITION EXCERPT / AFTER                                          │
│    │                                       │          c       d       e       f       g                              │
│    ·                                       │    4     ·       ·       ·       :       ·                              │
│    ·  43 later records                     │    5   [A03] ─────────────────→ B07      ·                              │
│                                            │    6     ·       ·       ·       ·       ·                              │
│                                            │          : previous B07 cell, not a surviving stack                     │
│ ───────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────── │
│  WATCH B07     E001: 12 ships    E016: position changes    E017: 10 ships / shield 12                                │
│  Hidden fields are omitted; an absent value is never treated as zero.                                                │
│                                                                                                                      │
│  Filter: ALL EVENTS     Scope: ENTIRE BATTLE      Future labels: ON      Cursor: AFTER SELECTED RECORD               │
│  ↑/↓ record    Enter follow actor    B before/after    / filter    Space play                       Esc close        │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: vertical chronology as the primary navigation surface, with a debugger-like state diff.
- Strong: changed and unchanged fields coexist; the screen separates observation from causal explanation.
- Risk: selecting a record and following a stack are competing navigation modes; the tiny plot loses global context.
- Steal: “previous relevant record” with an explicit limit on what that history proves.

[Gallery](../README.md)
