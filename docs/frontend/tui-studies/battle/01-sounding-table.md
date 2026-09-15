# B1 · Sounding table

Illustrative replay, not a mechanics specification. E-numbers order recorded events; plot cells and shield units are schematic. Only player-visible records are shown. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DENEB IV / 2443                    A: Homeward 26 ships   B: Sable 26 ships                      PAUSED E017 / 063   │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│ PLOT AFTER E017                       view: fixed / entire encounter                           A03 selected          │
│                                                                                                                      │
│                  a          b          c          d          e          f          g          h                      │
│           1      ·          ·          ·          ·          ·          ·          ·          ·                      │
│                                                                                                                      │
│           2      ·          ·          ·          ·          A12        ·          ·          ·                      │
│                                                            8                                                         │
│           3      ·          ·          ·          ·          ·          ·          ·          B11                    │
│                                                                                              10                      │
│           4      ·          ·          ·          ·          ·          ·          ·          ·                      │
│                                                                                                                      │
│           5      ·          ·         [A03]════════════════════════════B07         ·          ·                      │
│                                       14                               10                                            │
│           6      ·          ·          ·          ·          ·          ·          ·          ·                      │
│                                                                                                                      │
│           7      ·          A09        ·          ·          ·          ·          B02        ·                      │
│                             4                                                     6                                  │
│           8      ·          ·          ·          ·          ·          ·          ·          ·                      │
│                                                                                                                      │
│                                       A03 → B07 : selected event link, not a range ruler                             │
│                                                                                                                      │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  A03  3rd Beam Wing / Mako ×14                         B07  Needle ×10                                               │
│  c5   own stack                                      f5   observed stack                                             │
│  unchanged this event                                ships 12 → 10       shield 46 → 12                              │
│                                                                                                                      │
│  E017  A03 fires on B07. Two ships destroyed; B07 remains on the plot.                                               │
│  Next recorded: E018 / A12 moves.                                     Future event labels: ON                        │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  START 001 ───────── 009 ─────── 016 [017] 018 ─────────────── 032 ─────────────────────────────── 063 END           │
│                                       ^ event cursor; spacing is ordinal, not elapsed time                           │
│                                                                                                                      │
│  ←/→ event    Space play    [/] previous/next loss    Tab stack    I detail                   Position labels: ON    │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: a large, stable battlefield with a single event caption; horizontal chronology stays subordinate.
- Strong: the actor, target, and changed count are readable without opening an inspector.
- Risk: empty space is expensive in large battles; the connecting stroke could imply weapon range despite its label.
- Steal: an event link that temporarily names both ends while keeping the map stationary.

[Gallery](../README.md)
