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


# ---------------------------------------------------------------- OB-018 object scanning without hull scanners
# OB-011's JOAT Scouts added a built-in penetrating range of 30, which covered every R/4 edge. Here
# player 1 views with Small Freighters carrying one Rhino (no hull scanner: R 50, P 0, R/4 12.5).
FREIGHTER1 = 'design 1 2 Small Freighter, 1 Long Hump 6, 1 Rhino Scanner, empty = Rhino Freighter\n'
r = run('OB-018', 'scanning of objects by Rhino freighters (R 50, P 0, R/4 12.5)',
        extra='planet 8 scanner none\n' + FREIGHTER1)
r.scan = dict(viewer=1, mask=2, R=50, P=0)
for (sx, sy) in ((1050, 1040), (1050, 1260), (1360, 1040), (1370, 1230), (1151, 1277), (1291, 1274)):
    r.fleet(1, sx, sy, '2:1')
r.field(0, 1062, 1040, 100); r.case('A', 'S-17', 'unknown field 100 at d=12', 'seen (d <= R/4)', '', ('scan',))
r.field(0, 1050, 1053, 100); r.case('B', 'S-17', 'unknown field 100 at d=13', 'not seen', 'seen if any '
                                    'range above 13 applied', ('scan',))
r.field(0, 1080, 1260, 1000); r.case('C', 'S-17', 'unknown field 1000 at d=30, freighter inside', 'seen', '', ('scan',))
r.field(0, 1050, 1300, 100); r.case('D', 'S-17', 'unknown field 100 at d=40', 'not seen', 'seen at full R',
                                    ('scan',))
r.thing('minefield', 0, '1360 1080 100 known 2'); r.fields.append((0, 1360, 1080, 100, set()))
r.case('E', 'S-17', 'field known to player 1 at d=40', 'seen (full R)', '', ('scan',))
r.thing('minefield', 0, '1310 1040 100 known 2'); r.fields.append((0, 1310, 1040, 100, set()))
r.case('F', 'S-17', 'known field at d=50', 'seen', '', ('scan',))
r.thing('minefield', 0, '1360 1091 100 known 2'); r.fields.append((0, 1360, 1091, 100, set()))
r.case('G', 'S-17', 'known field at d=51', 'not seen', '', ('scan',))
r.thing('wormhole', 0, '1370 1270 1 0'); r.thing('wormhole', 0, '1210 1360 0 0')
r.case('H', 'S-17', 'unknown wormhole 40 ly from a freighter (at least 23 after the jiggle); partner far',
       'neither end seen', 'seen at full R', ('scan',))
r.thing('wormhole', 0, '1370 1230 3 0'); r.thing('wormhole', 0, '1020 1150 2 0')
r.case('I', 'S-17', 'unknown wormhole on a freighter before its jiggle', 'seen iff d <= 12.5 after the jiggle',
       '', ('scan',))
r.thing('packet', 0, '1150 1350 6 5 100 0 0')
r.case('J', 'S-17', 'packet about 48 ly from a freighter after its move', 'seen (d <= R)', '', ('scan',))
r.thing('packet', 0, '1300 1350 6 5 100 0 0')
r.case('K', 'S-17', 'packet about 53 ly from a freighter after its move', 'not seen', '', ('scan',))


# ---------------------------------------------------------------- round 4 (decomp reconciliation, O-41 and O-42)
# OB-019 runs three generations (2400 -> 2403), each started from the previous year's host file.
r = run('OB-019', 'lay-mines task held over three years (O-41) and the years word 1 (O-4)')
r.fleet(0, 1050, 1180, '0:1', extra='task lay 5 to 1050 1250 warp 5', fuel=400)
r.fields.append((0, 1050, 1180, 460, set()))
for y, n in ((1, 160), (2, 310), (3, 460)):
    r.case('A%d' % y, 'O-41', 'year %d: non-SD layer, waypoint 0 lay mines indefinitely, waypoint 1 25 ly away' % y,
           'stays at (1050,1180), field %d, both waypoints kept' % n, 'moves to waypoint 1; field stops growing',
           ('layhold', 0, 0, 1050, 1180, n, 2, '6'))
    r.cases[-1]['year'] = y
r.fleet(0, 1210, 1230, '0:1', extra='task lay 1', fuel=400)
r.fields.append((0, 1210, 1230, 460, set()))
for y, n, t in ((1, 160, '6'), (2, 310, '0'), (3, 300, '0')):
    r.case('B%d' % y, 'O-4', 'year %d: stationary layer with years word 1' % y,
           'field %d, task %s after the year' % (n, 'lay' if t == '6' else 'cleared'), '',
           ('layhold', 0, 1, 1210, 1230, n, 1, t))
    r.cases[-1]['year'] = y

r = run('OB-020', 'known and unknown wormholes between R/4 and R (O-42)',
        extra='planet 8 scanner none\n' + FREIGHTER1)
r.scan = dict(viewer=1, mask=2, R=50, P=0)
r.fleet(1, 1050, 1040, '2:1'); r.fleet(1, 1370, 1230, '2:1')
r.thing('wormhole', 0, '1050 1070 1 0 seen 2'); r.thing('wormhole', 0, '1220 1300 0 0')
r.case('A', 'O-42', 'wormhole known to player 1, 30 ly from a freighter (13 to 47 after the jiggle)',
       'seen (known: full R)', 'not seen if known wormholes use R/4', ('thingin', 2, 16384, True))
r.thing('wormhole', 0, '1370 1260 3 0'); r.thing('wormhole', 0, '1100 1300 2 0')
r.case('B', 'O-42', 'unknown wormhole at the same distance from the other freighter', 'not seen (R/4)', '',
       ('thingin', 2, 16386, False))
r.thing('wormhole', 0, '1250 1120 5 0 seen 2'); r.thing('wormhole', 0, '1300 1350 4 0')
r.case('C', 'O-42', 'known wormhole 170+ ly from every scanner (as OB-011-H)', 'not seen', '',
       ('thingin', 2, 16388, False))
r.case('D', 'S-17', 'every object in player 1\'s file', 'as the rules (known wormholes within R)', '', ('scan',))



# ---------------------------------------------------------------- round 5 (OBJECTS.md BINARY-ONLY rules)
# Predictions below restate OBJECTS.md (written from the stars-decomp objects reading, PR #10) for rules
# no earlier OB case tested. Numbers come from these helpers, written before any round-5 run.

def gate_pct(R, Ms, Md, dist, mass):
    """OBJECTS.md "Stargates": None when refused, else the danger percent (100 = lost)."""
    R = 8000 if R is None else R
    if dist > 5 * R:
        return None
    for M in (Ms, Md):
        if M and mass > 5 * M:
            return None
    f = 10000
    if dist > R:
        f = (5 * R - dist) * 2500 // R
        if f <= 0:
            return 100
    for M in (Ms, Md):
        if M and 0 < M < mass:
            g = (5 * M - mass) * 2500 // M
            if g <= 0:
                return 100
            f = g * f // 10000
    return (10000 - f) // 100


def gate_word(pct, armor):
    """Damage word of every survivor after a jump with 0 < pct < 100 and no earlier damage."""
    nw = max(1, pct * armor // 100)
    return '%d/100%%' % max(1, nw * 500 // armor)


def dist(a, b):
    return int(math.hypot(XY[a][0] - XY[b][0], XY[a][1] - XY[b][1]))


DD_MASS, DD_ARMOR = 41, 200          # Destroyer, Long Hump 6, two Lasers (design 0/1 "Laser DD")
SF_MASS, SF_ARMOR = 202, 400         # Super Freighter, three Long Hump 6 (design 0/9)
HSF_MASS = 502                       # Super Freighter, three Long Hump 6, five Tritanium (design 0/11)
GATES = ('sbdesign 0 3 Orbital Fort, 1 Stargate 100/250, empty, empty, empty, empty = Gate Fort\n'
         'sbdesign 0 4 Orbital Fort, 1 Stargate 150/600, empty, empty, empty, empty = Gate 600\n')
EXTRA_DESIGNS = ('design 0 11 Super Freighter, 3 Long Hump 6, empty, 5 Tritanium, empty = Heavy Freighter\n'
                 'design 0 12 Super Mine Layer, 1 Long Hump 6, 2 Mine Dispenser 40, empty, empty, empty, empty = Super Layer\n')


def own(n, owner, sb, pop=1000):
    return 'planet %d owner %d pop %d starbase %s\nplanetset %d %s scanner=31\n' % (
        n, owner, pop, sb if sb is not None else 'none', n, PLAIN)


# ---------------------------------------------------------------- OB-021 stargates (JOAT player 0)
ex = GATES + EXTRA_DESIGNS + 'tech 1 prop 5\ntech 1 con 5\n' + \
    'sbdesign 1 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, ' \
    'empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase\n' \
    'sbdesign 1 1 Orbital Fort, 1 Stargate 100/250, empty, empty, empty, empty = Gate Fort\n'
for n in (12, 15, 6, 16, 5, 11, 14, 22, 23, 0, 21, 18, 10):
    ex += own(n, 0, 3)
ex += own(1, 0, 4) + own(20, 0, 1) + own(9, 1, 1)
r = run('OB-021', 'stargates: range, mass, refusal, cargo, gate ownership (JOAT player 0, gates 100/250 and 150/600)',
        extra=ex)


def gate_fleet(r, src, dst, ships, cargo=None, plan=1, fuel=100):
    (x, y), (tx, ty) = XY[src], XY[dst]
    c = ' cargo %d %d %d %d' % cargo if cargo else ''
    return r.fleet(0, x, y, ships, plan=plan, planet=src, fuel=fuel, extra='%s to %d %d planet %d warp 11' % (c, tx, ty, dst))


d = dist(12, 15); gate_fleet(r, 12, 15, '1:1')
r.case('A', 'gate', 'Laser DD (mass %d) jumps %d ly between 100/250 gates' % (DD_MASS, d),
       'at planet 15, undamaged, fuel 100 (no fuel used)', 'stays; or fuel spent', ('gate', 0, 0, 15, 1, None, 100))
d = dist(6, 16); pct = gate_pct(250, 100, 100, d, DD_MASS); gate_fleet(r, 6, 16, '1:5')
r.case('B', 'gate', '5 Laser DDs jump %d ly through a 100/250 gate (over range): danger %d%%' % (d, pct),
       'at planet 16; each ship lost with %d%%; survivors %s (%d armor each)' % (pct // 3, gate_word(pct, DD_ARMOR),
                                                                             max(1, pct * DD_ARMOR // 100)),
       'refused; or no damage', ('gate', 0, 1, 16, 5, gate_word(pct, DD_ARMOR), 100))
d = dist(5, 11); pct = gate_pct(250, 100, 100, d, SF_MASS); gate_fleet(r, 5, 11, '9:3', cargo=(100, 50, 25, 10))
r.case('C', 'gate', '3 Super Freighters (mass %d > 100) jump %d ly carrying 100/50/25 kT and 10 kT colonists: danger %d%%'
       % (SF_MASS, d, pct),
       'at planet 11 empty; each ship lost with %d%%; survivors %s; source planet 5 surface +100/+50/+25 and pop '
       '1010 -> %d' % (pct // 3, gate_word(pct, SF_ARMOR), grown(1010)), 'cargo carried through',
       ('gate', 0, 2, 11, 3, gate_word(pct, SF_ARMOR), None, (0, 0, 0, 0)))
r.case('C2', 'gate', 'the source planet of C', 'surface +100/+50/+25, pop %d' % grown(1010), 'unchanged (%d)' % grown(1000),
       ('planet', 5, dict(surface=(100, 50, 25), pop=grown(1010))))
d = dist(14, 22); gate_fleet(r, 14, 22, '11:1', cargo=(100, 0, 0, 0))
r.case('D', 'gate', 'Heavy Freighter (mass %d > 5 x 100) at a gate, %d ly jump, carrying 100 kT ironium' % (HSF_MASS, d),
       'refused: stays at planet 14, undamaged, hold empty', 'jumps with damage', ('gate', 0, 3, 14, 1, None, 100, (0, 0, 0, 0)))
r.case('D2', 'gate', 'the source planet of D', 'surface +100 ironium (cargo dumped although the jump was refused, '
       'LEGACY BUG)', 'surface unchanged', ('planet', 14, dict(surface=(100, 0, 0))))
d = dist(1, 23); gate_fleet(r, 1, 23, '1:1')
r.case('E', 'gate', 'Laser DD jumps %d ly from a 150/600 gate to a 100/250 gate' % d,
       'at planet 23, undamaged (range from the source gate only)', 'damaged by the 250 range',
       ('gate', 0, 4, 23, 1, None, 100))
pct = gate_pct(250, 100, 150, d, DD_MASS); gate_fleet(r, 23, 1, '1:1')
r.case('F', 'gate', 'Laser DD jumps the same %d ly the other way (100/250 source): danger %d%%' % (d, pct),
       'at planet 1, lost with %d%%, else %s' % (pct // 3, gate_word(pct, DD_ARMOR)), 'undamaged',
       ('gate', 0, 5, 1, 1, gate_word(pct, DD_ARMOR), 100))
d = dist(0, 21); pct = gate_pct(250, 100, 100, d, SF_MASS); gate_fleet(r, 0, 21, '9:3')
r.case('G', 'gate', '3 Super Freighters (mass %d) jump %d ly: range and mass factors multiply, danger %d%%' % (SF_MASS, d, pct),
       'at planet 21; each lost with %d%%; survivors %s' % (pct // 3, gate_word(pct, SF_ARMOR)),
       'danger %d%% if only the larger factor counted' % max(gate_pct(250, None, None, d, SF_MASS), gate_pct(250, 100, 100, 0, SF_MASS)),
       ('gate', 0, 6, 21, 3, gate_word(pct, SF_ARMOR), 100))
gate_fleet(r, 18, 20, '1:1')
r.case('H', 'gate', 'Laser DD at a gate, destination planet 20 has a starbase without a gate',
       'stays at planet 18, fuel 100', 'jumps', ('gate', 0, 7, 18, 1, None, 100))
gate_fleet(r, 9, 10, '1:1')
r.case('I', 'gate', 'Laser DD (plan "nobody") at enemy player 1\'s gate planet 9, gate warp to own gate planet 10',
       'stays at planet 9 (source gate not owned by self or a friend)', 'jumps', ('gate', 0, 8, 9, 1, None, 100))


# ---------------------------------------------------------------- OB-022 Interstellar Traveler: gates and packets
IT = ('prt 1 7\nlrt 1 0x1b80\n' + ''.join('tech 1 %s 26\n' % f for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')) +
      'design 1 0 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD\n'
      'design 1 1 Super Freighter, 3 Long Hump 6, empty, empty, empty = Super Freighter\n'
      'design 1 2 Super Freighter, 3 Long Hump 6, empty, 5 Tritanium, empty = Heavy Freighter\n'
      'sbdesign 1 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, '
      'empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase\n'
      'sbdesign 1 1 Orbital Fort, 1 Stargate 100/250, empty, empty, empty, empty = Gate Fort\n'
      'sbdesign 1 2 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Catcher 7\n')
for n in (6, 16, 14, 22, 5, 11):
    IT += own(n, 1, 1)
IT += own(20, 1, None) + own(9, 1, 2)
r = run('OB-022', 'Interstellar Traveler player 1 (tech 26): stargates without losses or cargo dumps; packets into IT planets',
        extra=IT)


def gate_fleet1(r, src, dst, ships, cargo=None, fuel=100):
    (x, y), (tx, ty) = XY[src], XY[dst]
    c = ' cargo %d %d %d %d' % cargo if cargo else ''
    return r.fleet(1, x, y, ships, plan=0, planet=src, fuel=fuel, extra='%s to %d %d planet %d warp 11' % (c, tx, ty, dst))


d = dist(6, 16); pct = gate_pct(250, 100, 100, d, DD_MASS); gate_fleet1(r, 6, 16, '0:5')
r.case('A', 'gate/IT', 'IT: 5 Laser DDs jump %d ly through a 100/250 gate: danger %d%%' % (d, pct),
       'at planet 16, all 5 ships kept, each %s' % gate_word(pct, DD_ARMOR), 'ships lost with %d%%' % (pct // 3),
       ('gate', 1, 0, 16, -5, gate_word(pct, DD_ARMOR), 100))
gate_fleet1(r, 14, 22, '2:1', cargo=(100, 0, 0, 0))
r.case('B', 'gate/IT', 'IT: Heavy Freighter (mass %d) refused, carrying 100 kT ironium' % HSF_MASS,
       'stays at planet 14 with its 100 kT; planet 14 surface unchanged', 'cargo dumped',
       ('gate', 1, 1, 14, 1, None, 100, (100, 0, 0, 0)))
r.case('B2', 'gate/IT', 'the source planet of B', 'surface +0', '+100', ('planet', 14, dict(surface=(0, 0, 0))))
pct = gate_pct(250, 100, 100, dist(5, 11), SF_MASS); gate_fleet1(r, 5, 11, '1:3', cargo=(100, 50, 25, 10))
r.case('C', 'gate/IT', 'IT: 3 Super Freighters (danger %d%%) jump %d ly with 100/50/25 kT and 10 kT colonists'
       % (pct, dist(5, 11)), 'at planet 11, all 3 kept, cargo carried through, each %s' % gate_word(pct, SF_ARMOR),
       'cargo dumped at planet 5', ('gate', 1, 2, 11, -3, gate_word(pct, SF_ARMOR), 100, (100, 50, 25, 10)))
r.thing('packet', 0, '1348 1340 20 10 1000 0 0')
r.case('D', 'packet/IT', 'player 0 warp-10 1000 kT packet into IT planet 20 (no starbase, pop 1000)',
       'w^2 halved to 50: 312 killed, pop 688 -> %d; surface +111' % grown(688), 'not halved: 625 killed, %d' % grown(375),
       ('planet', 20, dict(pop=grown(688), surface=(111, 0, 0))))
r.thing('packet', 0, '1208 1347 9 10 1000 0 0')
r.case('E', 'packet/IT', 'the same into IT planet 9 with a Mass Driver 7 catcher (pop 1000)',
       'w^2 50, c^2 24: q 480, surface +537; 162 killed, pop 838 -> %d' % grown(838),
       'not halved: +546, %d; rounded c^2 25: +555, %d' % (grown(682), grown(844)),
       ('planet', 9, dict(pop=grown(838), surface=(537, 0, 0))))


# ---------------------------------------------------------------- OB-023 Packet Physics decay, single Trader arrival
r = run('OB-023', 'Packet Physics player 1 packet decay; one Mystery Trader reaching its destination',
        extra='prt 1 6\nlrt 1 0x1b80\n')
PP_PKT = []
for i, (x, y, cargo, cls, want, alt) in enumerate((
        (1060, 1040, (1000, 0, 0), 1, (950, 0, 0), '900'), (1060, 1140, (1000, 0, 0), 2, (880, 0, 0), '750; 875 if 12.5%'),
        (1060, 1240, (1000, 0, 0), 3, (750, 0, 0), '500'), (1060, 1340, (50, 0, 0), 1, (45, 0, 0), '40 (minimum 10)'),
        (1380, 1040, (100, 100, 0), 2, (88, 88, 0), '75/75; germanium stays 0'))):
    n = r.thing('packet', 1, '%d %d 23 5 %d %d %d class %d' % ((x, y) + cargo + (cls,)))
    r.case('P%d' % i, 'packet/PP', 'PP packet class %d, %s kT, warp 5 in flight' % (cls, '/'.join(map(str, cargo))),
           'cargo %s after one year (PP rates 5/12/25%%, minimum 5)' % '/'.join(map(str, want)), alt,
           ('pkt', 1, n, want))
n = r.thing('packet', 0, '1380 1140 23 5 1000 0 0 class 1')
r.case('Q', 'packet', 'player 0 (JOAT) packet class 1, 1000 kT', 'cargo 900 (10%)', '', ('pkt', 0, n, (900, 0, 0)))
n = r.thing('packet', 0, '1380 1240 23 5 50 0 0 class 1')
r.case('R', 'packet', 'player 0 packet class 1, 50 kT', 'cargo 40 (minimum 10)', '45', ('pkt', 0, n, (40, 0, 0)))
r.thing('trader', 0, '1360 1300 1380 1300 8')
r.case('T', 'trader', 'the only Mystery Trader, warp 8, 20 ly from its destination (1380,1300)',
       'gone (1/2), or at (1380,1300) with warp 7 (8 if its warp rose first) and a new destination on an edge',
       'keeps moving past', ('traderend', 0, 1380, 1300))


# ---------------------------------------------------------------- OB-024 minefield hits and the Super Mine Layer
r = run('OB-024', 'minefield hits at warp 10: mines lost by field size, salvage, speed-bump stops; Super Mine Layer',
        extra=EXTRA_DESIGNS)
r.field(1, 1060, 1230, 400, kind='heavy')
r.fleet(0, 1020, 1230, '1:1', plan=1, fuel=2000, extra='to 1120 1230 warp 10')
r.case('A', 'O-14/O-15', 'one Laser DD at warp 10 (100 ly) crossing 40 ly of a heavy 400 field (40 per mille per ly)',
       'no hit (20%): field 390, DD at (1120,1230); or hit: DD destroyed (2000 minimum), field 400-20-10 = 370, '
       'salvage of 0-9 kT of each mineral at the stop point', 'mines lost 10', ('minehit2', 0, 0, 1060, 1230, 390, 370))
r.field(1, 1200, 1230, 6000, kind='heavy', planets=[5, 9])
r.fleet(0, 1110, 1230, '1:5', plan=1, fuel=2000, extra='to 1290 1230 warp 10')
r.case('B', 'O-14/O-15', '5 Laser DDs at warp 10 crossing a heavy 6000 field (154 ly, two planets inside)',
       'hit (99.8%%): all destroyed (500 each); field 6000-60 = 5940, decay 10%% -> %d; salvage 0-9 kT each'
       % (5940 - 5940 * 10 // 100), 'mines lost 300 (N/20) or 50',
       ('minehit2', 0, 1, 1200, 1230, 6000 - 6000 * 10 // 100, 5940 - 5940 * 10 // 100))
r.field(1, 1060, 1060, 400, kind='bump')
r.fleet(0, 1020, 1060, '1:1', plan=1, fuel=2000, extra='to 1120 1060 warp 10')
r.case('C', 'O-14/O-15', 'one Laser DD at warp 10 crossing a speed-bump 400 field (175 per mille per ly)',
       'stopped inside, undamaged; field 400-20 = 380, decay 2% (no minimum) -> 373', 'damaged; or field 392',
       ('minehit2', 0, 2, 1060, 1060, 392, 373))
r.fleet(0, 1360, 1360, '12:1', plan=1, fuel=400, extra='task lay')
r.case('D', 'O-1', 'Super Mine Layer with 2 Mine Dispenser 40, laying in place', 'standard field 160 (doubled)', '80',
       ('field', 0, 1360, 1360, 160))



# ---------------------------------------------------------------- OB-025 three years: lay durations, wormhole ages and jumps
# Run like OB-019: 2400 -> 2403, each year from the previous year's host file; check.py with OB_YEAR=N.
r = run('OB-025', 'three years: lay-mines years words 2 and 3; wormhole years, classes and jumps (6%/yr ends)')
r.fleet(0, 1210, 1230, '0:1', plan=1, fuel=400, extra='task lay 2')
r.fields.append((0, 1210, 1230, 460, set()))
for y, n, t in ((1, 160, '6'), (2, 310, '6'), (3, 460, '0')):
    r.case('A%d' % y, 'O-4', 'year %d: stationary layer, years word 2' % y,
           'field %d, task %s' % (n, 'kept' if t == '6' else 'cleared (3 years laid)'),
           'cleared a year earlier (word = years)', ('layhold', 0, 0, 1210, 1230, n, 1, t))
    r.cases[-1]['year'] = y
r.fleet(0, 1080, 1360, '0:1', plan=1, fuel=400, extra='task lay 3')
r.fields.append((0, 1080, 1360, 460, set()))
for y, n in ((1, 160), (2, 310), (3, 460)):
    r.case('B%d' % y, 'O-4', 'year %d: stationary layer, years word 3' % y, 'field %d, task kept' % n, '',
           ('layhold', 0, 1, 1080, 1360, n, 1, '6'))
    r.cases[-1]['year'] = y
# wormholes: pair 0/1 class 1 years 0; ten pairs of class 2 ends aged 40 (6% per end per year)
r.thing('wormhole', 0, '1360 1040 1 1')
r.thing('wormhole', 0, '1360 1120 0 1')
for y in (1, 2, 3):
    r.case('W%d' % y, 'O-28/O-29', 'year %d: class-1 pair aged 0' % y,
           'no jump (0%% before 10 years); years %d; class 1; each step at most 12 ly per axis' % y, '',
           ('wormage', [0, 1], y, 1))
    r.cases[-1]['year'] = y
JW = [(1040, 1050), (1120, 1050), (1200, 1040), (1280, 1150), (1040, 1170), (1100, 1220), (1180, 1240),
      (1260, 1230), (1040, 1330), (1120, 1380), (1200, 1380), (1300, 1350), (1340, 1260), (1240, 1100),
      (1160, 1290), (1020, 1260), (1300, 1020), (1380, 1180), (1340, 1380), (1220, 1310)]
for i, (x, y) in enumerate(JW):
    num = 2 + i
    partner = num + 1 if i % 2 == 0 else num - 1
    r.thing('wormhole', 0, '%d %d %d 2 years 40' % (x, y, partner))
for y in (1, 2, 3):
    r.case('J%d' % y, 'O-28', 'year %d: twenty class-2 ends aged %d (jump 6%% per end per year)' % (y, 39 + y),
           'each end jiggles (years +1) or jumps (years 0, anywhere); class stays 2; recorded per end', '',
           ('wormjump', list(range(2, 22)), y))
    r.cases[-1]['year'] = y
# player 0 scouts heading for four of the aged ends at warp 1 (they never arrive)
for k, i in enumerate((0, 5, 10, 15)):
    x, y = JW[i]
    r.fleet(0, x, y + 20, '10:1', plan=1, fuel=50, extra='to %d %d thing 0x%x warp 1' % (x, y, 0x4000 + 2 + i))
for y in (1, 2, 3):
    r.case('F%d' % y, 'O-31', 'year %d: scouts at warp 1 targeting aged ends (player 0 sees the whole map)' % y,
           'the waypoint keeps the wormhole as target and follows its position, after jiggles and after jumps',
           'target dropped to deep space after a jump', ('wormfollow', [(0, 2 + k, 2 + i) for k, i in enumerate((0, 5, 10, 15))]))
    r.cases[-1]['year'] = y


# ---------------------------------------------------------------- OB-026 Mystery Trader: arrival with another Trader, rewards
r = run('OB-026', 'Mystery Trader: arrival while another exists, part and ship rewards (player 1 at tech 3)')
r.extra += 'design 1 0 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter\n'
r.thing('trader', 0, '1300 1100 1380 1100 9')
r.case('A', 'trader', 'Trader 0 (warp 9) 80 ly from its destination while three others exist', 'gone',
       'stays (1/2)', ('tradergone', 0))
r.thing('trader', 0, '1020 1210 1380 1210 8 item 1')
r.fleet(1, 1084, 1210, '0:24', extra='cargo 5000 0 0 0')
r.case('B', 'trader', 'Trader 1 offering part bit 0 moves 64 ly onto a player 1 fleet of 24 Medium Freighters with 5000 kT',
       'fleet removed; player 1 gains exactly one Mystery Trader part bit; tech unchanged', 'research levels',
       ('mtpart', 1, 0))
r.thing('trader', 0, '1020 1300 1380 1300 8 item 0x1000')
r.fleet(1, 1084, 1300, '0:24', extra='cargo 5000 0 0 0')
r.case('C', 'trader', 'Trader 2 offering a ship moves 64 ly onto a second player 1 fleet with 5000 kT',
       'fleet removed; a new player 1 fleet of 1 or 2 ships of one new design (added to its designs) at (1084,1300); tech '
       'unchanged', 'research levels; nothing', ('mtship', 1, 1, 1084, 1300))
r.thing('trader', 0, '1020 1050 1380 1050 9')
r.case('D', 'trader', 'Trader 3, warp 9, mid-crossing', 'at (1101,1050) warp 9 (24/25), or warp 10 at (1120,1050), '
       'perhaps with a new destination', '', ('traderend', 3, None, None))



# ---------------------------------------------------------------- OB-027 wormhole targets known vs unknown (after OB-025-F1)
# OB-025-F1: thing-target waypoints on wormholes player 0 had not seen at the start of the year became
# deep-space waypoints at the old position after the first jiggle. The decomp reading: the target is kept
# (and follows) only when the owner has the wormhole's seen bit.
r = run('OB-027', 'scouts targeting wormholes known (seen bit) and unknown at the start of the year')
KW = [(1040, 1050), (1120, 1050), (1200, 1040), (1280, 1150), (1040, 1170), (1100, 1220), (1180, 1240), (1260, 1230)]
for i, (x, y) in enumerate(KW):
    partner = i + 1 if i % 2 == 0 else i - 1
    r.thing('wormhole', 0, '%d %d %d 1%s' % (x, y, partner, ' seen 1' if i < 4 else ''))
    r.fleet(0, x, y + 20, '10:1', plan=1, fuel=50, extra='to %d %d thing 0x%x warp 1' % (x, y, 0x4000 + i))
r.case('A', 'O-31', 'scouts at warp 1 targeting class-1 wormholes 0-3, known to player 0 (seen bit set)',
       'waypoint keeps the wormhole as target (obj id kept)', 'deep space at the old position as in OB-025-F1',
       ('wormfollow', [(0, i, i) for i in range(4)]))
r.case('B', 'O-31', 'scouts targeting wormholes 4-7, unknown at the start (as OB-025)',
       'deep-space waypoint at the old position (repeats OB-025-F1)', '',
       ('wormlost', [(0, i, i) for i in range(4, 8)]))


# ================================================================ round 6: the BINARY-ONLY sweep (OB-028..OB-031)
# Predictions restate OBJECTS.md "Mass-driver packets" (Launch, launch-year flight, AR and PP impact) and
# "Mystery Trader" (arrival warp, several Traders), written before any round-6 run. Launch amounts, warp
# and class follow "Launch"; costs (110 kT per 100 kT, IT 120, PP 70; mixed 44, IT 48, PP 25) are the
# stars-decomp production reading, recorded here as a side check.

def launch_pos(src, dest, W):
    """Launch-year position: floor(W^2/2) ly toward planet dest, each coordinate rounded half away from zero."""
    (x, y), (tx, ty) = XY[src], XY[dest]
    dx, dy = tx - x, ty - y
    d = math.hypot(dx, dy)
    sp = W * W // 2
    if int(d) <= sp:
        return None
    rnd = lambda v: int(v + 0.5) if v >= 0 else -int(-v + 0.5)
    return x + rnd(sp * dx / d), y + rnd(sp * dy / d)


def decay(m, cls, pct, pp=False):
    rate = {0: 0, 1: 10, 2: 25, 3: 50}[cls]
    if not rate:
        return list(m)
    mn = 10
    if pp:
        rate //= 2
        mn = 5
    return [0 if x == 0 else max(0, x - max(x * rate * pct // 10000, mn)) for x in m]


SB_LAUNCH = ('sbdesign 0 3 Space Station, 1 Mass Driver 7, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, '
             '8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, 1 Mass Driver 7, 8 Mole-skin Shield = Twin 7\n'
             'sbdesign 0 4 Space Station, 1 Mass Driver 7, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, '
             '8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, 1 Mass Driver 5, 8 Mole-skin Shield = MD7 and MD5\n')
SB1 = ('sbdesign 1 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, '
       'empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase\n'
       'sbdesign 1 1 Orbital Fort, 1 Mass Driver 7, empty, empty, empty, empty = Catcher 7\n')
TECH1 = ''.join('tech 1 %s 26\n' % f for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))
LAUNCH = 'mines=0 factories=0 defenses=0 fe=5000 bo=5000 ge=5000 env=50,50,50 excess=0 scanner=31'


def launcher(owner, n, sb, dest, warp, queue):
    pk = 'none' if dest is None else '%d,%d' % (dest, warp)
    return 'planet %d owner %d pop 1000 starbase %d\nplanetset %d %s packet=%s\nqueue %d %s\n' % (
        n, owner, sb, n, LAUNCH, pk, n, queue)


def launch_case(r, cid, owner, src, dest, W, cls, cargo, cost, what, alt, pp=False, it=False):
    m = decay(cargo, cls, 50, pp)
    pos = launch_pos(src, dest, W)
    r.case(cid, 'launch', what, 'one packet to planet %d: warp %d, class %d, %s kT after the half-year decay, at %s'
           % (dest, W, cls, '/'.join(map(str, m)), pos), alt, ('launch', owner, dest, W, cls, tuple(m), pos))
    r.case(cid + 'c', 'launch cost', 'launcher planet %d surface minerals' % src,
           'down %s (side check of the production reading)' % '/'.join(map(str, cost)), '',
           ('surface', src, tuple(-c for c in cost)))


# ---------------------------------------------------------------- OB-028 packet launch (JOAT player 0, IT player 1)
ex = SB_LAUNCH + 'prt 1 7\nlrt 1 0x1b80\n' + TECH1 + SB1
ex += launcher(0, 0, 2, 23, 9, '14:1:1')
ex += launcher(0, 1, 2, 19, 11, '14:2:1')
ex += launcher(0, 2, 3, 21, 4, '17:1:1')
ex += launcher(0, 3, 4, 22, 4, '17:1:1')
ex += launcher(0, 4, 2, 20, 7, '14:1:1,14:1:1')
ex += launcher(0, 5, 2, None, 7, '14:1:1')
ex += launcher(0, 11, 2, 12, 10, '14:5:1')
ex += launcher(1, 14, 1, 7, 7, '14:1:1')
ex += launcher(1, 16, 1, 9, 10, '14:1:1')
r = run('OB-028', 'packet launch: driver warp, two drivers, speed setting, class, amounts, merge, '
        'no destination, launch-year flight (JOAT player 0); IT launcher class (player 1, tech 26)', extra=ex)
launch_case(r, 'A', 0, 0, 23, 9, 2, (100, 0, 0), (110, 0, 0), 'Mass Driver 7 fort, speed set to 9, one ironium item',
            'warp 7 class 0; or no launch-year decay')
launch_case(r, 'B', 0, 1, 19, 7, 0, (200, 0, 0), (220, 0, 0),
            'Mass Driver 7 fort, speed set to 11 (above 7 + 3), ironium item x2', 'warp 10 (capped); two packets')
launch_case(r, 'C', 0, 2, 21, 8, 0, (40, 40, 40), (44, 44, 44),
            'Space Station with Mass Driver 7 in both orbital slots, speed unset, one mixed item', 'warp 7')
launch_case(r, 'D', 0, 3, 22, 7, 0, (40, 40, 40), (44, 44, 44),
            'Space Station with Mass Driver 7 and Mass Driver 5 in the two orbital slots, speed unset, one mixed item',
            'warp 8 (any two drivers)')
launch_case(r, 'E', 0, 4, 20, 7, 0, (200, 0, 0), (220, 0, 0),
            'Mass Driver 7 fort, speed 7, two separate ironium items in one queue', 'two packets of 100 kT')
r.case('F', 'launch', 'Mass Driver 7 fort with no packet destination, one ironium item',
       'no packet from planet 5; surface unchanged; a message to player 0', 'packet launched',
       ('nolaunch', 0, 5))
pct = 35 * 100 // 50 // 2
m = decay((500, 0, 0), 3, pct)
r.case('G', 'launch', 'Mass Driver 7 fort, speed 10 (class 3), ironium x5 to planet 12, 35 ly away (within 50 = 10^2/2)',
       'arrives the launch year: decay for half its 70%% share (%d%%) leaves %d kT; unowned planet 12 surface +%d'
       % (pct, m[0], m[0] * 111 // 1000), 'still in flight; or arrives with full-year decay',
       ('surface', 12, (m[0] * 111 // 1000, 0, 0)))
launch_case(r, 'H', 1, 14, 7, 7, 1, (100, 0, 0), (120, 0, 0), 'IT player 1: Mass Driver 7 fort, speed 7',
            'class 0 (no IT +1)', it=True)
launch_case(r, 'I', 1, 16, 9, 10, 3, (100, 0, 0), (120, 0, 0), 'IT player 1: Mass Driver 7 fort, speed 10 (class 3)',
            'class 4; or 3 + 1 wrapping', it=True)


# ---------------------------------------------------------------- OB-029 Packet Physics launcher: amounts, terraforming, damage
ex = 'prt 1 6\nlrt 1 0x1b80\n' + TECH1 + SB1
ex += launcher(1, 14, 1, 7, 7, '14:1:1')
ex += launcher(1, 16, 1, 9, 7, '17:1:1')
for n in (0, 3, 6):
    ex += 'planetset %d env=20,20,20\n' % n
ex += 'planet 9 owner 0 pop 1000 starbase 1\nplanetset 9 %s scanner=31\n' % PLAIN
r = run('OB-029', 'Packet Physics player 1 (tech 26): launch amounts, terraforming by uncaught packets, damage and '
        'the catcher\'s design', extra=ex)
launch_case(r, 'A', 1, 14, 7, 7, 0, (70, 0, 0), (70, 0, 0), 'PP: Mass Driver 7 fort, speed 7, one ironium item',
            '100 kT', pp=True)
launch_case(r, 'B', 1, 16, 9, 7, 0, (25, 25, 25), (25, 25, 25), 'PP: Mass Driver 7 fort, speed 7, one mixed item',
            '40 kT each', pp=True)
for cid, n, mi, axis in (('T1', 0, 0, 'gravity'), ('T2', 3, 1, 'temperature'), ('T3', 6, 2, 'radiation')):
    x, y = XY[n]
    cargo = [0, 0, 0]
    cargo[mi] = 1000
    r.thing('packet', 1, '%d %d %d 10 %d %d %d' % ((x - 30, y, n) + tuple(cargo)))
    r.case(cid, 'PP terraform', 'PP packet, 1000 kT %s only, warp 10, into unowned planet %d (environment 20/20/20, '
           'player 1 ideal 50)' % ('ironium boranium germanium'.split()[mi], n),
           'only %s moves, up by the success count (10 chunks at 1/2: 1-10, mean 5); the other two stay 20; '
           'surface +111 of that mineral' % axis, 'another axis moves; or no terraforming',
           ('ppterra', n, mi))
r.thing('packet', 1, '%d %d 9 10 500 0 0' % (XY[9][0] - 30, XY[9][1]))
r.case('D', 'PP impact', 'PP packet 500 kT warp 10 into player 0 planet 9 (pop 1000, Laser Fort, no driver, at '
       'player 1\'s ideal)', 'damage 312: pop 688 -> %d; surface +55; environment unchanged (already at the ideal)'
       % grown(688), '', ('planet', 9, dict(pop=grown(688), surface=(55, 0, 0))))
r.case('D2', 'PP impact', 'player 1\'s file after D', 'player 0\'s Laser Fort design is known to player 1', '',
       ('designknown', 2, 0, 'Laser Fort'))


# ---------------------------------------------------------------- OB-030 AR target; two Traders on one point
ex = 'prt 1 8\nlrt 1 0x1b80\n' + TECH1 + SB1 + 'design 1 0 Super Freighter, 3 Long Hump 6, empty, empty, empty = Super Freighter\n'
for n in (20, 22):
    ex += 'planet %d owner 1 pop 1000 starbase 0\nplanetset %d mines=0 factories=0 defenses=0 fe=0 bo=0 ge=0 excess=0 ' \
          'scanner=31\n' % (n, n)
r = run('OB-030', 'Alternate Reality target (player 1, tech 26); two Mystery Traders reaching the same point', extra=ex)
r.thing('packet', 0, '%d %d 20 10 1000 0 0' % (XY[20][0] - 30, XY[20][1]))
r.case('A', 'AR impact', 'player 0 warp-10 1000 kT packet into AR planet 20 (pop 1000, starbase without driver)',
       'surface +111; no damage: pop equal to the control planet 22', '625 killed',
       ('arpacket', 20, 22, (111, 0, 0)))
r.thing('trader', 0, '1020 1230 1380 1230 8')
r.thing('trader', 0, '1020 1230 1380 1230 8')
for owner in (0, 0, 1):
    r.fleet(owner, 1084, 1230, '9:2' if owner == 0 else '0:2', plan=1 if owner == 0 else 0, extra='cargo 5000 0 0 0')
r.case('T', 'trader', 'Traders 0 and 1 (warp 8) both end at (1084,1230), where player 0 has fleets 0 and 1 and player 1 '
       'fleet 0, each with 5000 kT', 'all three fleets consumed: Trader 0 takes player 0 fleet 0 and player 1 fleet 0 '
       '(player 0 fleet 1 refused, "still recovering"), Trader 1 takes player 0 fleet 1',
       'player 0 fleet 1 kept (one reward per player per year)', ('tradertwo', [(0, 0), (0, 1), (1, 0)]))


# ---------------------------------------------------------------- OB-031 a warp-6 Trader arrives (run at three cycles)
r = run('OB-031', 'the only Mystery Trader, warp 6, arrives (cycles 20000, 30000, 60000)')
r.thing('trader', 0, '1360 1100 1380 1100 6')
r.case('A', 'trader', 'warp-6 Trader 20 ly from its destination (1380,1100), no other Trader',
       'gone (1/2), or at (1380,1100) with warp max(6, 6 - 2) + 1 = 7 and a new destination on an edge',
       'warp 5 (warp - 1) or 6', ('traderend6', 0, 1380, 1100))

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
