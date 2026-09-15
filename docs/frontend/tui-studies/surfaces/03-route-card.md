# S3 · Route card

Illustrative fleet order sheet. Fuel costs and ETAs are hypothetical previews, not derived movement rules. Planned future rows are visually distinct from recorded arrivals. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ SALT ROAD / F018                       Fleet + waypoint plan                                   DRAFT ORDERS / 2443   │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  3 × Small Freighter      at Hearth      fuel 720 / 900 mg       cargo 180 / 600 kt       no damage reported         │
│  Cargo manifest           Ironium 120 kt / Boranium 0 kt / Germanium 60 kt / colonists 0                             │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  FLIGHT PLAN / time descends                 │ ROUTE EXCERPT / distance labels schematic                             │
│                                              │                                                                       │
│  2443  ● HEARTH / arrived this turn          │    Hearth ●                                                           │
│        Recorded position                     │            ╲                                                          │
│        Orders: load nothing                  │             ╲  planned leg 1                                          │
│        Depart with cargo: 180 kt             │              ╲                                                        │
│          :                                   │               ◎ Candle  [selected destination]                        │
│          : warp 7 / planned                  │                :                                                      │
│          : preview fuel cost 140 mg          │                : planned leg 2                                        │
│          :                                   │                :                                                      │
│  2444  > CANDLE / ETA estimate               │               ○ Thimble                                               │
│        Planned: unload all minerals          │                                                                       │
│        Arrival fuel estimate: 580 mg         │    ● recorded now    ◎ selected plan    ○ later plan                  │
│        Cargo after order estimate: 0 kt      │    Lines express order sequence, not exact map geometry.              │
│          :                                   │                                                                       │
│          : warp 6 / planned                  │ NEAR THE ROUTE / observations, not threats confirmed now              │
│          : preview fuel cost 110 mg          │   Needle-7   2441   last observed near Candle                         │
│          :                                   │              composition and current location unknown                 │
│  2445  ○ THIMBLE / ETA estimate              │   Candle     2443   own colony / current observation                  │
│        Planned: wait; no transfer order      │                                                                       │
│        Arrival fuel estimate: 470 mg         │ [Inspect observation]      No interception forecast available         │
│ ─────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────── │
│  SELECTED LEG / Hearth → Candle       [Destination: Candle]   [Speed: warp 7]   [Task: unload all minerals]          │
│                                       Fuel 720 → 580 mg       Cargo 180 → 0 kt after destination task                │
│                                                                                                                      │
│  CHANGES FROM SAVED ORDERS            Added Thimble after Candle. First leg unchanged.                               │
│                                      Draft orders have not been committed with the turn.                             │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  Estimates assume this route, no other orders, and the fixture fuel costs. Recalculate when orders change.           │
│  ↑/↓ waypoint    Enter edit    +/- reorder    Tab route/intel                           [Keep draft] [Restore saved] │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: B2’s descending chronology as a flight plan, with B1’s spatial orientation reduced to a route excerpt.
- Strong: fuel and cargo changes attach to the waypoint where they happen; recorded and planned time look different.
- Risk: scheduled years can imply certainty; a straight route line could be mistaken for a spatially accurate path.
- Steal: carry-forward fuel and cargo printed directly beneath each destination task.

[Gallery](../README.md)
