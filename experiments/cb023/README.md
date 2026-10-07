# CB-023: fuel lost with destroyed ships

Round 4 (COMBAT.md "Salvage", fuel share, BINARY-ONLY). `gen.py` here
writes every round-4 spec (CB-023..CB-031). Player 1's fleet (2 Fuel
Transports, fuel capacity 750 each; 3 Small Freighters, 130 each; fleet
fuel 600) sits in deep space. Two player-0 Hunters with primary "fuel
transports" and no secondary fire only at the Fuel Transports.
`cb023-control.spec` keeps the fleets apart (no battle). Pinned at cycles
20000 and 30000.

## Predictions (committed before the run)

- Both Fuel Transports are destroyed; the Freighters are never fired at.
- The fleet loses `fuel · Σ lost · fuel capacity / Σ before · fuel
  capacity` per kill event, truncated: 600 − 600·1500/1890 = **124** left
  (also 124 if the two die in separate kill events: 600 → 362 → 124).
  Shared by ship count it would be 360; by cargo capacity, 600 (capped).
- The control fleet's fuel is unchanged by the turn (any change there is
  added to the prediction).

## Result

Both seeds (20000, 30000) gave the same end state.

- Both Fuel Transports were destroyed; the three Freighters were never
  fired at. CONFIRMED.
- The committed number **124 missed**: player 1's fleet ended with fuel
  **207**. The control shows why: its fuel went 600 → 1000 during the
  turn, because each Fuel Transport adds 200 fuel per turn and that
  happens **before** the battle. The committed note ("any change is added
  to the prediction") was the wrong correction for a multiplicative rule.
- With the fuel the fleet actually had at battle time (1000), the
  committed formula gives 1000 − ⌊1000·1500/1890⌋ = **207**, as observed;
  sequential kill events give the same 207 (1000 → 604 → 207). A share by
  ship count would leave 400, by cargo capacity 1000. The fuel-capacity
  rule is CONFIRMED.
- Salvage in deep space: 2/0/1, which is one quarter-lost pile from both
  Fuel Transports' minerals.
