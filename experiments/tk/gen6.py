#!/usr/bin/env python3
"""Write the TK round-6 Combat Lab spec: bombing message variants.

MESSAGES.md lists bombing texts that no run has shown yet. The message is
chosen from the installations killed (T), the colonists killed (K), whether
defenses reduced the bombs (s < 1) and whether the attacker has more than
one fleet at the planet (the plural/owner texts). Predictions restate the
private binary reading (stars-decomp docs/takeover.md §2-§3,
docs/messages/combat.md) as behavior and are written here before the run;
`check6.py` summarizes the dump.

Player 1 has energy 16 (Planetary Shield, coverage 30 tenths of a percent
per defense, TK-302). Bombing runs after growth, so P' = grow(P) and the
defenses that count are min(defenses, ceil(P'/25)).

  python3 experiments/tk/gen6.py OUTDIR      # write tk601.spec
  python3 experiments/tk/gen6.py --table     # print the prediction table
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen2 import cb_run, grow, D_LBU17, D_FREIGHTER  # noqa: E402
from gen3 import NOBODY  # noqa: E402

D_RETRO1 = 7
C_SHIELD = 30


def ftol(x):
    return int(math.floor(x))


def scaled(P, defenses, A=2, I=16):
    """Single LBU-17 (kill 2, installations 16) through Planetary Shields."""
    Pg = grow(P)
    n = min(defenses, math.ceil(Pg / 25))
    s = (1 - 0.001 * C_SHIELD) ** n if n else 1.0
    if s < 1:
        A, I = ftol(A * s + 0.5), ftol(I * (1 - (1 - s) / 2) + 0.5)
    return Pg, n, s, A, I


def runs():
    r = cb_run('tk601', 'bombing message variants (installations only, one installation, several fleets, retro)',
               p1=(16, 3, 3, 3, 3, 3))
    r.h(NOBODY)
    # B1: one installation, no defenses: T 1, K > 0, s = 1.
    r.case('TK-601', 'bomb messages', 'one LBU-17 bomber at player 1 planet 13: P 500, one factory, nothing else')
    r.orbit(13, f'{D_LBU17}:1'); r.target(13, 500, mines=0, factories=1, defenses=0)
    r.expect('planet', (13,), dict(owner=1, factories=0))
    r.expect('msg', (0, '0x063'), '0x063 to player 0 (fleet, planet, colonists killed 1 or 2, 1 installation)')
    r.expect('msg', (1, '0x06d'), '0x06d to player 1')
    # B2: as B1 with a second player 0 fleet: plural texts.
    r.case('TK-602', 'bomb messages', 'as TK-601 at player 1 planet 2, plus a player 0 Freighter (plan Nobody) in orbit')
    r.orbit(2, f'{D_LBU17}:1'); r.orbit(2, f'{D_FREIGHTER}:1', plan=1)
    r.target(2, 500, mines=0, factories=1, defenses=0)
    r.expect('planet', (2,), dict(owner=1, factories=0))
    r.expect('msg', (0, '0x169'), '0x169 to player 0')
    r.expect('msg', (1, '0x173'), '0x173 to player 1')
    # B3: installations only. P 1500 -> 1725, 69 shields count, s = 0.97^69 = 0.122:
    # A = ftol(2 s + 0.5) = 0, I = ftol(16 (1 - (1 - s)/2) + 0.5) = 9; no colonist dies.
    Pg, n, s, A, I = scaled(1500, 100)
    assert (n, A, I) == (69, 0, 9), (n, s, A, I)
    r.case('TK-603', 'bomb messages', 'one LBU-17 bomber at player 1 planet 14: P 1500, defenses 100, factories 10, '
           'mines 10 (69 defenses count after growth, s 0.122)')
    r.orbit(14, f'{D_LBU17}:1'); r.target(14, 1500, mines=10, factories=10, defenses=100)
    r.expect('planet', (14,), dict(owner=1, pop=Pg))
    r.expect('msg', (0, '0x067'), f'0x067 to player 0 (fleet, planet, {I} installations, defenses stopped a share); '
             'no colonists killed')
    r.expect('msg', (1, '0x071'), '0x071 to player 1')
    r.case('TK-604', 'bomb messages', 'as TK-603 at player 1 planet 3, plus a player 0 Freighter (plan Nobody)')
    r.orbit(3, f'{D_LBU17}:1'); r.orbit(3, f'{D_FREIGHTER}:1', plan=1)
    r.target(3, 1500, mines=10, factories=10, defenses=100)
    r.expect('planet', (3,), dict(owner=1, pop=Pg))
    r.expect('msg', (0, '0x16d'), '0x16d to player 0')
    r.expect('msg', (1, '0x177'), '0x177 to player 1')
    # B5: one defense and nothing else: s = 0.97, A = 2, I = 16 -> the defense dies, K >= 1.
    Pg5, n5, s5, A5, I5 = scaled(500, 1)
    assert (n5, A5, I5) == (1, 2, 16), (n5, s5, A5, I5)
    r.case('TK-605', 'bomb messages', 'one LBU-17 bomber and a Freighter at player 1 planet 16: P 500, one defense, '
           'nothing else')
    r.orbit(16, f'{D_LBU17}:1'); r.orbit(16, f'{D_FREIGHTER}:1', plan=1)
    r.target(16, 500, mines=0, factories=0, defenses=1)
    r.expect('planet', (16,), dict(owner=1, defenses=0))
    r.expect('msg', (0, '0x16e'), '0x16e to player 0 (colonists killed, 1 installation, defenses stopped a share)')
    r.expect('msg', (1, '0x178'), '0x178 to player 1')
    # B6: retro bombs with a second fleet.
    r.case('TK-606', 'bomb messages', 'three Retro1 bombers and a Freighter at player 1 planet 9: P 87, environment '
           '55/47/52, original 50/50/50')
    r.orbit(9, f'{D_RETRO1}:3'); r.orbit(9, f'{D_FREIGHTER}:1', plan=1)
    r.target(9, 87, mines=0, factories=0, defenses=0, env='55,47,52', orig='50,50,50')
    r.expect('planet', (9,), dict(owner=1, env=[52, 50, 50]))  # R 3: each axis up to 3 clicks
    r.expect('msg', (0, '0x17a'), '0x17a to player 0 (fleet, planet, clicks); no damage message')
    r.expect('msg', (1, '0x17b'), '0x17b to player 1')
    return [r]


def table():
    for r in runs():
        print('| Case | Setup | Predicted |')
        print('|---|---|---|')
        for cid, rule, text in r.cases:
            pred = []
            for c, k, a, v, y in r.checks:
                if c != cid:
                    continue
                pred.append(v if k == 'msg' else f'planet {a[0]}: ' + ', '.join(f'{x} {y}' for x, y in v.items()))
            print(f'| {cid} | {text} | {"; ".join(pred)} |')


if __name__ == '__main__':
    if sys.argv[1:] == ['--table']:
        table()
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
        for r in runs():
            r.write(out)
            print(r.name, len(r.cases), 'cases')
