#!/usr/bin/env python3
"""Decode the player-message (event) block of a .M file dump.

Each message record in the type-12 block is:
  word  kind | wide << 9   (kind = message id 0..0x182, see docs/MESSAGES.md;
                            bit k of `wide` = slot k is stored as 2 bytes)
  word  focus object        (planet id, fleet id | 0x8000, or a negative code)
  slots                     (SLOTS[kind] of them, 1 or 2 bytes each)

SLOTS is the number of stored parameter slots per message kind, the
"Slots" count in docs/MESSAGES.md.

Usage:
  events.py DUMP...        # lines from `fleetlab dump` / `hst-edit dump`
                           # ("... .M<n> events raw=HEX" or
                           #  "... .M<n> block type=12 ... data=DEC ...")
Prints one line per message: file, player file, kind, focus, slots.
"""
import re
import sys

SLOTS = [int(c) for c in (
    "4534422423112143332244334443333443311531221666623343412121245511"
    "1155557777555512313232211442663332344444553333444455222135543620"
    "0001111234422552244444666664455755664556712221211111110101310261"
    "1373356764565232311224565624243121434433444544655512711211321222"
    "0110122312211111111556601511222226625533311143311444423114224567"
    "4466534311211222121011234243222567456132344444553333444455332211"
    "241"
)]


def decode(b):
    """Return ([(kind, focus, [slots])], complete) for one event block."""
    out, i = [], 0
    while i + 4 <= len(b):
        w = b[i] | b[i + 1] << 8
        kind, wide = w & 0x1FF, w >> 9
        focus = b[i + 2] | b[i + 3] << 8
        i += 4
        if kind >= len(SLOTS):
            return out, False
        slots = []
        for k in range(SLOTS[kind]):
            if wide >> k & 1:
                slots.append(b[i] | b[i + 1] << 8)
                i += 2
            else:
                slots.append(b[i])
                i += 1
        out.append((kind, focus, slots))
    return out, i == len(b)


def blocks(path):
    for line in open(path, errors="replace"):
        m = re.search(r"(\S+\.M(\d+)) events (?:raw=)?([0-9a-f]+)", line)
        if m:
            yield m.group(1), int(m.group(2)), bytes.fromhex(m.group(3))
            continue
        m = re.search(r"(\S+\.M(\d+)) block type=12 .*data=([\d ]+)", line)
        if m:
            yield m.group(1), int(m.group(2)), bytes(map(int, m.group(3).split()))


def main():
    for path in sys.argv[1:]:
        for name, plr, b in blocks(path):
            recs, ok = decode(b)
            for kind, focus, slots in recs:
                print(f"{name} M{plr} 0x{kind:03x} focus=0x{focus:04x} slots={slots}")
            if not ok:
                print(f"{name} M{plr} undecoded tail")


if __name__ == "__main__":
    main()
