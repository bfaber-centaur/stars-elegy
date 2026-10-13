# GC-1: ground combat with two drops by one player

Question (coordinator, from lane G's rule in stars-elegy #195): is
ground-combat strength computed per drop and then pooled (H-drop), once
per player from its total troops (H-player), or by resolving the drops
one after another (H-seq)?

Predictions and inputs: `PREDICTION.md`, pushed in 294da9b. The activity
API shows the push at 2026-10-13T06:38:16Z, and the runs started at
06:38:30Z. Spec: `gc1.spec`. Raw evidence: private apparatus
`evidence/gc1`. One pinned year at cycles 20000 and 30000. The two
streams are identical.

The defender is player 1 (JOAT) with 10 Neutron Shields (`s' = 0.75911`).
The attacker is player 0. Its drops are 395 and 165 units from freighters
already in orbit.

| Case | P | Observed (2 of 2 streams) | H-drop | H-player | H-seq | Result |
|---|---:|---|---|---|---|---|
| C, 395 then 165 | 329 | captured; year-end 188, carry 60 (164 landed + growth) | 164 → 188/60 | 165 → 189/75 | 166 → 190/90 | H-drop, CONFIRMED by prediction |
| C2, 165 then 395 | 329 | captured; 188, carry 60 | 164 | 165 | 164 | H-drop (H-seq gives the same here), CONFIRMED by prediction |
| R, 395 then 165 | 600 | repelled; player 1 keeps 154, carry 10 (134 + growth) | 134 → 154/10 | 133 → 152/95 | 134 → 154/10 | per-drop floors, CONFIRMED by prediction |

Messages, as predicted:
- C and C2: 0x00c to player 0 and 0x007 to player 1.
- R: 0x001 to player 0 and 0x004 to player 1.

One predicted detail missed. 0x007's colonists field was expected to
hold the landed count (164). It held 560, the troops dropped, in both
captures. That is the reading `MESSAGES.md` gives ("landed troops, not
survivors"): troops sent down, not those that survived.

So strength is computed per drop, with the 110% factor and both floors
applied to each drop, and then pooled. The pooled total fights the
defenders once. The drops are not resolved one after another (C), and
their order did not change the result (C2). A repelled invasion costs
the defender the sum of the per-drop strengths (R).
