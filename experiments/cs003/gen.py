#!/usr/bin/env python3
"""Write the CS-003 Combat Lab specs and their predictions.

CS-003 tests the components-table columns that CS-001/CS-002 left
BINARY-ONLY (docs/COMPONENTS.md "Status"). Every prediction below is the
value already published in data/components.json (read from the original
program) pushed through the public rules that use it (KERNEL.md,
OBJECTS.md, TAKEOVER.md, COMBAT.md, SCANNING.md). `alt` is what a
different table value would give.

Runs (Combat Lab universe, one pinned generation 2400 -> 2401 each):

  CS-003-D  ship designer readouts (Initiative/Moves, Cloak/Jam, Scanner
            Range) for designs with Enigma Pulsar, Alien Miner, Mega Poly
            Shell and Multi Contained Munition
  CS-003-W  warp 10 with every engine (ship losses), fuel transport hulls
  CS-003-S  mine sweeping by every plain beam and the Multi Contained
            Munition; mine laying by a Super Mine Layer
  CS-003-B  bombing with the bombs whose zero values are BINARY-ONLY,
            the Multi Contained Munition as a bomb, colonizing with an
            Orbital Construction Module, remote mining with an Orbital
            Adjuster
  CS-003-C  torpedo and missile damage against an unshielded target;
            range-0 beams against an unshielded starbase

  python3 experiments/cs003/gen.py OUTDIR     # OUTDIR/cs003X.spec + predictions.tsv
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = json.load(open(os.path.join(HERE, '..', '..', 'data', 'components.json')))
ITEMS = {(r['category'], r['name']): r for r in TABLE['items']}
BYNAME = {r['name']: r for r in TABLE['items']}

# Combat Lab planets (docs/ORACLE.md "Combat Lab"); 17 = player 0's homeworld, 8 = player 1's
XY = {0: (1045, 1291), 1: (1071, 1087), 2: (1090, 1295), 3: (1129, 1265), 4: (1143, 1103),
      5: (1146, 1180), 6: (1166, 1017), 7: (1166, 1382), 8: (1169, 1145), 9: (1208, 1297),
      10: (1224, 1359), 11: (1243, 1123), 12: (1245, 1158), 13: (1249, 1354), 14: (1268, 1317),
      15: (1281, 1064), 16: (1284, 1383), 17: (1306, 1060), 18: (1324, 1192), 19: (1342, 1123),
      20: (1348, 1290), 21: (1359, 1121), 22: (1368, 1292), 23: (1380, 1295)}

FIELDS = ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')


def tech26(*players):
    return ''.join('tech %d %s 26\n' % (p, f) for p in players for f in FIELDS)


def stat(name, key):
    return BYNAME[name]['stats'][key]


class Run:
    def __init__(self, rid, title):
        self.rid, self.title = rid, title
        self.head, self.lines, self.cases = [], [], []
        self.nfleet = {0: 0, 1: 0}
        self.ndesign = {0: 0, 1: 0}
        self.design_ids = {}
        self.fleets = []        # (owner, id, x, y)
        self.fields = []        # (owner, num, x, y, count)
        self.nfield = {0: 0, 1: 0}

    def design(self, owner, text, name):
        n = self.ndesign[owner]
        assert n < 16, 'at most 16 ship designs per player'
        self.ndesign[owner] += 1
        self.head.append('design %d %d %s = %s' % (owner, n, text, name))
        self.design_ids[(owner, name)] = n
        return n

    def fleet(self, owner, x, y, ships, plan=0, fuel=200, extra='', planet=None):
        fid = self.nfleet[owner]
        self.nfleet[owner] += 1
        at = ('planet %d ' % planet if planet is not None else '') + 'at %d %d' % (x, y)
        self.lines.append(('fleet %d %d %s ships %s plan %d fuel %d %s' % (owner, fid, at, ships, plan, fuel, extra)).rstrip())
        self.fleets.append((owner, fid, x, y))
        return fid

    def field(self, owner, x, y, count):
        n = self.nfield[owner]
        self.nfield[owner] += 1
        self.lines.append('thing minefield %d %d %d %d %d kind std' % (owner, n, x, y, count))
        self.fields.append((owner, n, x, y, count))
        return n

    def case(self, cid, row, column, what, expect, alt, check):
        self.cases.append(dict(id='%s-%s' % (self.rid, cid), row=row, column=column, what=what,
                               expect=expect, alt=alt, check=check))

    def spec(self):
        return '# %s: %s (experiments/cs003/gen.py)\n' % (self.rid, self.title) + \
            '\n'.join(self.head) + '\n' + '\n'.join(self.lines) + '\n'


RUNS = []


def run(*a):
    r = Run(*a)
    RUNS.append(r)
    return r


def speed_code(w, mass, engines, halfsteps=0, jets=0, over=0):
    """COMBAT.md "Token values": speed code without the battle-only terms."""
    return max(0, min(8, w - 4 + jets + 2 * over + (halfsteps + 1) // 2 - (mass // 70) // engines))


def moves(code):
    q = code + 2              # quarter squares per round
    whole, frac = divmod(q, 4)
    return {0: '%d' % whole, 1: '%d 1/4' % whole, 2: '%d 1/2' % whole, 3: '%d 3/4' % whole}[frac] \
        .replace('0 1/', '1/').replace('0 3/', '3/')


def cloak_pct(u):
    """SCANNING.md "Fleet cloak" step 3."""
    if u <= 100: return u // 2
    if u <= 300: return 50 + (u - 100) // 8
    if u <= 612: return 75 + (u - 300) // 24
    if u <= 1124: return 88 + (u - 612) // 64
    return 96 if u <= 1379 else 97 if u <= 1611 else 98


def jam_pct(factors):
    """COMBAT.md "Token values": jammer % from the per-item factors."""
    if not factors: return 0
    J = 10000
    for f in factors: J = J * f // 100
    return min(95, 100 - (J + 50) // 100)


def mass_of(*parts):
    return sum(BYNAME[n]['mass'] * c for n, c in parts)


def battle_warp(engine):
    return stat(engine, 'battle_warp')


# ------------------------------------------------------------------ CS-003-D designer
r = run('CS-003-D', 'ship designer readouts')
r.head.append(tech26(0, 1).rstrip())
D = []


def dcase(cid, row, column, text, parts, hull, engine, nengine, half=0, cloak=0, jam=(), scan=None, alt=''):
    n = r.design(0, text, 'CS3D-%02d' % len(D))
    m = mass_of((hull, 1), *parts)
    code = speed_code(battle_warp(engine), m, nengine, half)
    exp = 'mass %d, moves %s, cloak/jam %d%%/%d%%' % (m, moves(code), cloak_pct(cloak), jam_pct(jam))
    if scan:
        exp += ', scanner %d / %d' % scan
    D.append((n, text))
    r.case(cid, row, column, 'design %d: %s' % (n, text), exp, alt, ('designer', 0, n))


dcase('A', 'Enigma Pulsar', 'cloak_points', 'Battleship, 4 Enigma Pulsar',
      [('Enigma Pulsar', 4)], 'Battleship', 'Enigma Pulsar', 4, half=4, cloak=4 * 20,
      alt='cloak 42% if 21 points per engine (one Enigma in CB-000 showed 10%: 20 or 21)')
dcase('B', 'Alien Miner', 'battle_speed_half_steps', 'Midget Miner, 1 Long Hump 6, empty',
      [('Long Hump 6', 1)], 'Midget Miner', 'Long Hump 6', 1,
      alt='control for C and D')
dcase('C', 'Alien Miner', 'battle_speed_half_steps', 'Midget Miner, 1 Long Hump 6, 1 Alien Miner',
      [('Long Hump 6', 1), ('Alien Miner', 1)], 'Midget Miner', 'Long Hump 6', 1, half=1,
      cloak=60, jam=(70,), alt='moves 1 if the Alien Miner adds no battle speed')
dcase('D', 'Alien Miner', 'battle_speed_half_steps', 'Midget Miner, 1 Long Hump 6, 2 Alien Miner',
      [('Long Hump 6', 1), ('Alien Miner', 2)], 'Midget Miner', 'Long Hump 6', 1, half=2,
      cloak=120, jam=(70, 70), alt='moves 1 1/2 if each Alien Miner were a whole step')
dcase('E', 'Alien Miner', 'battle_speed_half_steps', 'Midget Miner, 1 Enigma Pulsar, 1 Alien Miner',
      [('Enigma Pulsar', 1), ('Alien Miner', 1)], 'Midget Miner', 'Enigma Pulsar', 1, half=2,
      cloak=80, jam=(70,), alt='moves 2 1/2 if Enigma and Alien Miner were rounded separately')
dcase('F', 'Mega Poly Shell', 'scanner_range, penetrating_range', 'Medium Freighter, 1 Long Hump 6, empty, 1 Mega Poly Shell',
      [('Long Hump 6', 1), ('Mega Poly Shell', 1)], 'Medium Freighter', 'Long Hump 6', 1,
      cloak=40, jam=(80,), scan=(80, 40), alt='scanner (none) if the shell had no scanner')
dcase('G', 'Multi Contained Munition', 'scanner_range, penetrating_range',
      'Cruiser, 2 Long Hump 6, empty, empty, 1 Multi Contained Munition, empty, empty, empty',
      [('Long Hump 6', 2), ('Multi Contained Munition', 1)], 'Cruiser', 'Long Hump 6', 2,
      cloak=20, scan=(150, 75), alt='scanner (none) if the munition had no scanner')
r.lines.append('fleet 0 0 planet 17 at 1306 1060 ships 0:1 plan 0 fuel 200')

# ------------------------------------------------------------------ CS-003-W warp 10
r = run('CS-003-W', 'warp 10 with every engine; fuel transports')
r.head.append(tech26(0, 1).rstrip())
r.head.append('research 0 0\nresearch 1 0')
engines = [x for x in TABLE['items'] if x['category'] == 'engine']
SHIPS, FLEETS = 10, 6
y = 1005
for e in engines:
    n = r.design(0, 'Small Freighter, 1 %s, empty, empty' % e['name'], 'W10-%02d' % e['index'])
    rated = e['stats']['warp10_rated']
    fids = []
    for k in range(FLEETS):
        assert all((1105 - a) ** 2 + (y - b) ** 2 > 4 for a, b in XY.values())
        fids.append(r.fleet(0, 1005, y, '%d:%d' % (n, SHIPS), fuel=20000, extra='to 1205 %d warp 10' % y))
        y += 4
    tot = SHIPS * FLEETS
    if rated:
        exp, alt = 'all %d ships arrive (rated for warp 10)' % tot, 'about 1 in 10 lost'
    else:
        exp, alt = 'some of %d ships lost (1 in 10 each, KERNEL.md; P(no loss) = %.4f)' % (tot, 0.9 ** tot), 'none lost if rated'
    r.case('E%02d' % e['index'], e['name'], 'warp10_rated', '%d fleets of %d Small Freighters at warp 10' % (FLEETS, SHIPS),
           exp, alt, ('warp10', 0, fids, rated, tot))
assert y < 1400
# fuel transports: player 1, stationary in deep space with no fuel; generation 200 mg per hull a year (KERNEL.md)
ft = r.design(1, 'Fuel Transport, 1 Long Hump 6, empty', 'FT')
sx = r.design(1, 'Super-Fuel Xport, 2 Long Hump 6, empty, empty', 'SFX')
mf = r.design(1, 'Medium Freighter, 1 Long Hump 6, empty, empty', 'MF')
for cid, d, ships, row, exp, alt in (
        ('T1', ft, 1, 'Fuel Transport', 200, '0 without fuel_transport'),
        ('T2', ft, 3, 'Fuel Transport', 600, '0'),
        ('T3', sx, 1, 'Super-Fuel Xport', 200, '0'),
        ('T4', mf, 1, 'Medium Freighter (control)', 0, '200')):
    yy = {'T1': 1100, 'T2': 1140, 'T3': 1180, 'T4': 1220}[cid]
    fid = r.fleet(1, 1385, yy, '%d:%d' % (d, ships), fuel=0)
    r.case(cid, row, 'fuel_transport', '%d stationary ship(s), fuel 0' % ships, 'fuel %d mg' % exp, alt,
           ('fuel', 1, fid, exp))

# ------------------------------------------------------------------ CS-003-S sweeping and laying
r = run('CS-003-S', 'mine sweeping by every plain beam; Super Mine Layer laying')
r.head.append('relation 0 1 2\nrelation 1 0 2')
r.head.append(tech26(0, 1).rstrip())
r.head.append('research 0 0\nresearch 1 0')
r.head.append('plan 0 0 4 1 0 1 = Enemies\nplan 1 0 4 1 0 1 = Enemies')
plain = [x for x in TABLE['items'] if x['category'] == 'beam' and x['stats']['kind'] == 'beam']
assert len(plain) == 17     # 16 plain beams + Multi Contained Munition
placed = []                 # (x, y, radius)


def clear(x, y, rad):
    if not (1003 + rad <= x <= 1397 - rad and 1003 + rad <= y <= 1397 - rad):
        return False
    if any((x - a) ** 2 + (y - b) ** 2 <= (rad + 3) ** 2 for a, b in XY.values()):
        return False
    return all(math.hypot(x - a, y - b) > rad + rr + 2 for a, b, rr in placed)


def spot(rad):
    for yy in range(1005, 1400, 3):
        for xx in range(1005, 1400, 3):
            if clear(xx, yy, rad):
                placed.append((xx, yy, rad))
                return xx, yy
    raise SystemExit('no room for radius %d' % rad)


def decay(n):
    return n - max(10, max(2, n * 2 // 100))


order = sorted(plain, key=lambda b: -b['stats']['mines_swept'])
for i, b in enumerate(order):
    owner = i % 2               # alternate: player 0 sweeps player 1's field and vice versa
    sweep = b['stats']['mines_swept']
    count = max(400, (sweep * 5) // 4 + 200)
    rad = math.isqrt(count) + 1
    x, yy = spot(rad)
    fieldowner = 1 - owner
    fnum = r.field(fieldowner, x, yy, count)
    d = r.design(owner, 'Scout, 1 Long Hump 6, empty, 1 %s' % b['name'], 'SW-%02d' % b['index'])
    r.fleet(owner, x, yy, '%d:1' % d)
    after = decay(count)
    pred = after - sweep if sweep > 0 else after
    gat = after - b['stats']['damage'] * 16
    gat = 'cleared' if gat < 0 else 'field %d' % gat
    r.case('B%02d' % b['index'], b['name'], 'kind, mines_swept',
           'one Scout with 1 %s at the centre of a %d field (no planets)' % (b['name'], count),
           'field %d (decay to %d, swept %d)' % (pred, after, sweep),
           'gatling (range 4): %s; sapper: field %d' % (gat, after), ('field', fieldowner, fnum, x, yy, pred))
# Super Mine Layer: 2 Mine Dispenser 40 lay 80 a year; x2 on this hull (OBJECTS.md "Laying"); Mini Mine Layer control
sml = r.design(0, 'Super Mine Layer, 3 Long Hump 6, 1 Mine Dispenser 40, 1 Mine Dispenser 40, empty, empty, empty', 'SML')
mml = r.design(0, 'Mini Mine Layer, 1 Long Hump 6, 1 Mine Dispenser 40, 1 Mine Dispenser 40, empty', 'MML')
for cid, d, row, exp, alt in (('L1', sml, 'Super Mine Layer', 160, '80 without the doubling'),
                              ('L2', mml, 'Mini Mine Layer (control, OB-002)', 160, '80')):
    x, yy = spot(16)
    fid = r.fleet(0, x, yy, '%d:1' % d, extra='task lay 0')
    r.case(cid, row, 'mine_layer_multiplier', 'one layer, 2 Mine Dispenser 40, lay this year only',
           'new player 0 standard field %d at (%d,%d)' % (exp, x, yy), alt, ('newfield', 0, x, yy, exp))
# no sweeper may sit in another enemy field
for o, fid, x, yy in r.fleets:
    inside = [f for f in r.fields if f[0] != o and (f[2] - x) ** 2 + (f[3] - yy) ** 2 <= f[4]]
    assert len(inside) <= 1, (o, fid, inside)

# ------------------------------------------------------------------ CS-003-B bombing, colonizing, remote mining
r = run('CS-003-B', 'bombs with BINARY-ONLY zero values, MCM bomb, OCM colonize, Orbital Adjuster mining')
r.head.append('relation 0 1 2\nrelation 1 0 2')
r.head.append(tech26(0).rstrip())
r.head.append('research 0 0\nresearch 1 0')
r.head.append('plan 0 0 4 1 0 1 = Enemies')
r.head.append('sbdesign 1 0 Orbital Fort = Bare Fort')


def grown(p, carry=0):
    """KERNEL.md growth at 100% habitability, growth 15%, far below capacity."""
    return p + (15 * p + carry) // 100


targets = iter([0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23])


def target(p, **kv):
    n = next(targets)
    r.lines.append('planet %d owner 1 pop %d starbase none' % (n, p))
    kv = dict(kv)
    kv.setdefault('excess', 0)
    kv.setdefault('defenses', 0)
    kv['env'] = '50,50,50'
    kv['scanner'] = 31
    r.lines.append('planetset %d %s' % (n, ' '.join('%s=%s' % (k, v) for k, v in kv.items())))
    return n


def bomber(name, count=1):
    hull = 'Mini Bomber, 1 Long Hump 6, %d %s' % (count, name)
    return r.design(0, hull, name[:12])


for name in ('LBU-17 Bomb', 'LBU-32 Bomb', 'LBU-74 Bomb', 'Hush-a-Boom'):
    d = bomber(name)
    n = target(9)
    r.fleet(0, *XY[n], ships='%d:1' % d, planet=n)
    k = stat(name, 'kill_tenths_pct')
    r.case('N-' + name.split()[0], name, 'min_kill', '1 %s on P=9 (P\'=%d), no defenses' % (name, grown(9)),
           'pop %d (kill 1: k = 0 or 1 from %d permille, raised to 1)' % (grown(9) - 1, k),
           'pop %d or less with a minimum of 2 units or more' % (grown(9) - 2), ('pop', n, grown(9) - 1))
d = bomber('Retro Bomb')
n = target(9, mines=10, factories=10)
r.fleet(0, *XY[n], ships='%d:1' % d, planet=n)
r.case('R', 'Retro Bomb', 'kill_tenths_pct, installations, min_kill', '1 Retro Bomb on P=9, mines 10, factories 10, not terraformed',
       'pop %d, mines 10, factories 10' % grown(9), 'fewer colonists or installations',
       ('popinst', n, grown(9), 10, 10))
for name in ('Smart Bomb', 'Neutron Bomb', 'Enriched Neutron Bomb', 'Peerless Bomb', 'Annihilator Bomb'):
    d = bomber(name)
    n = target(1, mines=20, factories=20)
    r.fleet(0, *XY[n], ships='%d:1' % d, planet=n)
    r.case('S-' + name.split()[0], name, 'installations, min_kill', '1 %s on P=1, mines 20, factories 20' % name,
           'pop 1, mines 20, factories 20 (smart kill at most P\'-1 = 0; no minimum; no installation kills)',
           'pop 0 with a minimum kill; fewer installations with installation kills', ('popinst', n, 1, 20, 20))
d = r.design(0, 'Cruiser, 2 Long Hump 6, empty, empty, 1 Multi Contained Munition, empty, empty, empty', 'MCM Cruiser')
n = target(870, mines=10)
r.fleet(0, *XY[n], ships='%d:1' % d, planet=n)
r.case('M', 'Multi Contained Munition', 'bomb_kill_tenths_pct, bomb_installations, bomb_min_kill',
       '1 MCM Cruiser on P=870 (P\'=%d), mines 10' % grown(870),
       'pop %d (2%% of 1000 = 20, above the minimum 3), mines 5' % (grown(870) - 20),
       'pop 990 with 1%, 970 with 3% (T-18 at P\'=100 could not tell 2% from the minimum 3)',
       ('popinst', n, grown(870) - 20, 5, None))
# Orbital Construction Module colonizes (unowned planets, colonize on waypoint 0, in orbit)
for cid, text, exp, alt in (
        ('O1', 'Colony Ship, 1 Long Hump 6, 1 Orbital Construction Module', 'colonized by player 0', 'not colonized'),
        ('O2', 'Colony Ship, 1 Long Hump 6, 1 Colonization Module', 'colonized by player 0 (control)', 'not colonized'),
        ('O3', 'Colony Ship, 1 Long Hump 6, empty', 'not colonized (control)', 'colonized')):
    d = r.design(0, text, 'Col-' + cid)
    n = next(targets)
    r.fleet(0, *XY[n], ships='%d:1' % d, planet=n, extra='cargo 0 0 0 25 task colonize')
    r.case(cid, 'Orbital Construction Module' if cid == 'O1' else 'control', 'colonizes', text + ', 25 colonists, in orbit',
           exp, alt, ('owner', n, 0 if cid != 'O3' else None))
# remote mining: unowned planets, concentrations 100, mine task on waypoint 0 (KERNEL.md "Remote mining")
for cid, text, rate, alt in (
        ('X1', 'Midget Miner, 1 Long Hump 6, 2 Orbital Adjuster', 0, '+1 kT per robot-rate point'),
        ('X2', 'Midget Miner, 1 Long Hump 6, 2 Robo-Midget Miner', 10, '0')):
    d = r.design(0, text, 'Min-' + cid)
    n = next(targets)
    r.lines.append('planetset %d conc=100,100,100' % n)
    r.fleet(0, *XY[n], ships='%d:1' % d, planet=n, extra='task mine')
    r.case(cid, 'Orbital Adjuster' if cid == 'X1' else 'control', 'mining_rate', text + ' mining an unowned planet, concentrations 100',
           'surface +%d kT of each mineral' % rate, alt, ('mined', n, rate))

# ------------------------------------------------------------------ CS-003-C torpedoes and range-0 beams
r = run('CS-003-C', 'torpedo and missile damage; range-0 beams against a starbase')
r.head.append('relation 0 1 2\nrelation 1 0 2')
r.head.append(tech26(0, 1).rstrip())
r.head.append('research 0 0\nresearch 1 0')
r.head.append('plan 0 0 5 1 0 1 = Enemies')
r.head.append('sbdesign 1 0 Orbital Fort = Bare Fort')
tgt = r.design(1, 'Battleship, 4 Long Hump 6, empty, empty, empty, empty, empty, empty, empty, 6 Neutronium, empty, empty', 'Hulk')
torps = [x for x in TABLE['items'] if x['category'] == 'torpedo']
spots = [(1020 + 40 * k, 1230) for k in range(8)] + [(1020 + 40 * k, 1030) for k in range(4)] + \
        [(1200, 1250), (1300, 1250), (1100, 1340)]
for t in torps:
    d = r.design(0, 'Cruiser, 2 Trans-Star 10, empty, empty, 2 %s, 2 %s, 2 %s, empty' % ((t['name'],) * 3),
                 'T-%02d' % t['index'])
    x, yy = spots.pop(0)
    assert all((x - a) ** 2 + (yy - b) ** 2 > 100 for a, b in XY.values())
    r.fleet(0, x, yy, '%d:1' % d)
    r.fleet(1, x, yy, '%d:3' % tgt)
    dmg = t['stats']['damage']
    missile = t['stats']['kind'] == 'missile'
    r.case('T%02d' % t['index'], t['name'], 'kind',
           'Cruiser with 6 %s vs 3 unarmed, unshielded Battleships' % t['name'],
           'every hit does %d to armor (%s)' % (2 * dmg if missile else dmg, 'missile: doubled' if missile else 'torpedo'),
           '%d' % (dmg if missile else 2 * dmg), ('torp', x, yy, 2 * dmg if missile else dmg))
for name, n in (('Blackjack', 5), ('Bludgeon', 4), ('Blunderbuss', 12)):
    d = r.design(0, 'Destroyer, 1 Long Hump 6, 1 %s, empty, empty, empty, empty, empty' % name, 'R0-' + name[:6])
    r.lines.append('planet %d owner 1 pop 100 starbase 0' % n)
    r.lines.append('planetset %d env=50,50,50 scanner=31 defenses=0' % n)
    r.fleet(0, *XY[n], ships='%d:1' % d, planet=n)
    r.case('Z-' + name, name, 'kind', 'Destroyer with 1 %s at a planet with an unarmed, unshielded Orbital Fort' % name,
           'armor damage %d per hit on the fort (beam)' % stat(name, 'damage'), 'no damage (sapper)', ('beam0', n, stat(name, 'damage')))


# ------------------------------------------------------------------ CS-003-C2 single torpedoes (added after CS-003-C)
# CS-003-C could not tell 1 hit of 2d from 2 hits of d for Alpha, Juggernaut and
# Doomsday (6 torpedoes per salvo; Alpha's 5 dp is below the Hulk stack's damage
# resolution). Here each attacker fires 1 torpedo per round, so every hit record
# is one hit, at a single armed target (it does not disengage) whose armor
# resolves the damage.
r = run('CS-003-C2', 'single-torpedo salvos: Alpha Torpedo, Juggernaut and Doomsday Missile')
r.head.append('relation 0 1 2\nrelation 1 0 2')
r.head.append(tech26(0, 1).rstrip())
r.head.append('research 0 0\nresearch 1 0')
r.head.append('plan 0 0 5 1 0 1 = Enemies\nplan 1 0 5 1 0 1 = Enemies')
light = r.design(1, 'Cruiser, 2 Long Hump 6, empty, empty, 1 Laser, empty, empty, empty', 'Light')
heavy = r.design(1, 'Battleship, 4 Long Hump 6, empty, empty, 1 Laser, empty, empty, empty, empty, empty, empty, empty', 'Heavy')
for k, (name, tg, armor) in enumerate((('Alpha Torpedo', light, 700), ('Juggernaut Missile', heavy, 2000),
                                       ('Doomsday Missile', heavy, 2000))):
    t = BYNAME[name]
    d = r.design(0, 'Battleship, 4 Long Hump 6, empty, empty, 1 %s, empty, empty, empty, empty, empty, empty, empty' % name,
                 'T1-%02d' % t['index'])
    x, yy = (1060 + 80 * k, 1230)
    r.fleet(0, x, yy, '%d:1' % d)
    r.fleet(1, x, yy, '%d:1' % tg)
    dmg = t['stats']['damage']
    missile = t['stats']['kind'] == 'missile'
    D = 2 * dmg if missile else dmg
    r.case('T%02d' % t['index'], name, 'kind', 'Battleship with 1 %s vs one armed (1 Laser), unshielded ship, armor %d' % (name, armor),
           'every hit record is one hit of %d armor damage' % D, '%d' % (dmg if missile else 2 * dmg),
           ('torp1', x, yy, D, armor))


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    rows = []
    for r in RUNS:
        p = os.path.join(out, r.rid.lower().replace('-', '') + '.spec')
        open(p, 'w').write(r.spec())
        for c in r.cases:
            rows.append(c)
    with open(os.path.join(out, 'predictions.tsv'), 'w') as fh:
        fh.write('case\trow\tcolumn\tsetup\tpredicted\talternative\tcheck\n')
        for c in rows:
            fh.write('\t'.join([c['id'], c['row'], c['column'], c['what'], c['expect'], c['alt'], json.dumps(c['check'])]) + '\n')
    print(len(rows), 'cases in', len(RUNS), 'runs')


if __name__ == '__main__':
    main()
