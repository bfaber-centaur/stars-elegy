# RG-005 pre-run record: an out-of-sample validation game

Pre-run record. It is written and pushed before any turn of RG-005 is
generated, and it is never edited after that. Corrections go in new,
dated text elsewhere.

## Purpose

RG-005 is for validation, not development. The engine under test is
Elegy at the candidate SHA below, run unchanged. Its first comparison
is reported as it comes out, every mismatch MEASURED, before anyone
fixes anything. Once a fix made for RG-005 lands, RG-005 is no longer
out of sample for the engine that carries it.

Candidate engine: `bfaber-centaur/elegy` at
`8584f92e1c0bab6088f02a5da9568b57e405791f` (integrated main, the merge
of elegy #260; tree f0cf8e1; engine and harness code as f09acd9's,
tree b7e0e77). "Unchanged" means no change to engine or harness
code. The RG-005 vector, its empty ledger and the ledger lines the
first comparison generates are testdata only.

## Configuration

A new game from a definition file (`docs/ORACLE.md` "New games from a
definition file"), name RG5, game seed 5005:

- medium universe, normal density, player positions "farther";
- 5 players;
- option flags: public player scores on (flag 6), galaxy clumping on
  (flag 7); random events on; slower tech off;
- victory conditions as RG-004's.

Five custom races (`racelab edit` from AIX's `pg000.r1`), each with
advantage points at 0 or above by `racelab`'s count:

| Player | Name | PRT | LRTs | Growth | Habitability (centre, low–high) | Other | Points |
|---|---|---|---|---|---|---|---|
| 0 | Crafters | CA | IFE, ARM, CE | 11% | gravity immune; temperature 40 (15–65); radiation 60 (30–90) | weapons research expensive, biotech cheap; leftover to concentrations | 50 |
| 1 | Shades | SS | ISB, UR, NRSE, CE | 13% | 30 (10–50); 70 (50–90); 45 (20–70) | 900 colonists per resource; factories 11/10/12; mines 12/5/11; energy cheap, propulsion expensive; leftover to factories | 33 |
| 2 | Stoners | AR | TT, NAS, LSP | 11% | 55 (25–85); 45 (15–75); radiation immune | electronics cheap; leftover to mines | 16 |
| 3 | Raiders | WM | ARM, ISB, GR, RS | 11% | 50 (20–80); temperature immune; 35 (10–60) | factory cost 11; mine cost 6; weapons cheap, biotech expensive; leftover to defenses | 25 |
| 4 | Diggers | SD | IFE, MA, OBRM, BET | 12% | 65 (40–90); 40 (15–65); 55 (30–80) | 900 colonists per resource; factories 11/10/11; mines 12/5/12; energy expensive; leftover to surface minerals | 108 |

No player gives client orders, and no host-file state is edited apart
from the setup step below, which is a state edit (two kinds of byte:
each player's computer-player byte and the pairwise relations).

Race file hashes (sha256; files in apparatus `evidence/rg005/races/`):
- `ca.r1`: c14f2e20ceac81b7f1400d0575cccbfa84bb4cdbd290a175c91811b9d242543e
- `ss.r1`: 62226eb6c6f84fc55b8d0842eca9e83f26131056acb11c67d3a892d490b05cbe
- `ar.r1`: 906ace3bee78177151c85613ff0fc9e9d7018e9757eeb01a51f75b09951fd811
- `wm.r1`: a4242ff0ad3021921e24a9307ca3c15126a17fe473217250376c2fbe4cabe2ea
- `sd.r1`: 246db20721cb38469a05a8081ad1b8f6744b2a4adfb85857d92540d01baf5ae8

Setup step before the first year, as RG-004's (`experiments/rg004/README.md`
"Computer players (setup step)"): every player an expert computer
player, every pair at enemy. Personalities: 0 Turindrone, 1 Automitron,
2 Macinti, 3 Rototill, 4 Cybertron.

What differs:

| | RG-002/RG-003 | RG-004 | RG-005 |
|---|---|---|---|
| Size, density, positions | small, normal, moderate | small, dense, close | medium, normal, farther |
| Players | 7 | 7 | 5 |
| Races | AIX's built-in AI races, player 0 JoaT + ARM (state-edited) | 7 custom races, one shared habitability and economy | 5 custom races, each with its own habitability (three with an immunity), growth, economy and research costs |
| PRT and LRT sets | JoaT {ARM}, HE, SS, IS, CA, PP, AR with their AI sets | WM, SD, IT, JoaT, PP, IS, HE with 1–2 LRTs | CA, SS, AR, WM, SD; no set repeats an earlier corpus's |
| Personalities | all six, own races | Robotoid, Rototill, Cybertron | Turindrone, Automitron, Macinti, Rototill, Cybertron |
| Public scores | off | off | on |
| Slower tech | on (state edit) | off | off |
| Player 0 | client orders | computer | computer |
| State edits | many (RG-002 start) | setup step only | setup step only |

AI level stays expert: it is the only level whose host-file byte was
measured (`docs/ORACLE.md` "Computer players in the host file").

A dry check, before this record: the same five race files and
definition with another seed (9) and name were accepted by the original,
which created the game. Its game options byte read 0x40 (public
scores; MEASURED). No turn of that game was generated, and it is not
RG-005.

## Method

1. Create the game (`tools/fleetlab/new-game`, cycles 20000), apply the
   setup step (`combatlab build`).
2. Warm-up, unrecorded, as RG-004's: `tools/fleetlab/years`, year k at
   cycles 20000 + 1000·(k−1), the host planning for every player. The
   chain starts after warm-up year W: the first year from 45 on whose
   after-files carry at least 2 battle records (distinct battle ids
   across the player files), or 70 if none does.
3. Chain: `rg-chain` (RG-004's), 6 years at cycles 20000, then
   `rg-alt` at 3700 and 1490. Extended to 12 years the same way only if
   cost allows, decided before any comparison is run.
4. Raw evidence in apparatus `evidence/rg005/` with hashes. Lane F
   builds the public vector (`vectors/rg/rg005*.json`). Lane B adds it
   to elegy's `engine/testdata/vectors/rg/` with its `rg/GAMES` line and
   a header-only `rg005-ledger.txt` (hand-pinned `# restarts: N` and
   `# battle records: N`), then runs the ledger and battle-record write
   commands at the candidate SHA (elegy's vectors README "Adding a
   representative game"). No code changes.

## Acceptance criteria

Run classes: the chained run (year 1 strict; later years are chained
samples, as the RG ledgers class them) and the restarts (each year from
the original's own files). The harness runs 8 seeds: its reference seed
and 7 variants. Each compared expectation falls in one class, as the
harness computes it at the candidate SHA (random-driven is computed by
the harness, not classified by hand):

- **strict match:** an expectation the vector does not flag sample, equal
  on the reference seed;
- **random-driven:** such an expectation that misses on the reference
  seed and matches on at least one other variant;
- **deterministic miss:** such an expectation that misses on all 8
  seeds (the reference and all 7 variants), in a restart or in chained
  year 1;
- **sample:** flagged sample by the vector, or a chained difference
  after year 1. Tallied matched/missed, never counted as parity;
- **not compared:** not compared by the harness at the candidate SHA.
  Tallied, never counted as a pass.

Expectations touched by a random event the harness cannot model are
reported as not compared, with that reason, and never silently passed.

Also a failure: a load error, a panic, a restart refusal, or a recorded
order refused on the reference seed in a restart or chained year 1.

**First run.** The first comparison writes the ledger with the harness's
write flags, and its lines are recorded as found. The PR that adds the
vector commits the first-run tallies (counts by class), written before
any classification. Hand classification ("[owner]: note") comes only
after the first result is posted, and it never turns a deterministic
miss into another class.

**"RC holds out of sample"** means: 0 deterministic misses, 0 load
errors, 0 panics and 0 refused orders, in every restart and in chained
year 1. Not-compared and sample counts are reported beside it. It is a
claim about what is compared, not equivalence.

## Predictions

- The original creates RG5 and every chain repeat is byte-identical.
- RC does not hold out of sample: at least one deterministic miss or
  refused order in the restarts or chained year 1.
- At least one random-driven line, and at least one not-compared line.

Each prediction is scored on the first comparison. An outcome nobody
predicted is MEASURED.
