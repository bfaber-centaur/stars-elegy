# T15 follow-up prediction: DC-4 and DC-5

Pre-run record for two more starts. It is written and pushed after the
runs of `PREDICTION.md` (DC-1 to DC-3) and before any run of these
starts, and it is never edited after the runs.

Why: in DC-2, player 1's received copy of Possum Scout (electronics 5,
player 1 at electronics 3) kept its scanner after two years, in all 9
runs. That rules out the predicted reading. But every design measured as
removed so far, here and in T-37 and SC-021, belonged to player 0. So
DC-2 fits two explanations:

- **H-recv** (predicted): a design received with a fleet transfer is
  exempt from the check, and player 1's own designs are checked like
  player 0's.
- **H-p1**: player 1's designs are not checked in these Combat Lab games,
  whether received or not. The cause would be something about player 1's
  slot, not the transfer.

## Starts

`gen.py` (this version) writes `t15-p1own.spec` and `t15-recv0.spec`.
Two JOAT players, neutral to each other, research 0%. Possum Scout is
Scout + Quick Jump 5 + Possum Scanner (electronics 5).

- `t15-p1own` (DC-4): player 0 at tech 26 everywhere. Player 1 at
  electronics 3, every other field 26. Player 1 has its own Possum Scout
  in design slot 6 and one ship of it in deep space (fleet 1/0). One year.
- `t15-recv0` (DC-5): player 0 at electronics 3, every other field 26.
  Player 1 at tech 26.
  - Player 0 has its own Possum Scout in slot 0, with one ship (fleet
    0/0). This is the control: player 0's own design above its tech.
  - Player 1 has a Possum Scout in slot 6. Its fleet 1/0 has the
    Transfer Fleet task to player 0 at waypoint 0.
  - Two chained years.

Hashes (sha256) of the specs, `gen.py` and the built `.HST` starts are
in the private apparatus, `evidence/t15/SHA256SUMS.pre2`.

Runs: `tools/fleetlab/years`, step 1000, at cycles 20000, 30000 and
14000.

## Predictions

| Case | What | H-recv (predicted) | H-p1 |
|---|---|---|---|
| DC-4 | Player 1's own Possum Scout after year 1 | scanner removed | scanner kept |
| DC-5 control | Player 0's own Possum Scout (slot 0) after year 1 | scanner removed | scanner removed |
| DC-5 | Player 0's received copy of Possum Scout, after years 1 and 2 | scanner kept | scanner removed after year 1 or after year 2 |

If the DC-5 control keeps its scanner, DC-5 is not read. If the
recipient's electronics reaches 5, that year is not read.
