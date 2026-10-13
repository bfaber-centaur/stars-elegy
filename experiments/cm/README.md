# CM-1

## CM-1: the slots of the cargo messages 0x02b to 0x02e

Question (lane A): what do the mineral and location slots of 0x02b,
0x02c, 0x02d and 0x02e hold? `docs/MESSAGES.md` gave only the slot list
"fleet, amount, mineral, location", and its slot types are BINARY-ONLY.
RG-002 year 1 has one 0x02e, params [7, 50, 0, 3, 65535, 92]. It is the
record under test, so it is not counted as support below.

No new run. `tabulate.py` decodes every stored message block in the
private apparatus `evidence/` tree with `tools/fleetlab/events.py` and
lists each distinct 0x02b to 0x02e message once: `records.txt`. Runs
that repeat another run's fleets count once (ET-1, ET-1b, ET-2, ET-2b
and ET-2c; TK-301 and TK-302; WP-1 and its hand-driven first try; the
streams of one case). RG-002 and the RM runs, which start from RG-002's
game, are grouped as the record under test. That leaves 66 records from
18 sources. Every one is in player 0's file, about a fleet of player 0.

Each record was matched by hand to its case setup (the spec's cargo and
task, and the README's result) for the cargo type and location. Every
match held.

### Slots

| Slot | Holds | Records |
|---|---|---|
| 1 | the fleet: its number (see "Fleet slot") | 66 |
| 2, 3 | amount, kT or mg; slot 3 was 0 in every record (largest amount 300) | 66 |
| 4 | cargo type (table below) | 66 |
| 5, 6 | location (table below) | 66 |

### Cargo type (slot 4)

| Value | Cargo | 0x02b | 0x02c | 0x02d | 0x02e | Records |
|---|---|---|---|---|---|---|
| 0 | ironium | 17 | 0 | 14 | 0 | 31 |
| 1 | boranium | 13 | 0 | 1 | 0 | 14 |
| 2 | germanium | 2 | 0 | 0 | 0 | 2 |
| 3 | colonists (amount in kT, 100 colonists each) | 0 | 4 | 0 | 10 | 14 |
| 4 | fuel (amount in mg) | 2 | 0 | 3 | 0 | 5 |

Each value is MEASURED by the number of records shown. In these records,
0x02c and 0x02e carried only colonists, and 0x02b and 0x02d never did.
The two WP-NIB 0x02e records (fleets 16 and 17, one run) are two
fleets at planets 4 and 5 whose setups differ only in the waypoint's
high nibble; they count as 2. Germanium rests on 2 records: FO-01 C (160 kT) and WP-1 (30 kT, an
order-file run). In FO-01 B and TK-114 a fleet moved two minerals in
one year and got one message per mineral, ironium first (one fleet in
each).

### Location (slots 5 and 6)

| Target | Slot 5 | Slot 6 | Records | Label |
|---|---|---|---|---|
| a planet | 65535 (0xFFFF) | planet number | 39: player 0's planets, player 1's (TK-201 C, D) and an unowned one (TK-201 E) | MEASURED |
| a fleet | 65535 | 0x8000 + owner·512 + fleet number | 13: 12 at player 0's fleets, 1 at player 1's fleet 0 (FO-04, 33280) | MEASURED |
| a packet | 65534 (0xFFFE) | the object id, 0x2000 + owner·512 + number | 9: 6 player 0's packets, 3 player 1's (ET-2c, NS-1 A6, B2) | MEASURED |
| salvage | 65534 | the object id, as for a packet | 4: player 0's salvage (NS-1 A1 to A4) | MEASURED |
| deep space | x | y | 1: TK-201 F, 0x02d at (1200, 1230), both streams | MEASURED, one record |

That bit 15 of slot 6 tells a fleet from a planet is inferred. A
planet number and a fleet number differ in many planet records (for
example FO-01 I: fleet 8 at planet 9), so slot 6 is the planet, not the
fleet. The object ids match the host-file records of the named packet or
salvage (`MESSAGES.md` "Object ids in slots"). The deep-space form
rests on one record. Another message kind, 0x03c, used the same location
forms in MG-003 (65535, 0x8001 for fleet 1) and MG-006 ((1040, 1230),
the fleet's deep-space position). That is consistent, but it is not a
0x02b to 0x02e record and is not counted.

### Fleet slot (slot 1)

Slot 1 held the fleet's number in all 66 records. Every fleet was of
one design and one ship. The designs included 1, 2, 4, 6, 11, 13 and 15,
and no record carried design bits. Design 0 (MG-003) cannot tell the
readings apart and is not counted as support. So, for one-design,
one-ship fleets, the slot is not design·512 + number in these records,
unlike the fleet slot of 0x05b and 0x059 (FS-1). All the fleets belong
to player 0, so number and owner·512 + number cannot be told apart
here.

### Retrodiction

RG-002 year 1's [7, 50, 0, 3, 65535, 92] reads, by the tables above, as
fleet 7, 50 kT (5000 colonists), colonists, at planet 92. That fits.
It is a retrodiction, not support.

### Not observed

- The deep-space form in 0x02b, 0x02c or 0x02e. A fleet unloading
  colonists in deep space kept them and got 0x165, not 0x02e (TK-201 F).
- An unload to a packet or salvage, and another player's salvage.
- A load from another player's planet.
- A fleet slot of a player other than 0, and a fleet target of a
  player other than 0 and 1.
- The fleet slot of a mixed-design fleet (FS-1 found bit 13 set on one
  in 0x05b).
- An amount of 65536 or more: which of slots 2 and 3 is the high word
  is inferred.

These stay UNKNOWN; the slot-type table in `MESSAGES.md` (BINARY-ONLY)
is the only source for them.
