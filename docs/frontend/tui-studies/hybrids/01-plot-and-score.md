# H1 · Plot and score

Illustrative replay, not a mechanics specification. E-numbers order recorded events; plot cells and shield units are schematic. Only player-visible records are shown. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DENEB IV / 2443         Homeward 26 ships / Sable 26 ships         PLOT + SCORE                 PAUSED E017 / 063    │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  PLOT / after E017 / whole encounter                        │ EVENT RECEIPT                                          │
│                                                             │                                                        │
│         a     b     c     d     e     f     g     h         │ E017  A03 fires on B07                                 │
│    1    ·     ·     ·     ·     ·     ·     ·     ·         │                                                        │
│    2    ·     ·     ·     ·    A12    ·     ·     ·         │              BEFORE       AFTER       CHANGE           │
│    3    ·     ·     ·     ·     ·     ·     ·    B11        │ B07 ships        12          10           -2           │
│    4    ·     ·     ·     ·     ·     :     ·     ·         │ shield           46          12          -34           │
│    5    ·     ·   [A03]══════════════B07    ·     ·         │ plot cell        f5          f5            =           │
│    6    ·     ·     ·     ·     ·     ·     ·     ·         │                                                        │
│    7    ·    A09    ·     ·     ·     ·    B02    ·         │ : on plot = B07 previous cell at E016                  │
│    8    ·     ·     ·     ·     ·     ·     ·     ·         │                                                        │
│                                                             │ PREVIOUS RELEVANT / E016                               │
│  Selection persists when the cursor moves.                  │ B07 moved f4 → f5. Target-choice reason unreported.    │
│ ────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────── │
│  SCORE / all stacks / event ordinal →                          Same-column F/r = one interaction                     │
│                                                                                                                      │
│  STACK             013         014         015         016        [017]        018         019        NOW            │
│  A03  Mako          ·           ·           m           ·           F           ·           ·          14            │
│  A12  Kestrel       F           ·           ·           ·           │           m           r           8            │
│  A09  Tender        ·           ·           ·           ·           │           ·           ·           4            │
│  B07  Needle        ·           ·           ·           m          r -2         ·           ·          10            │
│  B02  Thorn         ·           m           ·           ·           │           ·           ·           6            │
│  B11  Lantern       r           ·           ·           ·           │           ·           F          10            │
│                                                                                                                      │
│  m move    F fire    r receive    · no event    │ cursor          No lane order implies battlefield position.        │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  Previous E016 / B07 moves               Current E017 / A03 fires               Next E018 / A12 moves                │
│  Future labels: ON                       Playback neighborhood: 013–019        [Loop neighborhood: OFF]              │
│                                                                                                                      │
│  Plot selection: A03                     Event receiver: B07                   [Inspect either endpoint]             │
│  ←/→ event    ↑/↓ lane    Tab plot/score    Space play    Enter record                                 Esc close     │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Steals: B1’s stable plot, B4’s synchronized stack lanes, and B2’s observed-state diff with previous relevant history.
- Tests: whether position and participation can share equal billing without reproducing the seed’s log-and-inspector layout.
- Strong: the same event can be understood as a shot across the plot and as an interaction between timeline lanes.
- Risk: two independent selection targets require unusually clear labels; many stacks could overwhelm the score.
- Worth retaining independently: label “plot selection” and “event receiver” separately when they differ.

[Gallery](../README.md)
