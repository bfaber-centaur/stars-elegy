# H2 · Replay window

Illustrative replay, not a mechanics specification. E-numbers order recorded events; plot cells and shield units are schematic. Only player-visible records are shown. Wails composition study: ordinary desktop controls surround a text replay inset; the large spatial view is a schematic stand-in for a non-text plot. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Elegy     Deneb IV / 2443                  Battle replay                            [Turn report]       [Close]      │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  NATIVE PLOT AREA / ordinary map rendering                  │ TEXT INSET / event receipt                             │
│  Schematic content below; this area need not use monospace. │                                                        │
│                                                             │ DENEB IV                         E017 / 063            │
│     Homeward 26 ships              Sable 26 ships           │                                                        │
│                                                             │ A03 / Mako ×14                                         │
│                   A12                                       │        ↓ fires                                         │
│                                                 B11         │ B07 / Needle ×10                                       │
│                                                             │                                                        │
│                                                             │ ships      12 → 10       -2                            │
│                   A03 ───────────────── B07                 │ shield     46 → 12      -34                            │
│                                                             │ position   f5 → f5        =                            │
│                                                             │                                                        │
│                                                             │ 016  B07 moves                                         │
│         A09                                    B02          │>017  A03 fires                                         │
│                                                             │ 018  A12 moves / next recorded                         │
│                                                             │                                                        │
│  Fixed view / after selected event                          │ [Full record]    [Pin receiver]                        │
│ ────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────── │
│  TEXT REPLAY RAIL / shared cursor                     HOMEWARD 26 remain / SABLE 26 remain, 2 lost so far            │
│                                                                                                                      │
│     015 A03 moves    ───    016 B07 moves    ───   [017 A03 fires]   ───    018 A12 moves                            │
│     └────────────────────────────────── loop neighborhood 015–018 ─────────────────────────────┘                     │
│                                                                                                                      │
│     B07 / before   12 ships    shield 46      │    B07 / after   10 ships    shield 12                               │
│                                               │    Camera and selection remain fixed when stepping.                  │
│ ──────────────────────────────────────────────┴───────────────────────────────────────────────────────────────────── │
│  [Previous event]  [Play]  [Next event]         [Loop: off] [1×]       [Future: next only]    [Outcome: concealed]   │
│                                                                                                                      │
│  Return to turn report: Deneb IV / report 1 of 18. Replay bookmark updates as you step.                              │
│  Reading state stays unread until you mark the report read.                                [Mark read and return]    │
│  ←/→ event    Space play    L loop    Esc return                                                                     │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Steals: B3’s replay loop and stable framing, B6’s compact receipt, and S1’s report bookmark and reading-state distinction.
- Tests: a TUI inset and replay rail inside an otherwise ordinary desktop battle window.
- Strong: the plot can use a modern renderer while event text keeps the precise, inspectable character of the terminal studies.
- Risk: native controls and text hints may duplicate each other; the inset could consume too much map width.
- Worth retaining independently: a return path that preserves the report position, replay cursor, and unread status separately.

[Gallery](../README.md)
