#!/usr/bin/env python3
"""Write the OB- (universe objects) Combat Lab specs and their predictions.

Each run is a Combat Lab generation (tools/fleetlab/combatlab build +
pinned-turn) with minefields, packets, wormholes and a Mystery Trader
inserted as host-file object records (`thing` lines, docs/ORACLE.md
"Universe objects"). Cases in one run sit far enough apart not to interact;
gen.py checks that every minefield contains exactly the planets its case
names and no other case's fleets.

  python3 experiments/ob/gen.py OUTDIR      # writes OUTDIR/obNNN.spec
  python3 experiments/ob/gen.py --list      # case table with predictions

Predictions are the stars-decomp reading (O-n ids, private
docs/objects-predictions.md), written here as behavior before any OB run;
`alt` is the competing reading each case is built to rule out.
"""
import math, os, sys

XY = {0: (1045, 1291), 1: (1071, 1087), 2: (1090, 1295), 3: (1129, 1265), 4: (1143, 1103),
      5: (1146, 1180), 6: (1166, 1017), 7: (1166, 1382), 8: (1169, 1145), 9: (1208, 1297),
      10: (1224, 1359), 11: (1243, 1123), 12: (1245, 1158), 13: (1249, 1354), 14: (1268, 1317),
      15: (1281, 1064), 16: (1284, 1383), 17: (1306, 1060), 18: (1324, 1192), 19: (1342, 1123),
      20: (1348, 1290), 21: (1359, 1121), 22: (1368, 1292), 23: (1380, 1295)}

TECH26 = ''.join('tech 0 %s 26\n' % f for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))

COMMON = """\
relation 0 1 {rel01}
relation 1 0 {rel10}
{tech}research 0 0
research 1 0
# player 0 ship designs (all parts within tech 26)
design 0 0 Mini Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, empty, empty = Layer
design 0 1 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD
design 0 2 Destroyer, 1 Long Hump 6, 1 Gatling Gun, 1 Gatling Gun, empty, empty, empty, empty = Gatling DD
design 0 3 Destroyer, 1 Long Hump 6, 1 Mini Gun, empty, empty, empty, empty, empty = Mini Gun DD
design 0 4 Destroyer, 1 Long Hump 6, 1 Pulsed Sapper, 1 Pulsed Sapper, empty, empty, empty, empty = Sapper DD
design 0 5 Mini Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, 2 Heavy Dispenser 50, empty = Layer2
design 0 6 Frigate, 1 Long Hump 6, empty, 3 Speed Trap 20, empty = Trap Frigate
design 0 7 Frigate, 1 Long Hump 6, empty, 2 Mine Dispenser 40, empty = MD40 Frigate
design 0 8 Frigate, 1 Long Hump 6, empty, 1 Multi Contained Munition, empty = MCM Frigate
design 0 9 Super Freighter, 3 Long Hump 6, empty, empty, empty = Super Freighter
design 0 10 Scout, 1 Long Hump 6, empty, empty = Scout
# player 0 starbase designs: 0 = the 2400 homeworld design, unchanged
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase
sbdesign 0 1 Orbital Fort, empty, 2 Laser, empty, empty, empty = Laser Fort
sbdesign 0 2 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Catcher 7
# plans: tactic 4, primary any, no secondary, attack who
plan 0 0 4 1 0 1 = Enemies
plan 0 1 4 1 0 0 = Nobody
plan 0 2 4 1 0 2 = Neutral and enemies
plan 0 3 4 1 0 3 = Everyone
plan 0 4 4 1 0 5 = Player 1 only
"""


class Run:
    def __init__(self, rid, title, rel01=2, rel10=2, tech=TECH26, extra=''):
        self.rid, self.title = rid, title
        self.rel01, self.rel10, self.tech, self.extra = rel01, rel10, tech, extra
        self.lines, self.cases, self.fields, self.fleetpos = [], [], [], []
        self.nfleet = {0: 0, 1: 0}
        self.nthing = {}
        self.scan = None

    def fleet(self, owner, x, y, ships, plan=0, extra='', planet=None, fuel=50):
        fid = self.nfleet[owner]
        self.nfleet[owner] += 1
        at = ('planet %d ' % planet if planet is not None else '') + 'at %d %d' % (x, y)
        self.lines.append('fleet %d %d %s ships %s plan %d fuel %d %s' % (owner, fid, at, ships, plan, fuel, extra))
        self.fleetpos.append((owner, x, y))
        return fid

    def thing(self, kind, owner, rest):
        n = self.nthing.get((kind, owner), 0)
        self.nthing[(kind, owner)] = n + 1
        if kind in ('wormhole', 'trader'):
            self.lines.append('thing %s %d %s' % (kind, n, rest))
        else:
            self.lines.append('thing %s %d %d %s' % (kind, owner, n, rest))
        return n

    def field(self, owner, x, y, count, planets=(), kind='std', det=False):
        n = self.thing('minefield', owner, '%d %d %d kind %s%s' % (x, y, count, kind, ' det' if det else ''))
        self.fields.append((owner, x, y, count, set(planets)))
        return n

    def case(self, cid, pred, what, expect, alt='', check=None):
        self.cases.append(dict(id='%s-%s' % (self.rid, cid), pred=pred, what=what, expect=expect, alt=alt,
                               check=check))

    def validate(self):
        for owner, x, y, count, planets in self.fields:
            inside = {n for n, (a, b) in XY.items() if (a - x) ** 2 + (b - y) ** 2 <= count}
            assert inside == planets, (self.rid, x, y, count, inside, planets)

    def spec(self):
        self.validate()
        head = '# %s: %s (experiments/ob/gen.py)\n' % (self.rid, self.title)
        return head + COMMON.format(rel01=self.rel01, rel10=self.rel10, tech=self.tech) + self.extra + \
            '\n'.join(self.lines) + '\n'


RUNS = []


def run(*a, **k):
    r = Run(*a, **k)
    RUNS.append(r)
    return r


# ---------------------------------------------------------------- OB-001 sweeping
r = run('OB-001', 'minefield sweeping by fleets and starbases (mutual enemies)')
# player 1 fields of 1000 mines decay 2% (no planets inside) to 980 before sweeping
r.field(1, 1050, 1030, 1000); r.fleet(0, 1070, 1030, '2:1')
r.case('A', 'O-8', 'Gatling DD (rating 992) 20 ly from the centre of a 1000 field',
       'field 399', 'field removed (0)', ('field', 1, 1050, 1030, 399))
r.field(1, 1050, 1180, 1000); r.fleet(0, 1050, 1180, '1:1')
r.case('B', 'O-9', 'Laser DD (2 lasers, rating 20) at the centre', 'field 960', '',
       ('field', 1, 1050, 1180, 960))
r.field(1, 1050, 1250, 1000); r.fleet(0, 1050, 1250, '3:1')
r.case('C', 'O-9', 'Mini Gun DD (gatling, swept as range 4: 13*16 = 208)', 'field 772',
       '928 if the Mini Gun swept at its range 2', ('field', 1, 1050, 1250, 772))
r.field(1, 1210, 1220, 1000); r.fleet(0, 1210, 1220, '4:1')
r.case('D', 'O-9', 'Sapper DD (2 Pulsed Sappers) at the centre', 'field 980 (sappers do not sweep)',
       'field reduced', ('field', 1, 1210, 1220, 980))
r.field(1, 1280, 1240, 1000); r.fleet(0, 1280, 1240, '1:1', plan=1)
r.case('E', 'O-10', 'Laser DD with plan "attack nobody" at the centre', 'field 980', 'field 960',
       ('field', 1, 1280, 1240, 980))
r.field(1, 1370, 1220, 1000); r.fleet(0, 1370, 1220, '1:1'); r.fleet(0, 1370, 1220, '1:1')
r.case('F', 'O-11', 'two separate Laser DD fleets at the centre', 'field 940', '960 if they shared',
       ('field', 1, 1370, 1220, 940))
r.field(1, 1080, 1360, 1000); r.fleet(0, 1080, 1360, '1:3')
r.case('G', 'O-9', 'one fleet of 3 Laser DDs at the centre', 'field 920', '960',
       ('field', 1, 1080, 1360, 920))
r.field(1, 1220, 1060, 1000, kind='bump'); r.fleet(0, 1220, 1060, '1:1')
r.case('H', 'O-9', 'speed-bump field 1000 (decays 2% to 980), Laser DD at the centre',
       'field 974 (a third of 20)', '960', ('field', 1, 1220, 1060, 974))
r.field(1, 1360, 1040, 2000); r.fleet(0, 1360, 1040, '2:1')
r.case('I', 'O-9', 'Gatling DD at the centre of a 2000 field (decays to 1960)',
       'field 968 (2*31*16 = 992)', '1712 if gatlings swept at range 2', ('field', 1, 1360, 1040, 968))
r.extra += 'planet 5 owner 0 pop 1000 starbase 1\nplanetset 5 mines=0 factories=0 defenses=0\n'
r.field(1, 1130, 1200, 1000, planets=[5])
r.case('J', 'O-9', 'player 0 planet 5 with a Laser Fort (2 lasers) inside a 1000 field (d^2 = 656)',
       'field 900 (starbase range +1: 2*10*4 = 80)', '960 without the +1', ('field', 1, 1130, 1200, 900))

# ---------------------------------------------------------------- OB-002 decay, laying, detonation
r = run('OB-002', 'minefield decay, laying and detonation (mutual enemies)')
r.field(1, 1050, 1030, 1000)
r.case('A', 'O-5', 'player 1 field 1000, no planets', 'field 980', '', ('field', 1, 1050, 1030, 980))
r.field(1, 1050, 1180, 100)
r.case('B', 'O-5', 'player 1 field 100', 'field 90 (minimum decay 10)', '98', ('field', 1, 1050, 1180, 90))
r.field(1, 1050, 1250, 100, kind='bump')
r.case('C', 'O-5', 'player 1 speed-bump field 100', 'field 98 (no minimum 10)', '90',
       ('field', 1, 1050, 1250, 98))
r.field(1, 1244, 1140, 1000, planets=[11, 12])
r.case('D', 'O-5', 'player 1 field 1000 containing unowned planets 11 and 12', 'field 900 (10%)', '980',
       ('field', 1, 1244, 1140, 900))
r.field(1, 1156, 1140, 2000, planets=[4, 5, 8])
r.case('E', 'O-5', 'player 1 field 2000 containing its own homeworld 8 and unowned 4, 5',
       'field 1720 (14%: owners do not matter)', '1880 if only unowned planets counted',
       ('field', 1, 1156, 1140, 1720))
r.fleet(0, 1210, 1220, '0:1', extra='task lay')
r.case('F', 'O-1/O-7', 'Mini Mine Layer (2 Mine Dispenser 40), lay indefinitely, empty space',
       'new player 0 field 160 at the fleet (laid after decay)', '150 if decayed the same turn',
       ('field', 0, 1210, 1220, 160))
r.field(0, 1280, 1240, 400)
r.fleet(0, 1290, 1240, '0:1', extra='task lay')
r.case('G', 'O-3', 'layer 10 ly east of the centre of its own 400 field (decays to 390)',
       'one field 550 centred at x+2 (1282,1240)', 'a second field at the fleet',
       ('fieldat', 0, 1282, 1240, 550))
r.fleet(0, 1370, 1220, '0:3', extra='task lay')
r.case('H', 'O-1', 'fleet of 3 Mini Mine Layers', 'field 480', '', ('field', 0, 1370, 1220, 480))
r.fleet(0, 1080, 1360, '5:1', extra='task lay')
r.case('I', 'O-1', 'Mini Mine Layer with 2 Mine Dispenser 40 + 2 Heavy Dispenser 50',
       'standard field 160 and heavy field 200 at the fleet', 'one mixed field',
       ('fields', 0, 1080, 1360, {'0': 160, '1': 200}))
r.fleet(0, 1220, 1060, '6:1', extra='task lay')
r.case('J', 'O-1', 'Frigate with 3 Speed Trap 20 (no layer hull)', 'speed-bump field 60', '120 if doubled',
       ('fields', 0, 1220, 1060, {'2': 60}))
r.fleet(0, 1360, 1040, '7:1', extra='task lay')
r.case('K', 'O-1', 'Frigate with 2 Mine Dispenser 40', 'standard field 80', '160',
       ('fields', 0, 1360, 1040, {'0': 80}))
r.fleet(0, 1130, 1220, '8:1', extra='task lay')
r.case('L', 'O-1', 'Frigate with 1 Multi Contained Munition', 'standard field 40 (if the part survives)',
       'no field', ('fields', 0, 1130, 1220, {'0': 40}))
# detonation: player 0 field set to detonate, its own warships, its own layer and enemy freighters inside
r.field(0, 1060, 1100 + 20, 1000, det=True)
r.fleet(0, 1060, 1120, '1:5')
r.fleet(0, 1066, 1120, '0:1')
r.fleet(1, 1060, 1135, '3:5')
r.case('M', 'O-13', 'player 0 detonating field 1000 with 5 own Laser DDs, own Mini Mine Layer, 5 enemy '
       'Medium Freighters inside', 'DDs 50% armor damage, layer undamaged, freighters 80% (100 per ship); '
       'field 730 (27%)', 'own warships exempt; field also shrunk by hits',
       ('detonate', 1060, 1120))
r.fleet(0, 1300, 1310, '0:1', extra='task lay 0')
r.case('N', 'O-4', 'layer with years word 0', 'field 160 and waypoint task cleared', 'task kept',
       ('laytask', 0, 1300, 1310, 160))

# ---------------------------------------------------------------- OB-003 packets
r = run('OB-003', 'mass-driver packets in flight and on impact (player 0 packets, mutual enemies)')
r.extra += ('planet 9 owner 0 pop 1000 starbase 2\nplanetset 9 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0\n'
            'planet 14 owner 0 pop 1000 starbase 2\nplanetset 14 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0\n'
            'planet 10 owner 0 pop 1000 starbase none\nplanetset 10 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0\n'
            'planet 20 owner 1 pop 1000 starbase none\nplanetset 20 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0\n'
            'planet 22 owner 1 pop 500 starbase none\nplanetset 22 mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0\n'
            'planet 18 owner 1 pop 1000 starbase none\nplanetset 18 mines=0 factories=0 defenses=50 fe=0 bo=0 ge=0\n')
r.thing('packet', 0, '1020 1291 0 10 1000 0 0')
r.case('A', 'O-21', '1000 kT ironium, warp 10, 25 ly from unowned planet 0', 'planet 0 surface +111 Ir',
       '+1000', ('surface', 0, (111, 0, 0)))
r.thing('packet', 0, '1196 1017 6 10 300 200 100')
r.case('B', 'O-21', '300/200/100 kT, warp 10, into unowned planet 6', 'surface +33/+22/+11', '+300/200/100',
       ('surface', 6, (33, 22, 11)))
r.thing('packet', 0, '1254 1354 13 10 100 0 0 class 1')
r.case('C', 'O-20', 'class-1 packet (10%/yr) of 100 kT arriving with a 5% share (5 ly at warp 10) into '
       'unowned planet 13', 'loses the 10 kT minimum: 90 arrive, surface +9', '+11 with no minimum',
       ('surface', 13, (9, 0, 0)))
r.thing('packet', 0, '1208 1347 9 10 1000 0 0')
r.case('D', 'O-21/O-22', 'warp 10 packet 1000 kT into own planet 9 with a Mass Driver 7 fort (catch 49%)',
       'surface +546; damage 318: pop 1000 -> 682 (units of 100)', 'surface +1000, no damage',
       ('planet', 9, dict(surface=(546, 0, 0), pop=682)))
r.thing('packet', 0, '1268 1367 14 7 1000 0 0')
r.case('E', 'O-21', 'warp 7 packet into own planet 14 with a Mass Driver 7 fort (fully caught)',
       'surface +1000, pop 1000 unchanged', '', ('planet', 14, dict(surface=(1000, 0, 0), pop=1000)))
r.thing('packet', 0, '1348 1340 20 10 1000 0 0')
r.case('F', 'O-22', 'warp 10, 1000 kT into enemy planet 20 (no starbase, no defenses, pop 1000)',
       'pop 375 (kill 625 units), surface +111', '', ('planet', 20, dict(surface=(111, 0, 0), pop=375)))
r.thing('packet', 0, '1368 1342 22 10 1000 0 0')
r.case('G', 'O-23', 'the same packet into enemy planet 22 with pop 500', 'planet uninhabited (owner none)',
       'pop > 0', ('planet', 22, dict(owner=-1)))
r.thing('packet', 0, '1224 1309 10 10 1000 0 0')
r.case('H', 'O-24', 'player 0 packet into its own planet 10 (no starbase, pop 1000)', 'pop 375',
       'no damage to own planets', ('planet', 10, dict(pop=375)))
r.thing('packet', 0, '1324 1242 18 10 1000 0 0')
r.case('I', 'O-22', 'warp 10, 1000 kT into enemy planet 18 with 50 SDI defenses, pop 1000',
       'damage 625 scaled by defenses to 418: pop 582, defenses 30', 'defenses ignored: pop 375',
       ('planet', 18, dict(pop=582, defenses=30)))
r.thing('packet', 0, '1130 1240 23 10 1000 0 0 class 2')
r.case('J', 'O-19/O-20', 'class-2 packet (25%/yr) in flight, 250 ly from planet 23, moved bit clear',
       'moves 100 ly to (1228,1261) (within 1 ly); 750 kT left', 'half speed or no move',
       ('packetat', 0, 1228, 1261, 750))
r.thing('packet', 0, '1130 1200 23 10 1000 0 0 class 3 moved')
r.case('K', 'O-19/O-20', 'class-3 packet (50%/yr), 250 ly+ from planet 23, moved bit set',
       'moves 100 ly; 500 kT left (bit meaning measured)', '', ('packetat', 0, None, None, 500))

# ---------------------------------------------------------------- OB-004 Mystery Trader
r = run('OB-004', 'Mystery Trader encounters (player 1 at tech 3, sum 18)')
r.extra += 'design 1 0 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter\n'
r.thing('trader', 0, '1020 1210 1380 1210 8')
# MT moves 64 ly to (1084,1210) before fleets move; every fleet below ends the turn there
r.fleet(0, 1084, 1210, '9:2', extra='cargo 4999 0 0 100', fuel=2000)
r.case('A', 'O-34', 'stationary player 0 fleet with 4999 kT minerals and 100 colonists at the MT',
       'fleet kept, no message (stationary)', '', ('fleet', 0, 0, 'kept'))
r.fleet(0, 1064, 1210, '9:2', extra='cargo 2000 1999 1000 0 to 1084 1210 warp 5', fuel=2000)
r.case('B', 'O-34', 'player 0 fleet with 4999 kT that moves 20 ly onto the MT', 'fleet kept, message 0x108',
       '', ('fleet', 0, 1, 'kept'))
r.fleet(0, 1084, 1210, '9:2', extra='cargo 2000 2000 1000 0', fuel=2000)
r.case('C', 'O-34', 'stationary player 0 fleet with exactly 5000 kT (tech 26: reward is a part or nothing)',
       'fleet removed', 'fleet kept', ('fleet', 0, 2, 'gone'))
r.fleet(1, 1084, 1210, '0:24', extra='cargo 5000 0 0 0')
r.case('D', 'O-34/O-36', 'player 1 fleet of 24 Medium Freighters with 5000 kT; MT item research',
       'fleet removed; player 1 gains 6 tech levels in total', 'fleet kept', ('mtgift', 1, 0, 6))
r.fleet(1, 1084, 1210, '0:24', extra='cargo 5000 0 0 0')
r.case('E', 'O-35', 'second player 1 fleet with 5000 kT at the same MT, same turn', 'fleet kept, message 0x118',
       'removed', ('fleet', 1, 1, 'kept'))

# ---------------------------------------------------------------- OB-005 wormholes
r = run('OB-005', 'wormhole jiggle and transit (multi-year; mutual enemies)')
r.thing('wormhole', 0, '1050 1180 1 0')
r.thing('wormhole', 0, '1290 1240 0 0')
r.case('A', 'O-28/O-29', 'class-0 pair, years 0', 'no jump; each end moves at most 12 ly per axis, '
       'years 1', '', ('worm', 0, 1050, 1180))
r.thing('wormhole', 0, '1080 1360 3 2 years 30')
r.thing('wormhole', 0, '1360 1040 2 2 years 30')
r.case('B', 'O-28', 'class-2 pair, years 30 (6%/yr)', 'jiggle (94%) or jump; recorded per stream', '',
       ('worm', 2, 1080, 1360))
r.fleet(0, 1050, 1210, '10:1', extra='to 1050 1180 thing 0x4000 warp 6')
r.case('C', 'O-31/O-40', 'scout 30 ly from wormhole 0 targeting it at warp 6',
       'ends on wormhole 1\'s pre-move position (1290,1240)', 'stops at wormhole 0',
       ('fleetat', 0, 0, 1290, 1240))
r.fleet(0, 1080, 1330, '10:1', extra='to 1080 1360 thing 0x4002 warp 4')
r.case('D', 'O-31', 'scout 30 ly from wormhole 2 at warp 4 (16 ly)', 'moves 16 ly, no transit', '',
       ('fleetat', 0, 1, 1080, 1346))


# ---------------------------------------------------------------- OB-006 new games (O-27)
# Games made by `stars.exe -a DEF` (tools/fleetlab/new-game); not Combat Lab.
# size 0 tiny .. 4 huge; flags line: the fourth flag is "no random events".
NEWGAMES = []
for size in range(5):
    for seed in (11, 22, 33):
        NEWGAMES.append(dict(id='OB-006-%s%d' % ('TSMLH'[size], seed), size=size, seed=seed, events=True,
                             name='o6%s%d' % ('tsmlh'[size], seed),
                             expect='%d..%d wormhole pairs, each end class 0, 1 or 2 with years 0'
                             % ([0, 1, 1, 3, 4][size], [2, 3, 5, 6, 8][size])))
for size in (0, 4):
    for seed in (11, 22, 33):
        NEWGAMES.append(dict(id='OB-006-%s%dN' % ('TSMLH'[size], seed), size=size, seed=seed, events=False,
                             name='o6%s%dn' % ('tsmlh'[size], seed),
                             expect='no wormholes (random events off)'))
PAIRS = [(0, 2), (1, 3), (1, 5), (3, 6), (4, 8)]


def newgame_def(g):
    name = g['name']                             # DOS 8.3: e.g. o6h11n
    return '\r\n'.join([
        name.upper(), '%d 1 1 %d' % (g['size'], g['seed']),
        '0 0 0 %d 0 0 0' % (0 if g['events'] else 1),
        '2', 'pg000.r1', '# 1 0',
        '1 60', '0 26 4', '0 5000', '0 100', '0 100', '0 100', '0 100', '1 50',
        '%s.xy' % name]) + '\r\n'


# ---------------------------------------------------------------- OB-007 neutral relations
r = run('OB-007', 'sweeping and relations: both players neutral; player 1 plan 0 attacks enemies only',
        rel01=0, rel10=0, extra='plan 1 0 4 1 0 1 = Enemies only\n')
r.field(1, 1050, 1180, 1000); r.fleet(0, 1050, 1180, '1:1', plan=0)
r.case('A', 'O-10', 'Laser DD with plan "enemies" in a neutral player\'s field', 'field 980 (no sweep)', '960',
       ('field', 1, 1050, 1180, 980))
r.field(1, 1050, 1250, 1000); r.fleet(0, 1050, 1250, '1:1', plan=2)
r.case('B', 'O-10', 'Laser DD with plan "neutral and enemies" in a neutral player\'s field', 'field 960', '980',
       ('field', 1, 1050, 1250, 960))
r.extra += 'planet 5 owner 0 pop 1000 starbase 1\nplanetset 5 mines=0 factories=0 defenses=0\n'
r.field(1, 1130, 1200, 1000, planets=[5])
r.case('C', 'O-10', 'player 0 Laser Fort (planet 5) inside a neutral player\'s 1000 field (1 planet: 6% decay)',
       'field 860 (940 - 80: starbases sweep any non-friend field)', '940', ('field', 1, 1130, 1200, 860))
r.fleet(0, 1169, 1145, '0:1', planet=8, extra='task lay')
r.case('D', 'O-12', 'player 0 layer lays 160 at player 1\'s homeworld (Space Station, 32 lasers: rating 1280)',
       'no player 0 field left (laid, then swept the same turn)', 'field 160', ('field', 0, 1169, 1145, 0))
r.field(1, 1210, 1220, 1000); r.fleet(0, 1210, 1220, '1:1', plan=3)
r.case('E', 'O-10', 'Laser DD with plan "everyone" in a neutral player\'s field', 'field 960', '980',
       ('field', 1, 1210, 1220, 960))

# ---------------------------------------------------------------- OB-008 friend relations
r = run('OB-008', 'sweeping and relations: player 0 counts player 1 as a friend', rel01=1, rel10=0)
r.extra += 'planet 5 owner 0 pop 1000 starbase 1\nplanetset 5 mines=0 factories=0 defenses=0\n'
r.field(1, 1130, 1200, 1000, planets=[5])
r.case('A', 'O-10', 'player 0 Laser Fort inside a friend\'s 1000 field (6% decay)', 'field 940 (no sweep)', '860',
       ('field', 1, 1130, 1200, 940))
r.field(1, 1050, 1180, 1000); r.fleet(0, 1050, 1180, '1:1', plan=3)
r.case('B', 'O-10', 'Laser DD with plan "everyone" in a friend\'s field', 'measured (does "everyone" include friends?)',
       '', ('fieldobs', 1, 1050, 1180))
r.field(1, 1050, 1250, 1000); r.fleet(0, 1050, 1250, '1:1', plan=2)
r.case('C', 'O-10', 'Laser DD with plan "neutral and enemies" in a friend\'s field', 'field 980', '960',
       ('field', 1, 1050, 1250, 980))
r.field(1, 1210, 1220, 1000); r.fleet(0, 1210, 1220, '1:1', plan=4)
r.case('D', 'O-10', 'Laser DD with plan "player 1 only" in a friend\'s field', 'measured', '',
       ('fieldobs', 1, 1210, 1220))

# ---------------------------------------------------------------- OB-009 packet damage with growth controlled
# Every target planet gets environment 50/50/50 (100% for both identical races) and carry 0, so a planet
# that keeps population P after the impact ends the year at P + floor(15 P / 100) (TK corpus). Impacts
# happen before growth.
PLAIN = 'mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 env=50,50,50 excess=0'


def grown(p):
    return p + 15 * p // 100


r = run('OB-009', 'packet impacts with population growth controlled (player 0 packets, mutual enemies)')
for n, owner, pop, sb, extra in ((9, 0, 1000, 2, ''), (14, 0, 1000, 2, ''), (10, 0, 1000, None, ''),
                                 (16, 0, 1000, None, ''), (20, 1, 1000, None, ''), (22, 1, 500, None, ''),
                                 (18, 1, 1000, None, ' defenses=50'), (21, 1, 1000, None, '')):
    r.extra += 'planet %d owner %d pop %d starbase %s\nplanetset %d %s%s\n' % (
        n, owner, pop, sb if sb is not None else 'none', n, PLAIN.replace(' defenses=0', '') if extra else PLAIN, extra)
r.case('A', 'control', 'player 0 planet 16, pop 1000, no packet', 'pop %d' % grown(1000), '',
       ('planet', 16, dict(pop=grown(1000))))
r.case('B', 'control', 'player 1 planet 21, pop 1000, no packet', 'pop %d' % grown(1000), '',
       ('planet', 21, dict(pop=grown(1000))))
r.thing('packet', 0, '1208 1347 9 10 1000 0 0')
r.case('C', 'O-21/O-22', 'warp 10, 1000 kT into own planet 9 with a Mass Driver 7 fort (catch 49%)',
       'surface +546; 318 units killed: pop 682 -> %d' % grown(682), 'no damage: %d' % grown(1000),
       ('planet', 9, dict(surface=(546, 0, 0), pop=grown(682))))
r.thing('packet', 0, '1268 1347 14 7 1000 0 0')
r.case('D', 'O-21', 'warp 7 packet 30 ly from own planet 14 with a Mass Driver 7 fort (fully caught)',
       'surface +1000, pop %d (no damage)' % grown(1000), '', ('planet', 14, dict(surface=(1000, 0, 0), pop=grown(1000))))
r.thing('packet', 0, '1224 1309 10 10 1000 0 0')
r.case('E', 'O-24', 'own packet into own planet 10 (no starbase, pop 1000)', 'pop 375 -> %d' % grown(375),
       'no damage', ('planet', 10, dict(pop=grown(375))))
r.thing('packet', 0, '1348 1340 20 10 1000 0 0')
r.case('F', 'O-22', 'warp 10, 1000 kT into enemy planet 20 (no defenses, pop 1000)', 'pop 375 -> %d' % grown(375),
       '', ('planet', 20, dict(pop=grown(375))))
r.thing('packet', 0, '1368 1342 22 10 1000 0 0')
r.case('G', 'O-23', 'the same into enemy planet 22, pop 500', 'uninhabited', '', ('planet', 22, dict(owner=-1)))
r.thing('packet', 0, '1324 1242 18 10 1000 0 0')
r.case('H', 'O-22', 'warp 10, 1000 kT into enemy planet 18 with 50 SDI (tech 3)',
       'damage 418: pop 582 -> %d, defenses 30' % grown(582), 'defenses ignored: %d' % grown(375),
       ('planet', 18, dict(pop=grown(582), defenses=30)))

# ---------------------------------------------------------------- OB-010 minefield hits (random)
r = run('OB-010', 'minefield hits while moving (player 1 fields, player 0 fleets of 5 Laser DDs, warp 9)')
for i, (x, y) in enumerate(((1050, 1030), (1050, 1180), (1080, 1360), (1360, 1040), (1370, 1220))):
    r.field(1, x, y, 1000, kind='heavy')
    r.fleet(0, x - 15, y, '1:5', extra='to %d %d warp 9' % (x + 15, y), fuel=1400)
    r.case('H%d' % i, 'O-14', 'warp-9 fleet moving only 30 ly inside a heavy field (checked at warp 6 = safe)',
           'never hit: ends at (%d,%d), undamaged' % (x + 15, y), '1-0.97^30 = 60%% hit chance if warp 9 counted',
           ('fleetat', 0, i, x + 15, y))
r.field(1, 1220, 1230, 3000)
r.fleet(0, 1160, 1230, '1:5', extra='to 1241 1230 warp 9', fuel=1400)
r.case('S', 'O-14/O-15', 'warp-9 fleet crossing 76 ly of a standard 3000 field (15 per mille per ly)',
       'no hit (32%): at (1241,1230), field 2940; or a stop inside the field, 50% damage on each DD and '
       'field 2891 (hit -50, then 2% decay)', '2890 if decay came first', ('minehit', 0, 5, 1220, 1230))

# ---------------------------------------------------------------- OB-015/016 decay cap and SD decay
r = run('OB-015', 'decay cap: a 40000 field over 22 planets')
r.field(1, 1200, 1200, 40000, planets=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22])
r.case('A', 'O-6', 'player 1 field 40000 containing 22 planets', 'field 20000 (50% cap)', '',
       ('field', 1, 1200, 1200, 20000))
r = run('OB-016', 'SD owner decay: the same 40000 field owned by a Space Demolition player 1', extra='prt 1 5\n')
r.field(1, 1200, 1200, 40000, planets=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22])
r.case('A', 'O-5/O-6', 'SD player 1 field 40000 with 22 planets', 'field 30400 (1 per planet + 2 = 24%)', '20000',
       ('field', 1, 1200, 1200, 30400))


# ---------------------------------------------------------------- OB-011..014 scanning of objects (S-17..S-19)
# Viewer: player 1 (tech 3). Its homeworld scanner is removed (`planet 8 scanner none`) and it keeps
# only the fleets listed, so every detection comes from a known scanner. check.py applies the S-17..S-19
# rules to the generated host file's object positions (wormholes jiggle and packets move before the
# files are written) and compares the result with the objects in player 1's .M file.
SCOUT1 = 'design 1 1 Scout, 1 Long Hump 6, 1 Rhino Scanner, empty = Rhino Scout\n'


def pkt_after(x, y, dest, warp):
    """Position of a packet after one full-speed year toward planet dest (or arrival)."""
    tx, ty = XY[dest]
    dx, dy = tx - x, ty - y
    d = math.hypot(dx, dy)
    sp = warp * warp
    if int(d) <= sp:
        return None
    rnd = lambda v: int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    return x + rnd(sp * dx / d), y + rnd(sp * dy / d)


r = run('OB-011', 'scanning of objects by a JOAT viewer with Rhino scouts (R 50, no penetrating range)',
        extra='planet 8 scanner none\n' + SCOUT1)
# JOAT Scouts carry a built-in 20*elec / 10*elec scanner (SCANNING.md); with the Rhino (50/0) the
# fleet ranges combine as fourth powers: R = (60^4 + 50^4)^(1/4) = 66, P = 30 at electronics 3.
r.scan = dict(viewer=1, mask=2, R=66, P=30)
for (sx, sy) in ((1050, 1040), (1050, 1180), (1050, 1260), (1110, 1360), (1360, 1040), (1370, 1230),
                 (1220, 1060), (1300, 1150)):
    r.fleet(1, sx, sy, '1:1')
r.field(0, 1062, 1040, 100);  r.case('A', 'S-17', 'field 100 at d=12 from a scout (not inside)', 'seen (d <= R/4)', '', ('scan',))
r.field(0, 1063, 1180, 100);  r.case('B', 'S-17', 'field 100 at d=13', 'not seen', '', ('scan',))
r.field(0, 1080, 1260, 1000); r.case('C', 'S-17', 'field 1000 at d=30 (scout inside)', 'seen', '', ('scan',))
r.field(0, 1140, 1360, 800);  r.case('D', 'S-17', 'field 800 at d=30 (scout outside after decay to 784)', 'not seen', '', ('scan',))
r.thing('minefield', 0, '1360 1080 100 known 2'); r.fields.append((0, 1360, 1080, 100, set()))
r.case('E', 'S-17', 'field 100 already known to player 1, d=40', 'seen (full R)', '', ('scan',))
r.thing('minefield', 0, '1370 1281 100 known 2'); r.fields.append((0, 1370, 1281, 100, set()))
r.case('F', 'S-17', 'field 100 already known, d=51', 'not seen', '', ('scan',))
r.thing('wormhole', 0, '1220 1066 1 0'); r.thing('wormhole', 0, '1110 1110 0 0')
r.case('G', 'S-17', 'wormhole 6 ly from a scout before its jiggle; partner far from every scanner',
       'each end seen iff d <= R/4 after the jiggle', '', ('scan',))
r.thing('wormhole', 0, '1210 1230 3 0 seen 2'); r.thing('wormhole', 0, '1300 1310 2 0')
r.case('H', 'S-17', 'wormhole already known to player 1, far from scanners; its partner unknown and far',
       'known end seen, partner not', '', ('scan',))
r.thing('packet', 0, '1300 1105 6 5 100 0 0')   # moves 25 ly toward planet 6
r.case('I', 'S-17', 'packet near the (1300,1150) scout after its move', 'seen iff d <= R', '', ('scan',))
r.thing('trader', 0, '1020 1100 1380 1100 8')
r.case('J', 'S-18', 'Mystery Trader ending the move at (1084,1100), 69+ ly from every scanner', 'seen anyway', '',
       ('scan',))

r = run('OB-012', 'Packet Physics viewer: every packet, and its own packet as a scanner (S-19)',
        extra='prt 1 6\nlrt 1 0x1b80\nplanet 8 scanner none\n')
r.scan = dict(viewer=1, mask=2, ppacket=True)
# player 1 packet, warp 5, moving from (1100,1240) toward planet 18: about 25 ly
r.thing('packet', 1, '1100 1240 18 5 100 0 0')
q = pkt_after(1100, 1240, 18, 5)
r.fleet(0, q[0], q[1] - 20, '10:1'); r.fleet(0, q[0], q[1] + 30, '10:1')
r.case('A', 'S-19', 'player 0 scouts 20 and 30 ly from player 1\'s moving warp-5 packet',
       'the first seen (penetrating range 25), the second not', '', ('scanfleets', [(0, 0, True), (0, 1, False)]))
r.field(0, q[0] - 20, q[1], 100); r.field(0, q[0] + 30, q[1], 100)
r.case('B', 'S-19', 'player 0 fields 20 and 30 ly from the packet', 'first seen, second not', '', ('scan',))
r.thing('packet', 0, '1380 1040 15 5 100 0 0')
r.case('C', 'S-19', 'player 0 packet far from every player 1 scanner', 'seen (PP sees every packet)', '', ('scan',))

r = run('OB-013', 'Interstellar Traveler viewer: planets with stargates within its gate range',
        extra='prt 1 7\nlrt 1 0x1b80\ntech 1 prop 5\ntech 1 con 5\nplanet 8 scanner none\n'
              'sbdesign 1 0 Space Station, 1 Stargate 100/250, 8 Laser, 8 Mole-skin Shield, 8 Laser, '
              '8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Gate\n'
              'sbdesign 0 3 Orbital Fort, 1 Stargate 100/250, empty, empty, empty, empty = Gate Fort\n'
              'planet 23 owner 0 pop 1000 starbase 3\nplanetset 23 mines=0 factories=0 defenses=0 scanner=31\n'
              'planet 15 owner 0 pop 1000 starbase 1\nplanetset 15 mines=0 factories=0 defenses=0 scanner=31\n'
              'planet 11 owner 0 pop 1000 starbase 3\nplanetset 11 mines=0 factories=0 defenses=0 scanner=31\n')
r.case('A', 'IT gate', 'player 0 planet 11 with a gate fort, 75 ly from player 1\'s gate (range 250)',
       'player 1 sees planet 11 at level 3 or more', '', ('planetlevel', 1, 11, 3))
r.case('B', 'IT gate', 'player 0 planet 23 with a gate fort, 259 ly away', 'below level 3', '', ('planetlevel', 1, 23, -3))
r.case('C', 'IT gate', 'player 0 planet 15 with a starbase but no gate, 138 ly away', 'below level 3', '',
       ('planetlevel', 1, 15, -3))

r = run('OB-014', 'Space Demolition player 1: minefield detection, decay and laying while moving',
        extra='prt 1 5\nplanet 8 scanner none\n'
              'design 1 0 Mini Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, empty, empty = SD Layer\n')
r.field(1, 1244, 1140, 1000, planets=[11, 12])
r.case('A', 'O-5', 'SD player 1 field 1000 containing planets 11 and 12', 'field 960 (1 per planet + 2 = 4%)', '900',
       ('field', 1, 1244, 1140, 960))
r.fleet(0, 1244, 1140, '10:1'); r.fleet(0, 1243, 1123, '10:1', planet=11); r.fleet(0, 1110, 1360, '10:1')
r.case('B', 'S-17/SD', 'player 0 scouts: deep space inside the SD field, orbiting planet 11 inside it, '
       'and far away', 'only the deep-space one appears in player 1\'s file', '',
       ('scanfleets', [(0, 0, True), (0, 1, False), (0, 2, False)]))
r.fleet(1, 1050, 1180, '0:1', extra='to 1050 1250 warp 5 task lay', fuel=400)
r.case('C', 'O-2', 'SD layer moving 25 ly (warp 5) toward a lay-mines waypoint', 'new field 80 at (1050,1205)',
       'nothing while moving', ('field', 1, 1050, 1205, 80))
r.fleet(0, 1360, 1040, '0:1', extra='task lay to 1360 1100 warp 5', fuel=400)
r.case('D', 'O-2', 'non-SD (player 0) layer with lay on waypoint 0 that moves 25 ly', 'no field', '160 or 80',
       ('nofield', 0, 1360, 1040, 1360, 1065))


# ---------------------------------------------------------------- OB-017 known wormholes and packet marks
# After OB-011 (a wormhole known to player 1 but out of range was not in its file). Player 0 has no
# scanner at all (homeworld scanner removed, no fleets); player 1 has two Rhino Scouts (R 66, P 30).
r = run('OB-017', 'known wormholes in range, and packet visibility marks carried between viewers',
        extra='planet 8 scanner none\nplanet 17 scanner none\n' + SCOUT1)
r.scan = dict(viewer=1, mask=2, R=66, P=30)
r.fleet(1, 1050, 1180, '1:1'); r.fleet(1, 1360, 1040, '1:1')
r.thing('wormhole', 0, '1050 1180 1 0 seen 2'); r.thing('wormhole', 0, '1210 1230 0 0')
r.case('A', 'S-17', 'wormhole known to player 1, starting on a scout (after its jiggle within the penetrating '
       'range 30)', 'in player 1\'s file (decomp: known or in range)', 'absent if known wormholes are skipped',
       ('thingin', 2, 16384, True))
r.thing('wormhole', 0, '1360 1040 3 0'); r.thing('wormhole', 0, '1290 1240 2 0')
r.case('B', 'S-17', 'unknown wormhole starting on the other scout', 'in player 1\'s file', '', ('thingin', 2, 16386, True))
r.case('C', 'S-17', 'the two partners, far from every scanner', 'absent', '', ('thingin', 2, [16385, 16387], False))
r.thing('packet', 1, '1100 1300 6 5 100 0 0')
r.case('D', 'S-17', 'player 1 packet, start file mark bit 15 clear, far from player 0 (no scanners)',
       'absent from player 0\'s file', '', ('thingin', 1, 8704, False))
r.thing('packet', 1, '1300 1300 6 5 100 0 0 bit15')
r.case('E', 'S-17', 'player 1 packet with bit 15 set in the start file (as every host file leaves it)',
       'absent from player 0\'s file (decomp: only host and PP mark packets)', 'present if the mark persists',
       ('thingin', 1, 8705, False))
r.thing('packet', 0, '1150 1380 6 5 100 0 0')
r.case('F', 'S-17', 'player 0 packet far from player 1\'s scouts (player 0 is written first)',
       'absent from player 1\'s file', 'present if player 0\'s own pass marks it', ('thingin', 2, 8192, False))


def main():
    if sys.argv[1:2] == ['--defs']:
        out = sys.argv[2]
        os.makedirs(out, exist_ok=True)
        for g in NEWGAMES:
            open(os.path.join(out, g['name'] + '.def'), 'w', newline='').write(newgame_def(g))
        return
    if sys.argv[1:] == ['--list']:
        print('## OB-006: new games from a definition file (O-27)')
        for g in NEWGAMES:
            print('| %s | O-27 | size %d, seed %d, random events %s | %s |  |' % (
                g['id'], g['size'], g['seed'], 'on' if g['events'] else 'off', g['expect']))
        for r in RUNS:
            print('## %s: %s' % (r.rid, r.title))
            for c in r.cases:
                print('| %s | %s | %s | %s | %s |' % (c['id'], c['pred'], c['what'], c['expect'], c['alt']))
        return
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for r in RUNS:
        p = os.path.join(out, r.rid.lower().replace('-', '') + '.spec')
        open(p, 'w').write(r.spec())
        print('wrote', p)


if __name__ == '__main__':
    main()
