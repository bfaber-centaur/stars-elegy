#!/usr/bin/env python3
"""Write the TK round-2 (TK-101..TK-115) Combat Lab specs, with predictions.

Round 2 tests the takeover rules that round 1 (gen.py, TK-001..007) could
not reach: War Monger, Inner Strength, Alternate Reality and Claim Adjuster
ground combat and colonization, the default production queue after a
capture, scrap, remote mining, several players bombing one planet, the
phase-start ownership record, own-planet unload amounts, colonize retries,
tech on capture, colony minerals at intermediate tech, and the design check
at generation. Predictions come from docs/TAKEOVER.md (main, plus the rules
of stars-elegy #34) and are written here before the runs; `check2.py`
compares them with the run dumps.

Each run is one pinned generation (tools/fleetlab/pinned-turn) of a start
built by `tools/fleetlab/combatlab build` from Combat Lab (CB, two JOAT
players) or, for TK-113, from TK3, a tiny three-player game made with
tools/fleetlab/new-game (three human players of the PG000 race: Super
Stealth, growth 10%). TK-111 runs two years.

Populations are in the file's units of 100 colonists. "P" is the start
value; growth (KERNEL.md) happens before the after-movement phase, so most
targets use P = 87 (100 after growth at 15%).

  python3 experiments/tk/gen2.py OUTDIR      # write tkNNN.spec files
  python3 experiments/tk/gen2.py --table     # print the prediction table
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')

CB_XY = {0: (1045, 1291), 1: (1071, 1087), 2: (1090, 1295), 3: (1129, 1265), 4: (1143, 1103),
         5: (1146, 1180), 6: (1166, 1017), 7: (1166, 1382), 8: (1169, 1145), 9: (1208, 1297),
         10: (1224, 1359), 11: (1243, 1123), 12: (1245, 1158), 13: (1249, 1354), 14: (1268, 1317),
         15: (1281, 1064), 16: (1284, 1383), 17: (1306, 1060), 18: (1324, 1192), 19: (1342, 1123),
         20: (1348, 1290), 21: (1359, 1121), 22: (1368, 1292), 23: (1380, 1295)}
TK3_XY = {0: (1011, 1355), 1: (1033, 1039), 2: (1069, 1285), 3: (1082, 1167), 4: (1114, 1300),
          5: (1119, 1011), 6: (1123, 1382), 7: (1126, 1138), 8: (1150, 1027), 9: (1162, 1167),
          10: (1168, 1290), 11: (1171, 1020), 12: (1173, 1333), 13: (1186, 1309), 14: (1210, 1263),
          15: (1237, 1333), 16: (1238, 1142), 17: (1240, 1299), 18: (1256, 1322), 19: (1280, 1274),
          20: (1312, 1181), 21: (1332, 1269), 22: (1339, 1307), 23: (1345, 1111), 24: (1351, 1161),
          25: (1354, 1312), 26: (1371, 1039), 27: (1371, 1185), 28: (1373, 1389), 29: (1376, 1303),
          30: (1384, 1244), 31: (1386, 1208)}

FIELDS = ['energy', 'weapons', 'prop', 'con', 'elec', 'bio']
JSON_FIELDS = ['energy', 'weapons', 'propulsion', 'construction', 'electronics', 'biotechnology']
NEG = '0x1b80'        # NRSE, CE, OBRM, LSP, BET: makes WM, AR, CA (and UR) legal (ORACLE.md)
UR_NEG = '0x1ba0'     # the same plus Ultimate Recycling (legal, checked before the runs)
QUEUE = [(1, 10), (0, 5), (2, 3), (4, 2), (5, 1)]   # auto factories, mines, defenses, min/max terraform

# ---------------------------------------------------------------- cost (COMPONENTS.md "Cost for an owner")

ITEMS = {x['name']: x for x in json.load(open(os.path.join(ROOT, 'data', 'components.json')))['items']}


def item_cost(name, tech, bet=False):
    """Minerals (I, B, G) of one unit for an owner at tech levels `tech`
    (six ints), COMPONENTS.md steps 1 and 3 (no race step applies to the
    hulls, engines and modules used here)."""
    it = ITEMS[name]
    req = [it['tech'][f] for f in JSON_FIELDS]
    if any(req):
        m = min(t - r for t, r in zip(tech, req) if r > 0)
    else:
        m = min(tech)
    c = [it['cost']['ironium'], it['cost']['boranium'], it['cost']['germanium']]
    if m > 0:
        d = min(5 * min(m, 19), 80) if bet else min(4 * min(m, 19), 75)
        c = [x if x == 0 else max(1, x - (x * d + 50) // 100) for x in c]
    elif bet and any(req):
        c = [2 * x for x in c]
    return c


def design_cost(parts, tech, bet=False):
    tot = [0, 0, 0]
    for name, n in parts:
        tot = [a + n * b for a, b in zip(tot, item_cost(name, tech, bet))]
    return tot


COLONIZER = [('Colony Ship', 1), ('Long Hump 6', 1), ('Colonization Module', 1)]
OCM_SHIP = [('Colony Ship', 1), ('Long Hump 6', 1), ('Orbital Construction Module', 1)]


def colony_minerals(parts, tech, bet=False, n=1):
    return [3 * x * n // 4 for x in design_cost(parts, tech, bet)]


def grow(p, g=15, carry=0):
    """Uncrowded growth (KERNEL.md), start population p in units of 100."""
    return p + (g * p + carry) // 100

# ---------------------------------------------------------------- spec writer

DESIGNS0 = """\
design 0 0 Mini Bomber, 1 Long Hump 6, 2 Cherry Bomb = Cherry2
design 0 1 Mini Bomber, 1 Long Hump 6, 2 Smart Bomb = Smart2
design 0 2 Mini Bomber, 1 Long Hump 6, 2 Peerless Bomb = Peerless2
design 0 3 Mini Bomber, 1 Long Hump 6, 1 Lady Finger Bomb = Lady1
design 0 4 Mini Bomber, 1 Long Hump 6, 1 LBU-17 Bomb = LBU17
design 0 5 Mini Bomber, 1 Long Hump 6, 1 LBU-32 Bomb = LBU32
design 0 6 Mini Bomber, 1 Long Hump 6, 1 Hush-a-Boom = Hush1
design 0 7 Mini Bomber, 1 Long Hump 6, 1 Retro Bomb = Retro1
design 0 8 Colony Ship, 1 Long Hump 6, 1 Orbital Construction Module = OCM
design 0 9 Frigate, 1 Long Hump 6, empty, 1 Multi Contained Munition, empty = MCM
design 0 10 Frigate, 1 Long Hump 6, empty, 2 Laser, empty = Laser Frigate
design 0 11 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
design 0 12 Colony Ship, 1 Long Hump 6, 1 Colonization Module = Colonizer
design 0 13 Mini-Miner, 1 Long Hump 6, empty, 1 Robo-Miner, 1 Robo-Miner = Miner24
"""
D_CHERRY2, D_SMART2, D_LADY1, D_LBU17, D_OCM, D_FREIGHTER, D_COLONIZER, D_MINER = 0, 1, 3, 4, 8, 11, 12, 13
DESIGN_PARTS0 = {0: ['Cherry Bomb'], 1: ['Smart Bomb'], 2: ['Peerless Bomb'], 3: ['Lady Finger Bomb'],
                 4: ['LBU-17 Bomb'], 5: ['LBU-32 Bomb'], 6: ['Hush-a-Boom'], 7: ['Retro Bomb'],
                 8: ['Orbital Construction Module'], 9: ['Multi Contained Munition'], 10: ['Laser'],
                 11: [], 12: ['Colonization Module'], 13: ['Robo-Miner']}
DESIGN_HULLS0 = {0: 'Mini Bomber', 1: 'Mini Bomber', 2: 'Mini Bomber', 3: 'Mini Bomber', 4: 'Mini Bomber',
                 5: 'Mini Bomber', 6: 'Mini Bomber', 7: 'Mini Bomber', 8: 'Colony Ship', 9: 'Frigate',
                 10: 'Frigate', 11: 'Medium Freighter', 12: 'Colony Ship', 13: 'Mini-Miner'}

PLANS0 = """\
plan 0 0 4 1 0 1 = Enemies
"""


class Run:
    """One spec. checks: (case, kind, args, expected) tuples read by check2.py."""

    def __init__(self, name, title, game='CB', years=1, cycles=(20000,)):
        self.name, self.title, self.game, self.years, self.cycles = name, title, game, years, cycles
        self.xy = CB_XY if game == 'CB' else TK3_XY
        self.hdr, self.lines, self.checks, self.cases = [], [], [], []
        self.fid = {}

    def h(self, s):
        self.hdr.append(s.rstrip('\n'))

    def tech(self, p, levels):
        for f, v in zip(FIELDS, levels):
            self.h(f'tech {p} {f} {v}')

    def case(self, cid, rule, text):
        self.cases.append((cid, rule, text))
        self.lines.append(f'# {cid} ({rule}): {text}')
        self.cur = cid

    def expect(self, kind, args, value, year=1):
        self.checks.append((self.cur, kind, args, value, year))

    def target(self, n, pop, owner=1, starbase=False, **kv):
        self.lines.append(f"planet {n} owner {owner} pop {pop} starbase {0 if starbase else 'none'}")
        kv.setdefault('env', '50,50,50')
        kv.setdefault('excess', 0)
        kv.setdefault('scanner', 31)
        kv.setdefault('fe', 0); kv.setdefault('bo', 0); kv.setdefault('ge', 0)
        self.lines.append(f"planetset {n} " + " ".join(f"{k}={v}" for k, v in kv.items()))

    def planetset(self, n, **kv):
        self.lines.append(f"planetset {n} " + " ".join(f"{k}={v}" for k, v in kv.items()))

    def _fleet(self, owner):
        i = self.fid.get(owner, 0)
        self.fid[owner] = i + 1
        return i

    def orbit(self, n, ships, owner=0, plan=0, cargo=None, task=None, fuel=200, then=None):
        i = self._fleet(owner)
        x, y = self.xy[n]
        s = f"fleet {owner} {i} planet {n} at {x} {y} ships {ships} plan {plan} fuel {fuel}"
        if cargo: s += " cargo " + " ".join(str(c) for c in cargo)
        if task: s += f" task {task}"
        if then is not None:
            tx, ty = self.xy[then]
            s += f" to {tx} {ty} planet {then} warp 6"
        self.lines.append(s)
        return i

    def arrive(self, n, ships, owner=0, plan=0, cargo=None, task=None, fuel=200, dy=20):
        """A fleet 20 ly from planet n that arrives this year (warp 6)."""
        i = self._fleet(owner)
        x, y = self.xy[n]
        sy = y + dy
        near = min(math.dist((x, sy), p) for k, p in self.xy.items() if k != n)
        assert near > 15, (self.name, n, near)
        s = f"fleet {owner} {i} at {x} {sy} ships {ships} plan {plan} fuel {fuel}"
        if cargo: s += " cargo " + " ".join(str(c) for c in cargo)
        s += f" to {x} {y} planet {n} warp 6"
        if task: s += f" task {task}"
        self.lines.append(s)
        return i

    def space(self, x, y, ships, owner=0, task=None):
        i = self._fleet(owner)
        near = min(math.dist((x, y), p) for p in self.xy.values())
        assert near > 30, (self.name, x, y, near)
        s = f"fleet {owner} {i} at {x} {y} ships {ships} plan 0 fuel 200"
        if task: s += f" task {task}"
        self.lines.append(s)
        return i

    def text(self):
        return (f"# {self.name}: {self.title}\n# generated by experiments/tk/gen2.py; game {self.game}, "
                f"{self.years} year(s)\n" + "\n".join(self.hdr) + "\n" + "\n".join(self.lines) + "\n")

    def write(self, out):
        with open(os.path.join(out, self.name + '.spec'), 'w') as f:
            f.write(self.text())


def cb_run(name, title, p0=(26,) * 6, p1=(3,) * 6, prt0=None, lrt0=None, prt1=None, lrt1=None,
           queue=False, rel=2, **kw):
    r = Run(name, title, **kw)
    r.h(f'relation 0 1 {rel}\nrelation 1 0 {rel}')
    r.tech(0, p0)
    r.tech(1, p1)
    r.h('research 0 0\nresearch 1 0')
    for p, prt, lrt in ((0, prt0, lrt0), (1, prt1, lrt1)):
        if prt is not None: r.h(f'prt {p} {prt}')
        if lrt is not None: r.h(f'lrt {p} {lrt}')
    if queue:
        r.h('defqueue 0 ' + ','.join(f'{i}:{c}' for i, c in QUEUE))
        r.h('defleftover 0 1')
    r.h(DESIGNS0)
    r.h('sbdesign 1 0 Orbital Fort = Bare Fort')
    r.h(PLANS0)
    return r


def qitems(skip=()):
    return [(i, c) for i, c in QUEUE if i not in skip]


def colonize_case(r, n, owner_tech, bet, queue_skip, design=D_COLONIZER, parts=COLONIZER, rule='T-26/T-36'):
    r.arrive(n, f'{design}:1', cargo=(0, 0, 0, 25), task='colonize')
    r.expect('planet', (n,), dict(owner=0, pop=25, surface=colony_minerals(parts, owner_tech, bet)))
    if queue_skip is not None:
        r.expect('queue', (n,), qitems(queue_skip))
        r.expect('planet', (n,), dict(leftover=True))


def runs():
    out = []
    T26 = (26,) * 6

    # T-36: colony minerals at tech 5, 10 and 15 everywhere
    for name, L in (('tk101', 5), ('tk102', 10), ('tk103', 15)):
        r = cb_run(name, f'T-36 colony ship minerals, player 0 at tech {L} in every field', p0=(L,) * 6)
        r.case('A', 'T-36', f'Colonizer (Colony Ship + Long Hump 6 + Colonization Module) arrives at unowned planet 21, colonize 25, tech {L}')
        colonize_case(r, 21, (L,) * 6, False, None)
        out.append(r)

    # T-37: design check at generation, electronics one short of LBU-17
    for name, field in (('tk104', 'energy'), ('tk105', 'elec')):
        r = cb_run(name, f'T-37 player 0 tech 26 except electronics 7; research field {field}',
                   p0=(26, 26, 26, 26, 7, 26))
        r.h(f'field 0 {field}')
        r.case('A', 'T-37', f'designs after generation; research field {field}')
        tech = (26, 26, 26, 26, 7, 26)
        for d, parts in DESIGN_PARTS0.items():
            keep = []
            for p in parts + [DESIGN_HULLS0[d], 'Long Hump 6']:
                it = ITEMS[p]
                short = any(tech[i] < it['tech'][f] for i, f in enumerate(JSON_FIELDS))
                exempt = it['mystery_trader'] or it['restriction']['prt_only'] or it['restriction']['prt_not']
                keep.append(not short or bool(exempt))
            r.expect('design', (0, d), 'kept' if all(keep) else 'part removed')
        out.append(r)

    # TK-106: War Monger attacker against JOAT; queue and leftover after capture
    r = cb_run('tk106', 'T-24/T-26 War Monger attacker (NRSE CE OBRM LSP BET), default queue and leftover',
               prt0=2, lrt0=NEG, queue=True)
    r.case('A', 'T-24', 'WM 100 arriving vs P=131 (150 after growth)')
    r.target(0, 131); r.arrive(0, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 100), task='unload')
    r.expect('planet', (0,), dict(owner=0, pop=9))
    r.case('A2', 'T-26', 'the captured planet gets the WM default queue and leftover setting')
    r.expect('queue', (0,), qitems())
    r.expect('planet', (0,), dict(leftover=True))
    r.case('B', 'control', 'P=131, nothing arrives')
    r.target(5, 131); r.expect('planet', (5,), dict(owner=1, pop=150))
    r.case('C', 'T-25', 'WM 600 arriving vs P=435 (500), 20 SDI')
    r.target(3, 435, defenses=20); r.arrive(3, f'{D_FREIGHTER}:3', cargo=(0, 0, 0, 600), task='unload')
    r.expect('planet', (3,), dict(owner=0, pop=248, defenses=0))
    r.case('D', 'T-26/BET', 'WM (BET) Colonizer arrives at unowned planet 21, colonize 25')
    colonize_case(r, 21, T26, True, ())
    out.append(r)

    # TK-107: Alternate Reality
    r = cb_run('tk107', 'T-33 Alternate Reality player 0 (NRSE CE OBRM LSP BET), default queue',
               prt0=8, lrt0=NEG, queue=True)
    r.case('A', 'T-33', 'AR OCM ship arrives at unowned planet 21, colonize 25')
    colonize_case(r, 21, T26, True, (0, 1, 2), design=D_OCM, parts=OCM_SHIP)
    r.expect('starbase', (21,), 0)
    r.case('B', 'T-33', 'AR freighter 100 arriving, unload on player 1 planet P=87')
    r.target(0, 87); i = r.arrive(0, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 100), task='unload')
    r.expect('planet', (0,), dict(owner=1, pop=100))
    r.expect('fleet', (0, i), dict(col=100))
    out.append(r)

    # TK-108: Claim Adjuster both sides
    r = cb_run('tk108', 'T-26 Claim Adjuster both players (NRSE CE OBRM LSP BET), default queue',
               prt0=3, lrt0=NEG, prt1=3, lrt1=NEG, queue=True)
    r.case('A', 'T-26', 'CA 100 arriving vs CA P=87, env 50/50/50 orig 55/47/52')
    r.target(0, 87, orig='55,47,52'); r.arrive(0, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 100), task='unload')
    r.expect('planet', (0,), dict(owner=0, pop=9, env=(55, 47, 52)))
    r.expect('queue', (0,), qitems((4, 5)))
    r.case('B', 'control', 'CA P=87, env 50/50/50 orig 55/47/52, nothing arrives')
    r.target(5, 87, orig='55,47,52'); r.expect('planet', (5,), dict(owner=1, pop=100, env=(50, 50, 50)))
    r.case('C', 'T-26/BET', 'CA Colonizer arrives at unowned planet 21, colonize 25')
    colonize_case(r, 21, T26, True, (4, 5))
    out.append(r)

    # TK-109: Inner Strength defender
    r = cb_run('tk109', 'T-24 Inner Strength defender', prt1=4)
    r.case('A', 'T-24', '150 arriving vs IS P=87 (100)')
    r.target(0, 87); r.arrive(0, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 150), task='unload')
    r.expect('planet', (0,), dict(owner=1, pop=18))
    r.case('B', 'T-24', '300 arriving vs IS P=87 (100)')
    r.target(3, 87); r.arrive(3, f'{D_FREIGHTER}:2', cargo=(0, 0, 0, 300), task='unload')
    r.expect('planet', (3,), dict(owner=0, pop=118))
    r.case('C', 'control', 'IS P=87, nothing arrives')
    r.target(5, 87); r.expect('planet', (5,), dict(owner=1, pop=100))
    out.append(r)

    # TK-110: War Monger against Inner Strength
    r = cb_run('tk110', 'T-24 War Monger attacker against Inner Strength', prt0=2, lrt0=NEG, prt1=4)
    r.case('A', 'T-24', 'WM 150 arriving vs IS P=87 (100)')
    r.target(0, 87); r.arrive(0, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 150), task='unload')
    r.expect('planet', (0,), dict(owner=0, pop=28))
    r.case('B', 'control', 'IS P=87, nothing arrives')
    r.target(5, 87); r.expect('planet', (5,), dict(owner=1, pop=100))
    out.append(r)

    # TK-111: scrap and remote mining, two years; player 1 has Ultimate Recycling
    r = cb_run('tk111', 'T-34 scrap and T-35 remote mining over two years; player 1 UR (plus NRSE CE OBRM LSP BET)',
               lrt1=UR_NEG, years=2)
    C = design_cost(COLONIZER, T26)
    C30 = [30 * c for c in C]

    def scr(f):
        return [f(c) for c in C30]
    r.case('S1', 'T-34', '30 Colonizers scrap at player 0 planet 0 with a starbase: 4C/5')
    r.target(0, 87, owner=0, starbase=True); r.orbit(0, f'{D_COLONIZER}:30', task='scrap')
    r.expect('planet', (0,), dict(surface=scr(lambda c: 4 * c // 5)))
    r.case('S2', 'T-34', '30 Colonizers scrap at player 0 planet 1 without a starbase: C/3')
    r.target(1, 87, owner=0); r.orbit(1, f'{D_COLONIZER}:30', task='scrap')
    r.expect('planet', (1,), dict(surface=scr(lambda c: c // 3)))
    r.case('S3', '#34/T-34', 'S2 at planet 2 with cargo 100/0/0 and 50 colonists: cargo added, colonists join before growth')
    r.target(2, 87, owner=0); r.orbit(2, f'{D_COLONIZER}:30', task='scrap', cargo=(100, 0, 0, 50))
    s = scr(lambda c: c // 3); s[0] += 100
    r.expect('planet', (2,), dict(surface=s, pop=grow(137)))
    r.case('S4', 'T-34', '30 Colonizers scrap at UR player 1 planet 3 with a starbase: 9C/10')
    r.target(3, 87, starbase=True); r.orbit(3, f'{D_COLONIZER}:30', task='scrap')
    r.expect('planet', (3,), dict(owner=1, surface=scr(lambda c: 9 * c // 10)))
    r.case('S5', 'T-34', '30 Colonizers scrap at UR player 1 planet 4 without a starbase: 9C/20')
    r.target(4, 87); r.orbit(4, f'{D_COLONIZER}:30', task='scrap')
    r.expect('planet', (4,), dict(owner=1, surface=scr(lambda c: 9 * c // 20)))
    r.case('S6', 'T-34', 'S5 at planet 5 with 50 colonists: colonists do not join (P 87 -> 100)')
    r.target(5, 87); r.orbit(5, f'{D_COLONIZER}:30', task='scrap', cargo=(0, 0, 0, 50))
    r.expect('planet', (5,), dict(owner=1, pop=100, surface=scr(lambda c: 9 * c // 20)))
    r.case('S7', 'T-34', '30 Colonizers scrap at unowned planet 6: C/3 on the surface')
    r.planetset(6, conc='50,50,50'); r.orbit(6, f'{D_COLONIZER}:30', task='scrap')
    r.expect('planet', (6,), dict(owner=-1, surface=scr(lambda c: c // 3)))
    r.case('S8', 'T-34', '30 Colonizers scrap in deep space at (1200,1220): C/3 salvage')
    r.space(1200, 1220, f'{D_COLONIZER}:30', task='scrap')
    r.expect('salvage', (1200, 1220), scr(lambda c: c // 3))
    r.case('S9', 'T-34', '30 Colonizers scrap at player 0 planet 7, second waypoint to planet 10: scrapped at 7')
    r.target(7, 87, owner=0); r.orbit(7, f'{D_COLONIZER}:30', task='scrap', then=10)
    r.expect('planet', (7,), dict(surface=scr(lambda c: c // 3)))
    r.case('S10', 'T-34', '30 Colonizers arrive at player 0 planet 9 with scrap: nothing in year 1, C/3 in year 2')
    r.target(9, 87, owner=0); f = r.arrive(9, f'{D_COLONIZER}:30', task='scrap')
    r.expect('planet', (9,), dict(surface=[0, 0, 0]))
    r.expect('fleet', (0, f), dict(ships=f'{D_COLONIZER}:30'))
    r.expect('planet', (9,), dict(surface=scr(lambda c: c // 3)), year=2)
    R = 24  # two Robo-Miners
    gain = [100 * R // 100, 50 * R // 100, 25 * R // 100]
    r.case('M1', 'T-35', 'Miner24 (24 robots) stationary at unowned planet 13, conc 100/50/25')
    r.planetset(13, conc='100,50,25'); r.orbit(13, f'{D_MINER}:1', task='mine')
    r.expect('planet', (13,), dict(surface=gain))
    r.expect('planet', (13,), dict(surface=[2 * g for g in gain]), year=2)
    r.case('M2', 'T-35', 'Miner24 arrives at unowned planet 14, conc 100/50/25: nothing in year 1, mines in year 2')
    r.planetset(14, conc='100,50,25'); r.arrive(14, f'{D_MINER}:1', task='mine')
    r.expect('planet', (14,), dict(surface=[0, 0, 0]))
    r.expect('planet', (14,), dict(surface=gain), year=2)
    r.case('M3', 'T-35', 'Miner24 stationary at player 1 planet 15: nothing')
    r.target(15, 87); r.orbit(15, f'{D_MINER}:1', task='mine')
    r.expect('planet', (15,), dict(surface=[0, 0, 0]))
    r.case('M4', 'T-35', 'Miner24 stationary at player 0 planet 16: nothing')
    r.target(16, 87, owner=0); r.orbit(16, f'{D_MINER}:1', task='mine')
    r.expect('planet', (16,), dict(surface=[0, 0, 0]))
    out.append(r)

    # TK-113: three players: bombing order, colonize retries
    r = Run('tk113', 'several bombers on one planet; colonize retries after a tie (three players, Super Stealth, growth 10%)',
            game='TK3')
    r.h('relation 0 1 2\nrelation 1 0 2\nrelation 2 1 2\nrelation 1 2 2\nrelation 0 2 1\nrelation 2 0 1')
    r.tech(0, T26); r.tech(2, T26)
    r.h('research 0 0\nresearch 1 0\nresearch 2 0')
    for p in (0, 2):
        r.h(f'design {p} 0 Mini Bomber, 1 Long Hump 6, 2 Cherry Bomb = Cherry2\n'
            f'design {p} 1 Mini Bomber, 1 Long Hump 6, 2 Smart Bomb = Smart2\n'
            f'design {p} 2 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter\n'
            f'design {p} 3 Colony Ship, 1 Long Hump 6, 1 Colonization Module = Colonizer')
    r.case('B1', 'bombing order', 'players 0 and 2, 10 Cherry each, on player 1 P=728 (800): 800 -> 600 -> 450')
    r.target(13, 728); r.orbit(13, '0:5', owner=0); r.orbit(13, '0:5', owner=2)
    r.expect('planet', (13,), dict(owner=1, pop=450))
    r.case('B2', 'bombing order', 'player 0 10 Smart, player 2 10 Cherry, on P=37 (40): smart first 40 -> 36 -> 6')
    r.target(9, 37); r.orbit(9, '1:5', owner=0); r.orbit(9, '0:5', owner=2)
    r.expect('planet', (9,), dict(owner=1, pop=6))
    r.case('B3', 'bombing order', 'player 0 10 Cherry, player 2 10 Smart, on P=37 (40): cherry first 40 -> 10 -> 9')
    r.target(3, 37); r.orbit(3, '0:5', owner=0); r.orbit(3, '1:5', owner=2)
    r.expect('planet', (3,), dict(owner=1, pop=9))
    cm = colony_minerals(COLONIZER, T26)
    r.case('R1', '#34 retry', 'before movement: players 0 and 2 unload 150 each on P=100 (tie, emptied), '
           'player 0 Colonizer in orbit retries: player 0 owns 25 after movement')
    r.target(23, 100)
    c = r.orbit(23, '3:1', owner=0, cargo=(0, 0, 0, 25), task='colonize')
    r.orbit(23, '2:1', owner=0, cargo=(0, 0, 0, 150), task='unload')
    r.orbit(23, '2:1', owner=2, cargo=(0, 0, 0, 150), task='unload')
    r.expect('planet', (23,), dict(owner=0, pop=25, surface=cm))
    r.expect('nofleet', (0, c), None)
    r.case('R2', '#34 retry LEGACY BUG', 'after movement: players 0 and 2 arrive with 150 each on P=100 (110), '
           'player 0 Colonizer arrives: retry consumes it, colonists lost, planet unowned')
    r.target(26, 100)
    c = r.arrive(26, '3:1', owner=0, cargo=(0, 0, 0, 25), task='colonize')
    r.arrive(26, '2:1', owner=0, cargo=(0, 0, 0, 150), task='unload')
    r.arrive(26, '2:1', owner=2, cargo=(0, 0, 0, 150), task='unload')
    r.expect('planet', (26,), dict(owner=-1, surface=cm))
    r.expect('nofleet', (0, c), None)
    out.append(r)

    # TK-114: phase-start ownership; own-planet unloads
    r = cb_run('tk114', '#34 phase-start ownership record and own-planet unload amounts; player 1 Lady Finger bombers',
               p1=T26)
    r.h('design 1 0 Mini Bomber, 1 Long Hump 6, 2 Lady Finger Bomb = Lady2')
    r.h('plan 1 0 4 1 0 1 = Enemies')
    cm = colony_minerals(COLONIZER, T26)
    r.case('PS1', '#34 phase start', 'unowned planet 13: player 0 Colonizer in orbit colonizes 25 (28 after growth), '
           'player 1 10 Lady Finger bomb it empty, player 0 freighter arrives with 50 and unloads: player 0 owns 50')
    r.planetset(13, env='50,50,50')
    r.orbit(13, f'{D_COLONIZER}:1', cargo=(0, 0, 0, 25), task='colonize')
    r.orbit(13, '0:5', owner=1)
    f = r.arrive(13, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 50), task='unload')
    r.expect('planet', (13,), dict(owner=0, pop=50, surface=cm))
    r.expect('fleet', (0, f), dict(col=0))
    r.case('PS2', 'T-4 control', 'unowned planet 16 with player 1 bombers in orbit; player 0 freighter arrives with 50: refused, keeps 50')
    r.orbit(16, '0:5', owner=1)
    f = r.arrive(16, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 50), task='unload', dy=-20)
    r.expect('planet', (16,), dict(owner=-1))
    r.expect('fleet', (0, f), dict(col=50))
    r.case('U1', '#34 unload', 'own planet 0 P=87, freighter in orbit unloads all 50 before growth: 137 -> 157')
    r.target(0, 87, owner=0); f = r.orbit(0, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 50), task='transport -,-,-,2:0,-')
    r.expect('planet', (0,), dict(pop=grow(137))); r.expect('fleet', (0, f), dict(col=0))
    r.case('U2', '#34 unload', 'own planet 1 P=87, freighter arrives and unloads all 50 after growth: 100 + 50')
    r.target(1, 87, owner=0); f = r.arrive(1, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 50), task='unload')
    r.expect('planet', (1,), dict(pop=150)); r.expect('fleet', (0, f), dict(col=0))
    r.case('U3', '#34 unload', 'own planet 2 P=87, in orbit, cargo 100/40/0/50: unload exactly 30 Ir, all Bo, exactly 20 colonists')
    r.target(2, 87, owner=0)
    f = r.orbit(2, f'{D_FREIGHTER}:1', cargo=(100, 40, 0, 50), task='transport 4:30,2:0,-,4:20,-')
    r.expect('planet', (2,), dict(pop=grow(107), surface=[30, 40, 0]))
    r.expect('fleet', (0, f), dict(fe=70, bo=0, col=30))
    r.case('U4', '#34 unload', 'own planet 3 P=87, in orbit, cargo 100/0/0/50: set amount Ir 60, colonists 10')
    r.target(3, 87, owner=0)
    f = r.orbit(3, f'{D_FREIGHTER}:1', cargo=(100, 0, 0, 50), task='transport 8:60,-,-,8:10,-')
    r.expect('planet', (3,), dict(pop=grow(127), surface=[40, 0, 0]))
    r.expect('fleet', (0, f), dict(fe=60, col=10))
    r.case('U5', '#34 unload', 'own planet 4 P=87, in orbit, cargo 100/0/0/50: unload exactly 500 Ir (capped at 100), '
           'set waypoint colonists to 120 (unloads 33)')
    r.target(4, 87, owner=0)
    f = r.orbit(4, f'{D_FREIGHTER}:1', cargo=(100, 0, 0, 50), task='transport 4:500,-,-,9:120,-')
    r.expect('planet', (4,), dict(pop=grow(120), surface=[100, 0, 0]))
    r.expect('fleet', (0, f), dict(fe=0, col=17))
    out.append(r)

    # TK-115: tech attempt on capture, several streams
    r = cb_run('tk115', '#34 tech on capture: player 0 tech 3, player 1 weapons 10; two captures',
               p0=(3,) * 6, p1=(3, 10, 3, 3, 3, 3),
               cycles=(20000, 12000, 15000, 25000, 30000, 40000, 50000, 17000))
    for cid, n in (('A', 0), ('B', 5)):
        r.case(cid, '#34 tech', f'100 arriving vs P=87 (100) on planet {n}: captured with 9')
        r.target(n, 87); r.arrive(n, f'{D_FREIGHTER}:1', cargo=(0, 0, 0, 100), task='unload')
        r.expect('planet', (n,), dict(owner=0, pop=9))
    r.case('T', '#34 tech', 'player 0 ends at weapons 3 or 4 (one gain at most per year), other fields 3')
    r.expect('tech', (0,), 'weapons 3 or 4; others 3')
    out.append(r)
    return out


def table():
    for r in runs():
        print(f'### {r.name.upper()}: {r.title}')
        print()
        cyc = '' if len(r.cycles) == 1 else f' Cycles {", ".join(map(str, r.cycles))}.'
        print(f'Game {r.game}, {r.years} year(s).{cyc}')
        print()
        print('| Case | Rule | Setup | Predicted |')
        print('|---|---|---|---|')
        for cid, rule, text in r.cases:
            pred = '; '.join(fmt(k, a, v, y) for c, k, a, v, y in r.checks if c == cid)
            print(f'| {cid} | {rule} | {text} | {pred} |')
        print()


def fmt(kind, args, v, year):
    y = '' if year == 1 else f' (year {year})'
    if kind == 'planet':
        return f'planet {args[0]}: ' + ', '.join(
            f'{k} {"/".join(map(str, x)) if isinstance(x, (list, tuple)) else x}' for k, x in v.items()) + y
    if kind == 'queue':
        return f'queue {args[0]}: ' + (', '.join(f'{i}:{c}' for i, c in v) or 'none') + y
    if kind == 'fleet':
        return f'fleet {args[0]}/{args[1]}: ' + ', '.join(f'{k} {x}' for k, x in v.items()) + y
    if kind == 'nofleet':
        return f'fleet {args[0]}/{args[1]} gone' + y
    if kind == 'design':
        return f'design {args[1]} {v}' + y
    if kind == 'starbase':
        return f'planet {args[0]} starbase design {v}' + y
    if kind == 'salvage':
        return f'salvage at {args[0]},{args[1]}: {"/".join(map(str, v))}' + y
    return f'{kind} {args} {v}' + y


if __name__ == '__main__':
    if sys.argv[1:] == ['--table']:
        table()
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else HERE
        for r in runs():
            r.write(out)
            print(r.name, len(r.cases), 'cases', len(r.checks), 'checks')
