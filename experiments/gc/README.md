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

The landed and lost counts below are inferred, not reported. They come
from the year-end population and carry through the growth rule
(`t = 15·P` hundredths at 100% habitability, below a quarter of
capacity), because 0x007 does not report the landed count (see below).

| Case | P | Observed (2 of 2 streams) | H-drop | H-player | H-seq | What separates |
|---|---:|---|---|---|---|---|
| C, 395 then 165 | 329 | captured; year-end 188, carry 60, so 164 landed | 164 → 188/60 | 165 → 189/75 | 166 → 190/90 | H-drop vs H-player, and H-drop vs H-seq |
| C2, 165 then 395 | 329 | captured; 188, carry 60, so 164 landed | 164 | 165 | 164 | H-drop vs H-player only (H-seq gives the same) |
| R, 395 then 165 | 600 | repelled; player 1 keeps 154, carry 10, so 134 left and 466 lost | 134 → 154/10 | 133 → 152/95 | 134 → 154/10 | H-drop vs H-player only (H-seq gives the same) |

H-drop matched every case: CONFIRMED by prediction (2 of 2 streams).
H-player fails in C, C2 and R. H-seq fails in C only.

Messages, as predicted:
- C and C2: 0x00c to player 0 and 0x007 to player 1.
- R: 0x001 to player 0 and 0x004 to player 1.

One predicted detail missed. 0x007's colonists field was expected to
hold the landed count (164). It held 560, the troops dropped, in both
captures. That is the reading `MESSAGES.md` gives ("landed troops, not
survivors"): troops sent down, not those that survived.

So strength is computed per drop and then pooled, and the pooled total
fights the defenders once. At least one floor, inner or outer, is
applied to each drop's strength. GC-1 cannot tell which:
`395·1.1 = 434.5` and `165·1.1 = 181.5`, and any per-drop floor (inner
only, outer only, or both) gives 466, while only "no per-drop floor"
gives 467. The drops are not resolved one after another (C). Their order
did not change the result (C2). A repelled invasion cost the defender
the sum of the per-drop strengths (R).

Scope: one attacking player, two drops, a JOAT (not IS) defender with
the Neutron Shield as its only defense type, and drops before movement.
Several attacking players, three or more drops, an IS or other-PRT
defender, and other defense types are NOT RUN.

Corrected 2026-10-13: `PREDICTION.md` says that every fraction is at
least 0.40 from an integer. 137.40 (137.399) is not. The prediction
record stays as pushed. The fractions are 0.45, 0.399 and 0.61, so none
is near a floor boundary, and the predictions are unaffected.
