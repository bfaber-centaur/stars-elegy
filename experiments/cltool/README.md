# CombatLab tooling check: production queues and Mystery Trader parts

One pinned turn on the two-player Combat Lab base (cycles 20000) checking
the CombatLab `queue` and `mt` directives and Mystery Trader parts in
designs, before combat round 6 uses them (queued ships lost with a
starbase; Mystery Trader items from battle). Results in `docs/ORACLE.md`,
"Production queues and Mystery Trader parts". Raw run: stars-oracle-apparatus
`evidence/cb6/cltool`.

- Player 1's homeworld (planet 8) queues two bare Scouts (`queue 8 1:2:2`).
- Player 0 (no Mystery Trader items) has two Anti Matter Torpedo
  Destroyers fighting three Laser Destroyers in deep space, and a Mini
  Morph with Mystery Trader parts elsewhere.
- Player 1's Mystery Trader mask is set to 0x0003.

Observed: both Scouts were built; both Mystery Trader designs were kept and
the torpedoes fired (10 hits, checker 0 mismatches); the mask was kept.
