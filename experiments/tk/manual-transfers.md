# Manual cargo transfers to other players (TK round 5, predictions)

These cases need a manual cargo transfer, which is an order the player gives
in the client's cargo dialog. Combat Lab cannot put one in a host file, so
the cases wait on client automation (`tools/fleetlab/client-orders`, owned
by the combat oracle lane). Every order here is a legal client order. If
the client refuses one, that refusal is itself the result.

The predictions restate the private binary reading (stars-decomp
`docs/takeover.md` §1 and §4, `docs/orders-misc.md` §4–5,
`docs/messages/orders.md`) as behavior. They were committed before any run.

Setting: the Combat Lab base (`evidence/cb/base2400`), two players at war,
player 0 gives and player 1 receives. Planet numbers and fleets will be
fixed when the client side exists; amounts are in kT, colonists in units of
100.

## When it happens

- The client's order is replayed in step 1 of the year (orders applied).
  The giving fleet or planet loses the cargo **then**.
- Colonists given to a planet the giver does not own are queued as a drop.
  They resolve with the waypoint drops of the **first** drop step (before
  movement), in the same ground combat as unload-task drops on that
  planet.
- Everything else given to another player's fleet or planet is queued as a
  gift and credited in its own step, after the pre-movement load phase and
  before movement. Messages go to the source's owner and the
  destination's owner at that time.
- A gift that does not fit is lost. Nothing goes back to the giver.

## Cases

| Case | Setup | Predicted |
|---|---|---|
| TK-401 | Player 0 Freighter at player 1's planet (P 100, no defenses) gives it 30 colonists by hand | Planet captured in the first drop step with the ground-combat rule of `TAKEOVER.md` (30 against 100 colonists: strength 33 < 100, so the defender wins and keeps `100 − ⌊100·33/100⌋ = 67`). Messages 0x000 to player 0 and 0x003 to player 1, as for an unload. The Freighter's colonists are gone either way. |
| TK-402 | As TK-401 with 200 colonists | Strength 220 ≥ 100: captured with 0x00c to player 0 and 0x007 to player 1; survivors `200·⌊120·220/220⌋/220 = 109`, then growth |
| TK-403 | As TK-402, and a second player 0 Freighter at the same planet has an unload task with 50 colonists | One ground combat with 250 troops for player 0 (strength 275), survivors `250·⌊175·275/275⌋/275 = 159` |
| TK-404 | Player 0 Freighter at an unowned planet gives it 30 colonists by hand (if the client allows it) | Colonists lost, planet stays unowned, 0x002 to player 0 (colonists, planet). No colony |
| TK-405 | Player 0 Freighter gives 100 ironium to player 1's planet | Surface +100. 0x042 to player 0 (source fleet, 100, ironium, planet) and 0x044 to player 1 (planet, 100, ironium, fleet). The minerals are on the surface for this year's production |
| TK-406 | Player 0 Freighter gives 100 ironium to a player 1 fleet with 50 kT free | 50 received, 50 lost. 0x046 to player 0 (requested 100, received 50), 0x048 to player 1 (received 50, requested 100) |
| TK-407 | As TK-406, receiver hold full | Nothing received, all 100 lost. 0x04a to player 0, 0x04c to player 1 |
| TK-408 | Player 0 Freighter gives 20 colonists to a player 1 Freighter with room | Received in full; 0x042 / 0x044 with the cargo kind colonists |
| TK-409 | Player 0 fuel transport gives 50 mg of fuel to a player 1 fleet with room | Received; 0x043 / 0x045 (the fuel variants, whose wording speaks of colonists: LEGACY BUG? in `MESSAGES.md`) |
| TK-410 | Player 0 fleet at player 1's planet with a starbase gives it 30 colonists by hand | Refused at the drop: colonists lost, planet unchanged; 0x058 to player 0 |

## Results (TK-501, TK-502)

Run with `gen5.py` (TK-401..405, TK-410 in TK-501; TK-411, TK-412 in
TK-502); `check5.py` summarizes them and `docs/PARITY.md` "Round 5: manual
cargo transfers" has the table. Every planet outcome held. Minerals given
to a planet sent no 0x042/0x044 (TK-405, TK-412): those kinds belong to
gifts to another player's fleet. TK-406..409 (fleet receivers) are not run:
the client automation opens Cargo Transfer only with the orbited planet.
The client allowed colonists onto an unowned planet and onto a starbase
planet.

## Revised predictions for fleet receivers (before the runs)

The TK-406..409 predictions above assumed the gift queue. A closer reading
of the order replay (stars-decomp `docs/takeover.md` §14, asm-checked)
says the replay applies every transfer in two passes, debits first and
credits second, and that a credit to another player's object takes the
in-place path in the second pass whatever the owners, relation or object
kind. The path that would add to the gift queue is never reached when
giving, and nothing else fills that queue, so the queued-gift step (after
the pre-movement loads) has nothing to do in this build. TK-405 and
TK-412 (minerals to a planet, silent, in place) fit this reading. The
original predictions stay above as written; these replace them for the
runs:

| Case | Setup | Predicted |
|---|---|---|
| TK-406 | Player 0 Freighter gives 100 ironium to a player 1 fleet with 50 kT free | The client offers at most the receiver's free room. If an order for 100 reaches the host anyway: 50 received at order time, the giver gets 0x0dd (shortfall 50, request 100), the other 50 are lost (not refunded). No 0x046/0x048 |
| TK-407 | As TK-406, receiver hold full | Client offers nothing. If 100 is ordered: nothing received, 0x0dd to the giver, 100 lost. No 0x04a/0x04c |
| TK-408 | Player 0 Freighter gives 20 colonists to a player 1 Freighter with room | Received in full at order time (colonists to a fleet are not a drop). No message to either player |
| TK-409 | Player 0 fleet gives 50 mg of fuel to a player 1 fleet with room | Received at order time. No message (no 0x043/0x045) |
| TK-413 | Player 0 Freighter gives 100 ironium to a player 1 Freighter that has an unload-all task at its own planet this year | In place at order time, so the receiver's before-movement unload carries the gift to the planet the same year: player 1's planet surface +100 and 0x02d to player 1. (A queued gift would credit after that unload and leave the 100 in the hold.) |
| TK-414 | As TK-408 with players 0 and 1 friends | Same as TK-408: no relation check on a manual gift |

Not runnable with legal orders yet: a gift whose receiver is gone when
the order is replayed (it would need another player's earlier order in
the same year to merge or scrap the receiver). Reading: the replay looks
up both objects first and skips the whole transfer if either is missing,
so nothing is debited and the giver keeps the cargo.

## Not predicted

- Whether the client lets a player give colonists to an unowned planet
  (TK-404) or to a planet with a starbase (TK-410).
- Which of two conflicting manual orders wins; that depends on the random
  player order of step 1 (`ORDERS.md`).
- Whether the receiver's relation toward the giver matters. The task form
  ("Cargo to another player's fleet", `TAKEOVER.md`) refuses an enemy
  receiver; the manual form has no relation check in the binary reading.
