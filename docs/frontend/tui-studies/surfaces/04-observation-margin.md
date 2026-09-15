# S4 · Observation margin

Narrow intel companion for a modern Wails galaxy map; the map stays outside this text panel. Mock contact knowledge only, with no extrapolated true positions. Canvas: 72 × 38.

```text
┌──────────────────────────────────────────────────────────────────────┐
│ INTEL / 2443                       Candle vicinity                   │
│ ──────────────────────────────────────────────────────────────────── │
│  Selection on map: Needle-7                                          │
│  Last observed 2441 / two turns old                                  │
│                                                                      │
│  CURRENT KNOWLEDGE                                                   │
│  Name / contact label      Needle-7                                  │
│  Side                      Sable, observed 2441                      │
│  Ship count                12, observed 2441                         │
│  Design                    unreported                                │
│  Current position          UNKNOWN                                   │
│  Current ship count        UNKNOWN                                   │
│                                                                      │
│  OBSERVATION HISTORY / newest first                                  │
│  2443   No new report for this contact.                              │
│  2442   No new report for this contact.                              │
│  2441   OBSERVED / 12 ships / location (128, 206)                    │
│         [Center historical marker]                                   │
│  2440   No matching earlier record.                                  │
│                                                                      │
│  No new report does not imply absence or destruction.                │
│ ──────────────────────────────────────────────────────────────────── │
│  MAP LAYER KEY / words accompany every marker                        │
│  ● NOW       observed this turn                                      │
│  : OLD       position from an earlier observation                    │
│  ? UNKNOWN   no current position; listed, not placed                 │
│                                                                      │
│  [x] Show dated historical markers                                   │
│  [ ] Show inferred areas              No inference available         │
│ ──────────────────────────────────────────────────────────────────── │
│  Other contacts       Seen      Status                               │
│  Survey 04            2443      NOW / own fleet                      │
│  Lantern-2            2442      OLD / 1 turn                         │
│  ↑/↓ contact   Enter history   C center observation   Esc close      │
│                                                                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

- Tests: B6’s narrow embedded format and B5’s explicit missing data on an intel surface.
- Strong: old counts and positions stay useful without silently becoming current facts.
- Risk: repeated knowledge labels consume space; glyphs must remain secondary to the accompanying words.
- Steal: separate “center historical marker” from any action that claims to locate the fleet now.

[Gallery](../README.md)
