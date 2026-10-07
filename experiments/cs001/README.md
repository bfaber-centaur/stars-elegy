# CS-001: component table in the game's own displays

Question: does the component table read from the binary (`data/components.json`,
`docs/COMPONENTS.md`) match what the original game shows, for every item,
cost rule and race restriction?

Method (2026-10-07, PG001 2407, player 0 edited with `scripts/oracle/hst-edit`
in both `PG001.HST` and `PG001.M1`, no turn generated):

- **Technology Browser** (Help → Technology Browser), every item stepped
  through with Space, for the 13 race setups in `configs.txt` (PRT number,
  LRT mask, six tech levels, Mystery Trader mask). Predictions of every
  readout were committed in private `stars-decomp`
  (`docs/components-pred/browser-cNN.json`) before any comparison. The
  screens were decoded with a glyph reader built from the game's own font
  (private evidence). `readouts.tsv` is the decoded cost, mass and label
  of every item; the descriptions' values were compared too (private
  evidence, all matched).
- **Ship & Starbase Designer** (F4 → Available Hull Types), every hull and
  starbase hull, for SS + IFE/TT/ARM/ISB, HE, IS, WM, SD and AR at tech 26.
  Read by eye against the predicted slot layouts.
- **Planet status panel**: defense type and coverage at energy 0, 5, 10,
  16 and 26 (10 defenses on Endeavor).

Race setups outside the point budget are fine here: the game only checks
the race when it generates a turn (`docs/ORACLE.md`).

## Result

- Browser: 3,095 of 3,095 readouts as predicted (name, Fe/Bo/Ge,
  resources, mass, tech requirement, Available / UnAvail / research-cost
  label, and every value the description states). The 12 Mystery Trader
  items are absent from the list when the mask is 0 (setup c12: 227 items).
- Designer: all 37 slot layouts as predicted; each race's hull list is
  exactly the predicted set (24, 21, 21, 21, 21, 19 ship hulls; 4, 2, 2, 2,
  2, 3 starbase hulls). Starbase hull costs follow the ISB/AR −20% and
  halving rule (`docs/COMPONENTS.md`).
- Defenses: 9.56%, 18.29%, 21.56%, 26.25%, 32.11% for SDI, Missile
  Battery, Laser Battery, Planetary Shield, Neutron Shield.

`check.py` recomputes every browser readout from `data/components.json` and
the rules in `docs/COMPONENTS.md`: `python3 experiments/cs001/check.py`.
Raw screens: private apparatus repository, `evidence/cs/cs-001/`.
