# B3 · Touchline

Illustrative replay, not a mechanics specification. E-numbers order recorded events; plot cells and shield units are schematic. Only player-visible records are shown. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DENEB IV                                       HOMEWARD  /  SABLE                                         2443       │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  HOMEWARD       26 ships remain                   E017 / 063                    26 ships remain       SABLE          │
│                  0 lost so far                    PAUSED                        2 lost so far                        │
│                                                                                                                      │
│                                      A03 fires. Needle loses two ships.                                              │
│                                                                                                                      │
│              BEFORE E017                                    │             AFTER E017                                 │
│                                                             │                                                        │
│                      A12                                    │                     A12                                │
│                                                             │                                                        │
│                                                  B11        │                                                 B11    │
│                                                             │                                                        │
│                                                             │                                                        │
│                    A03 ──────────────→ B07                  │                   A03 ──────────────→ B07              │
│                     14                  12                  │                    14                  10              │
│                                                             │                                                        │
│                                                             │                                                        │
│           A09                                  B02          │          A09                                  B02      │
│                                                             │                                                        │
│              fixed crop / whole plot                        │             same crop / same scale                     │
│ ────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────── │
│                                                                                                                      │
│                   B07 / NEEDLE              SHIPS  12 → 10            SHIELD  46 → 12                                │
│                   A03 / MAKO                SHIPS  14 → 14            No recorded change                             │
│                                                                                                                      │
│  REPLAY WINDOW      015 A03 moves  ──  016 B07 moves  ── [017 FIRE] ──  018 A12 moves                                │
│                     └────────────────────── repeat these four events ──────────────────┘                             │
│                                                                                                                      │
│  MARKERS            001 start         013 first fire         017 first loss         ...         063 result           │
│                     Event labels shown ahead: OFF / next event only                                                  │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  One event at a time. No camera cuts.                                      [Loop 015–018: OFF]   [Speed: 1×]         │
│  ←/→ step    Space play    L loop window    Enter full record    Home start                       Esc close          │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: a sports-replay composition with a score rail, matched before/after views, and a short repeatable passage.
- Strong: losses are instantly legible; a fixed camera makes the visual comparison honest.
- Risk: ship totals suggest equal ship value, and two full plots halve the available spatial resolution.
- Steal: a clearly bounded replay loop around the selected event, with identical framing on both sides.

[Gallery](../README.md)
