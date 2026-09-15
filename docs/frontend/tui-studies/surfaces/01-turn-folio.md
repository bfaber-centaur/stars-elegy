# S1 · Turn folio

Mock turn report; counts and outcomes are illustrative. Rows summarize player-visible reports, not hidden simulation events. Canvas: 120 × 40.

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HOMEWARD / 2443                         Turn folio                                           07 of 18 reports read   │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  02 battles          04 construction          01 research          03 arrivals          08 other reports             │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  LOCATION / CHANGE                                 │ DENEB IV / BATTLE                              1 of 2 battles   │
│                                                    │                                                                 │
│  > Deneb IV       Battle replay available     NEW  │ Homeward encountered Sable.                                     │
│    Alkaid         Battle replay available     read │                                                                 │
│                                                    │ [Open replay from start]       [Show outcome]                   │
│    Hearth         8 factories completed       NEW  │ Outcome concealed by your replay preference.                    │
│    Candle         1 freighter completed       NEW  │                                                                 │
│    Thimble        6 mines completed           read │ Replay bookmark / last viewed event                             │
│    Home           1 scout completed           read │ ┌─────────────────────────────────────────────────┐             │
│                                                    │ │ E017  A03 fires on B07.                         │             │
│    Research       Propulsion advanced         NEW  │ │ Needle ships 12 → 10; shield 46 → 12.           │             │
│                                                    │ │ Homeward 26 / Sable 26 ships at bookmark.       │             │
│    Salt Road      Arrived at Hearth           NEW  │ │                                                 │             │
│    Survey 04      Arrived at Candle            read│ │ [Continue here]       [Previous record]         │             │
│    One More Turn  Arrived at Thimble           read│ └─────────────────────────────────────────────────┘             │
│                                                    │                                                                 │
│    Needle-7       Last observed 2441          read │ Your 2443 order context                                         │
│    Hearth         Queue now empty             NEW  │   Salt Road is at Hearth, not this battle.                      │
│    Candle         Mineral stock changed       NEW  │   No fleet orders are changed by replaying.                     │
│    ...            5 further reports                │                                                                 │
│                                                    │ Related records                                                 │
│                                                    │   Deneb IV / previous observation / 2442                        │
│                                                    │   A03 / own stack record at battle start                        │
│ ───────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────── │
│  CHANGE STRIP / selected report context                                                                              │
│  2441                         2442                               2443                                                │
│  no Deneb report              Deneb observed                     battle report + replay                              │
│                               [Inspect observation]              [Current selection]                                 │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│  Unread is a reading state, not a severity. A replay bookmark does not mark its report as read.                      │
│  ↑/↓ report    Enter open    R mark read    / filter    Tab preview                    [Next unread] [Done reading]  │
│                                                                                                                      │
│                                                                                                                      │
│                                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

- Tests: B2’s vertical record list and B6’s event receipt inside a turn-wide digest.
- Strong: the player can resume a battle without losing their place among construction and arrivals.
- Risk: the bookmark competes with the actual turn outcome; concealment must be a deliberate preference.
- Steal: separate “unread,” “last viewed,” and “needs an order” rather than one overloaded warning badge.

[Gallery](../README.md)
