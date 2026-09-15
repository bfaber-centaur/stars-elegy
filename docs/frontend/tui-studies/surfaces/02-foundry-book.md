# S2 · Foundry book

Illustrative planet and queue. Costs, completion forecasts, environment, and resource splits are mock estimates, not validated Stars! formulas. Queue is a draft for 2444. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEARTH / 2443                    Planet + production                               Owned / observed this turn        │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  Population       382,400         Habitability       78%          Factories       240          Mines            180  │
│  Gravity          0.92 g         Temperature       18°C          Radiation       42 mR        Starbase       present │
│  Resources           640         Production         480          Research         160          Local fleets        1 │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  MINERALS / kt                   AVAILABLE            QUEUE USE THIS YEAR            REMAINING                       │
│  Ironium                              420                             82                  338                        │
│  Boranium                             180                             20                  160                        │
│  Germanium                            260                             72                  188                        │
│                                                                                                                      │
│  PRODUCTION / DRAFT                     Costs below are illustrative totals per row, not per item.                   │
│  ORDER   ITEM                QTY    RESOURCES       I / B / G kt       THIS YEAR             AFTER THIS YEAR         │
│    01    Factories             8          120         12 / 0 / 32      finish 8              row removed             │
│  > 02    Small Freighter       1          360         70 / 20 / 40     finish 1              row removed             │
│    03    Mines                10          150         10 / 0 / 0       none                  all 10 remain           │
│    04    Factories            12          180         18 / 0 / 48      none                  all 12 remain           │
│  ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│          Current-year use                 480         82 / 20 / 72                                                   │
│          Remaining resources                0        Minerals available for later rows; resources exhausted first.   │
│                                                                                                                      │
│  SELECTED ROW / 02                      │ TWO POSITIONS / preview only                                               │
│  Small Freighter ×1                     │                         CURRENT          IF MOVED BELOW MINES              │
│  Resources 360                          │ Factories done                8                             8              │
│  Ironium 70 / Boranium 20 / Germanium 40│ Mines done                    0                            10              │
│                                         │ Freighter                finishes                 partial allocation       │
│  [Move up] [Move down] [Change quantity]│ Freighter resources         360                           210 / 360        │
│  [Remove row]                           │ Exact partial-build behavior requires engine-backed estimates.             │
│ ────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────── │
│  RESOURCE RECEIPT          640 total  =  480 production  +  160 research                                             │
│                           [production used 480 / 480]         Mineral extraction is outside this static preview.     │
│                                                                                                                      │
│  The move preview has not changed the queue.                                 [Apply move]    [Discard preview]       │
│  Draft order: Factories → Freighter → Mines → Factories                         [Keep draft]   [Restore saved queue] │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  ↑/↓ row    Alt+↑/↓ preview move    Enter edit quantity    Tab minerals/queue                        Esc planet list │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: B5’s ledger density and B3’s matched comparisons on an editable production queue.
- Strong: the resource bottleneck and consequences of reordering are visible alongside mineral totals.
- Risk: computed-looking estimates can be overtrusted; partial-build rules must come from actual mechanics later.
- Steal: a small numerical receipt for the budget, plus a comparison that stays explicitly unapplied.

[Gallery](../README.md)
