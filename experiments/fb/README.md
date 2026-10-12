# FB: queue items whose design the owner may not build

## FB-1

Question: what happens when a ship or starbase item completes and its
design holds a part the owner's race may not use, or an unowned Mystery
Trader part? This tests lane G's rule in `docs/PRODUCTION-LAUNCH.md` "Can
the planet build it" and "Starbases".

Setup: `fb1.spec` on Combat Lab base2400. Player 0 is a human JOAT at
tech 26 in every field, so every part is fully researched. The designs
were written into the state directly (a state edit), because the client
would not let a JOAT draw them:

- Gun Scout: Scout, Long Hump 6, Mini Gun (Inner Strength only);
- HE Scout: Scout, Settler's Delight (Hyper Expansion only);
- MT Scout: Scout, Long Hump 6, Multi Function Pod (Mystery Trader, not
  owned);
- Plain Scout: Scout, Long Hump 6 (control);
- Fort MD5: Orbital Fort with a Mass Driver 5 (Packet Physics only).

Each ship planet has an empty Space Station, 200,000 colonists (about 200
resources), no mines or factories, and 5000 kT of each mineral. The mines
queued after the ship item measure the resources left (a mine costs 5).
The public `fb1.spec` differs from the run's copy only in its comments.

**Predictions** (private apparatus): pushed at 23:11:53Z, before the runs.

- Lane G's rule (`PRODUCTION-LAUNCH.md` as above), with the unit costs at
  tech 26 that Elegy computes: Gun Scout 5 resources and 2/5/2 kT; HE and
  Plain Scout 3 and 2/1/2; MT Scout 9 and 4/1/4; Fort to Fort MD5 18 and
  6/5/5.
- Elegy 8426a6a has no build-time check: it builds every design.

One pinned year at cycles 20000 and 30000, then a second year chained from
each. Year 1 agrees on every line below. Year 2 differs only by 1 kT of
surface minerals on four planets, from mining.

| Case | Queue | Observed | Verdict |
|---|---|---|---|
| a | Gun Scout ×1 from 0%, then mines | 0x04f; no fleet; 2/5/2 kT spent; mines 39 and 19% toward the next (5 resources fewer than a0) | CONFIRMED by prediction |
| a2 | HE Scout ×1 from 0%, then mines | 0x04f; no fleet; 2/1/2 kT spent; mines 39 and 59% (3 fewer) | CONFIRMED by prediction |
| a0 | mines (control) | mines 40 and 19%; no minerals spent | control |
| a1 | Plain Scout ×1 from 0%, then mines (control) | a fleet of 1 (0x02f); 2/1/2 kT spent; mines 39 and 59% | CONFIRMED by prediction |
| b | MT Scout ×1 from 0%, then mines | 0x04f; no fleet; 4/1/4 kT spent; mines 38 and 39% (9 fewer) | CONFIRMED by prediction |
| c | Fort to Fort MD5 from 0%, nothing after | only 0x03e; the Fort kept; 6/5/5 kT spent | CONFIRMED by prediction |
| c0 | Fort, empty queue (control) | nothing spent | control |
| d, year 1 | Gun Scout ×3 from 0%, then mines; about 6 resources | 0x04f; no fleet; 2/6/2 kT spent (one unit and the progress on the next); no mines; the queue keeps an empty ship item (count 0, 39%) before the mines | CONFIRMED by prediction |
| d, year 2 | as left by year 1 | the empty item dropped with no message, its progress lost; 1 mine built (0x037); no minerals spent | CONFIRMED by prediction |

0x04f carried parameters (design slot + 1, 0): slots 0, 1 and 3 gave 1, 2
and 4. The message object was the planet.

Elegy 8426a6a differs in a, a2, b, c and d. It builds the forbidden
designs, including the Mass Driver 5 starbase.

Not tested: a part the owner has not fully researched (the research half
of the check), a starbase hull the race may not build, and a starbase
item at partial progress.
