# T15 follow-up prediction: DC-6, the check against the load phase

Pre-run record. It is written and pushed after the runs of `PREDICTION.md`
and `PREDICTION-DC4.md`, and before any run of this start. It is never
edited after the runs.

The question is whether the year's design check runs before the
waypoint-0 load tasks (`KERNEL.md` "Turn order", step 2). The case tells
nothing about the order of the check against client orders (order
replay), which needs an order file and stays NOT RUN.

## Start

`gen.py` (this version) writes `t15-load.spec`. Two JOAT players,
neutral to each other, research 0%. Player 0 is at construction 8 and 26
in every other field. Player 1 is at 26 everywhere. Player 0 has two
designs:

- Pod Scout (slot 0): Scout + Quick Jump 5 + Super Cargo Pod. The pod
  needs construction 9 and energy 3, and gives 100 kT of cargo. A bare
  Scout has no cargo space.
- Small Pod Scout (slot 1): Scout + Quick Jump 5 + Cargo Pod. The pod
  needs construction 3 and gives 50 kT.

Fleets:
- 0/0: one Pod Scout in orbit of player 0's homeworld, planet 17, which
  has 423 kT of ironium on the surface. Waypoint-0 task: transport, load
  all ironium.
- 0/1: one Small Pod Scout at planet 17 with the same task. This is the
  control: it shows the load works.
- 0/2: one Pod Scout in deep space at (1010,1010), already holding 80 kT
  of ironium, with no task.

Hashes (sha256) of the spec, `gen.py` and the built `.HST` are in the
private apparatus, `evidence/t15/SHA256SUMS.pre3`. One pinned year
(`tools/fleetlab/years`, N = 1) at cycles 20000, 30000 and 14000.

## Predictions

| Case | H-check-first (predicted; Elegy's step order, check before load tasks) | H-load-first |
|---|---|---|
| DC-6 control: fleet 0/1 | loads 50 Ir | loads 50 Ir |
| DC-6: fleet 0/0 | Super Cargo Pod removed; loads 0 Ir | pod removed after the load; loads 100 Ir |
| DC-6b: fleet 0/2, 80 kT already aboard | Pod removed; the fleet still holds 80 kT (ASSUMPTION T15: cargo is kept above the new capacity) | the same |

For DC-6b the other readings are that the cargo is clamped to 0, or that
it is lost or left as salvage. If the control does not load 50, DC-6 is
not read. If player 0's construction reaches 9, the start is not read.
