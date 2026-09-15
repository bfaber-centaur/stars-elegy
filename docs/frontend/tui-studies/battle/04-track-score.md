# B4 · Track score

Illustrative replay, not a mechanics specification. E-numbers order recorded events; plot cells and shield units are schematic. Only player-visible records are shown. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DENEB IV / 2443      Track score       Homeward vs Sable                                     PAUSED E017 / 063       │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  TIME →       Event ordinal, equal spacing. One lane per stack.                      Window 011–020 / ALL STACKS     │
│                                                                                                                      │
│  STACK                 011     012     013     014     015     016    [017]    018     019     020      SHIPS NOW    │
│                         │       │       │       │       │       │       ║       │       │       │                    │
│  A03  Mako       ───────┼───────┼───────┼───────┼───────m───────┼───────F───────┼───────┼───────┼─────      14       │
│                                                                         ║                                            │
│  A12  Kestrel    ───────┼───────┼───────F───────┼───────┼───────┼───────╫───────m───────r───────┼─────       8       │
│                                                                         ║                                            │
│  A09  Tender     ───────m───────┼───────┼───────┼───────┼───────┼───────╫───────┼───────┼───────m─────       4       │
│                                                                         ║                                            │
│  B07  Needle     ───────┼───────┼───────┼───────┼───────┼───────m───────r───────┼───────┼───────┼─────      10       │
│                                                                        -2                                            │
│  B02  Thorn      ───────┼───────┼───────┼───────m───────┼───────┼───────╫───────┼───────┼───────┼─────       6       │
│                                                                         ║                                            │
│  B11  Lantern    ───────┼───────m───────r───────┼───────┼───────┼───────╫───────┼───────F───────┼─────      10       │
│                                                                         ║                                            │
│  m move    F fires    r receives fire    -n ships lost    ─ no event in lane    ║ current record                     │
│  Same-column F/r belong to one recorded interaction; lane order has no spatial meaning.                              │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  E017 / INTERACTION                         │ POSITION AT CURSOR                  │ CHANGE                           │
│                                             │                                     │                                  │
│  A03  3rd Beam Wing                         │        c    d    e    f             │ B07 ship count                   │
│       Mako ×14                              │   4    ·    ·    ·    :             │ 12  ●●●●●●●●●●●●                 │
│             │ fire                          │   5   A03 ─────────→ B07            │ 10  ●●●●●●●●●●--                 │
│             ↓                               │   6    ·    ·    ·    ·             │                ^^ lost           │
│  B07  Needle ×10                            │                                     │                                  │
│       shield 46 → 12                        │ : B07 previous location, E016       │ Dots count ships only.           │
│ ────────────────────────────────────────────┴─────────────────────────────────────┴───────────────────────────────── │
│  RECORD STRIP     001 ─────── [011────────────017──020] ────────────────────────────────────────────────── 063       │
│                               visible window     Future labels: ON                                                   │
│                                                                                                                      │
│  ←/→ record    ↑/↓ stack lane    +/- time window    Enter full record    Space play                        Esc close │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: glyph-heavy horizontal chronology, like a musical score, with space relegated to a small excerpt.
- Strong: participation and inactivity can be scanned across stacks; the paired fire/receive marks expose interaction.
- Risk: a many-stack battle demands scrolling, and grid intersections compete with the actual event glyphs.
- Steal: one temporal column linking the actor lane, receiver lane, and count change.

[Gallery](../README.md)
