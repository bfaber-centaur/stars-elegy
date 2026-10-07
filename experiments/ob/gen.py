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
"""


class Run:
    def __init__(self, rid, title, rel01=2, rel10=2, tech=TECH26, extra=''):
        self.rid, self.title = rid, title
        self.rel01, self.rel10, self.tech, self.extra = rel01, rel10, tech, extra
        self.lines, self.cases, self.fields, self.fleetpos = [], [], [], []
        self.nfleet = {0: 0, 1: 0}
        self.nthing = {}

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
r.fleet(0, 1084, 1210, '9:2', extra='cargo 4999 0 0 100')
r.case('A', 'O-34', 'stationary player 0 fleet with 4999 kT minerals and 100 colonists at the MT',
       'fleet kept, no message (stationary)', '', ('fleet', 0, 0, 'kept'))
r.fleet(0, 1064, 1210, '9:2', extra='cargo 2000 1999 1000 0 to 1084 1210 warp 5')
r.case('B', 'O-34', 'player 0 fleet with 4999 kT that moves 20 ly onto the MT', 'fleet kept, message 0x108',
       '', ('fleet', 0, 1, 'kept'))
r.fleet(0, 1084, 1210, '9:2', extra='cargo 2000 2000 1000 0')
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


def main():
    if sys.argv[1:] == ['--list']:
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
