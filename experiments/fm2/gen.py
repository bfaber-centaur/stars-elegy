#!/usr/bin/env python3
"""Write the FM round-2 (FM-101..FM-104) Combat Lab specs, with predictions.

FM round 2 tests the movement and fuel rules of docs/KERNEL.md "Fleet
movement" that FM-001..004 did not reach (BINARY-ONLY there, or "not
exercised"):

- Improved Fuel Efficiency (engine factor f - trunc(15f/100)); Cheap
  Engines (a 1 in 10 chance at warp 7+ that a fleet does not move);
- warp 10 on an engine not rated for it (each ship lost with chance 1/10;
  cargo and fuel leave with lost ships), and rated engines at warp 10;
- ram scoops on a design with two engines; a design whose engine slot is
  not full (stars-decomp reading: factor 99999);
- fuel generators (anti-matter generator +50, fuel transport hull +200);
- refuelling at a friend's starbase, at a starbase without a dock, and at
  an enemy's dock; fuel unloaded onto a planet;
- "a fleet whose current task is transport or lay mines does not move";
- a fleet that cannot afford its whole leg but keeps fuel keeps its warp;
- designs with equal engine factor: cargo in the fleet's design order;
- chasers that are fuel-limited, ram-scoop or top up (rule 6);
- movement order between two players' fleets;
- rounding toward negative coordinates; Radiating Hydro-Ram Scoop
  colonist losses;
- waypoint chains across years (FM-104, two years).

Predictions come from KERNEL.md (stars-elegy main 004b4dc) through
model.py; where KERNEL.md is silent, the stars-decomp reading
(fleet-movement.md, fleet-fuel.md) is named. COMPONENTS.md engine tables
and masses are used as given. Random cases (CE, warp 10) predict a
distribution, not a value.

  python3 experiments/fm2/gen.py OUTDIR      # write fmNNN.spec files
  python3 experiments/fm2/gen.py --table     # print the prediction table
"""
import copy, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'tk'))
from model import Design, Fleet, year, dist  # noqa: E402
from gen2 import Run, CB_XY, FIELDS  # noqa: E402

ITEMS = {x['name']: x for x in json.load(open(os.path.join(ROOT, 'data', 'components.json')))['items']}

# ---------------------------------------------------------------- designs (player 0)
# number: (spec parts, engine, engines per ship, full engine slot)
DESIGNS = {
    0: ('Scout, 1 Quick Jump 5, empty, 1 Fuel Tank', 'QJ5 scout'),
    1: ('Scout, 1 Long Hump 6, empty, 1 Fuel Tank', 'LH6 scout'),
    2: ('Scout, 1 Trans-Star 10, empty, 1 Fuel Tank', 'TS10 scout'),
    3: ('Scout, 1 Radiating Hydro-Ram Scoop, empty, 1 Fuel Tank', 'RHRS scout'),
    4: ('Scout, 1 Fuel Mizer, empty, 1 Fuel Tank', 'FM scout'),
    5: ('Scout, 1 Long Hump 6, empty, 1 Anti-matter Generator', 'AMG scout'),
    6: ('Super-Fuel Xport, 2 Long Hump 6, empty, empty', 'SFX'),
    7: ('Large Freighter, 2 Radiating Hydro-Ram Scoop, empty, empty', 'LF 2 RHRS'),
    8: ('Large Freighter, 1 Long Hump 6, empty, empty', 'LF 1 of 2 LH6'),
    9: ('Medium Freighter, 1 Radiating Hydro-Ram Scoop, empty, empty', 'MF RHRS'),
    10: ('Small Freighter, 1 Quick Jump 5, empty, empty', 'SF QJ5'),
    11: ('Small Freighter, 1 Long Hump 6, empty, empty', 'SF LH6'),
    12: ('Scout, 1 Long Hump 6, empty, 1 Mine Dispenser 40', 'minelayer'),
    13: ('Medium Freighter, 1 Long Hump 6, empty, empty', 'MF LH6'),
    14: ('Small Freighter, 1 Long Hump 6, empty, empty', 'SF LH6 (second)'),
    15: ('Small Freighter, 1 Quick Jump 5, empty, empty', 'SF QJ5 (second)'),
}
ENGINE_NAMES = {'Quick Jump 5', 'Long Hump 6', 'Trans-Star 10', 'Radiating Hydro-Ram Scoop', 'Fuel Mizer'}


def design(num):
    parts = [p.strip() for p in DESIGNS[num][0].split(',')]
    hull = ITEMS[parts[0]]
    mass, tank, cargo = hull['mass'], hull['stats']['fuel_capacity'], hull['stats']['cargo_capacity']
    engine, e = None, 0
    for p in parts[1:]:
        if p == 'empty':
            continue
        n, name = p.split(' ', 1)
        it = ITEMS[name]
        mass += int(n) * it['mass']
        tank += int(n) * it['stats'].get('fuel_capacity', 0)
        if name in ENGINE_NAMES:
            engine, e = name, int(n)
    full = e == hull['stats']['slots'][0]['max']
    return Design(num, mass, engine, e=e, full=full, cargo=cargo, tank=tank)


D = {n: design(n) for n in DESIGNS}
P1_SCOUT = 6     # player 1's LH6 scout (spec below)


class FmRun(Run):
    def __init__(self, name, title, years=1, rel01=2, rel10=2, lrt0=None, p1tech=26):
        super().__init__(name, title, years=years)
        self.h(f'relation 0 1 {rel01}\nrelation 1 0 {rel10}')
        self.tech(0, (26,) * 6)
        self.tech(1, (p1tech,) * 6)
        self.h('research 0 0\nresearch 1 0')
        if lrt0 is not None:
            self.h(f'lrt 0 {lrt0}')
        self.ife = lrt0 is not None and int(lrt0, 16) & 1
        for n, (parts, label) in DESIGNS.items():
            self.h(f'design 0 {n} {parts} = {label}')
        self.h(f'design 1 {P1_SCOUT} Scout, 1 Long Hump 6, empty, 1 Fuel Tank = LH6 scout')
        # combatlab replaces a player's starbase designs, so the homeworlds' design 0 is restated
        # (unarmed, so no battle at a homeworld)
        self.h('sbdesign 0 0 Space Station = Bare Station\nsbdesign 1 0 Space Station = Bare Station\n'
               'sbdesign 0 1 Orbital Fort = Bare Fort\nsbdesign 1 1 Space Dock = Bare Dock\nsbdesign 1 2 Orbital Fort = Bare Fort')
        self.h('plan 0 0 0 1 0 0 = Dodge')
        self.model = []       # Fleet objects in host order (owner, number)
        self.row = 1005
        self.pos = {}

    def text(self):
        return super().text().replace('experiments/tk/gen2.py', 'experiments/fm2/gen.py')

    def lane(self):
        y = self.row
        self.row += 6
        assert y < 1396
        return y

    def fleet(self, ships, at, fuel, cargo=(0, 0, 0, 0), wps=(), owner=0, planet=None, extra='', model=True):
        """ships: {design: count}; wps: [(x, y, warp)] or [((owner, id), warp)]."""
        i = self._fleet(owner)
        s = f'fleet {owner} {i} '
        if planet is not None:
            s += f'planet {planet} '
        s += f'at {at[0]} {at[1]} ships ' + ','.join(f'{d}:{c}' for d, c in ships.items())
        s += f' plan 0 fuel {fuel} cargo ' + ' '.join(map(str, cargo))
        for w in wps:
            if isinstance(w[0], tuple):
                o, n = w[0]
                tx, ty = self.pos[(o, n)]
                s += f' to {tx} {ty} fleet {o} {n} warp {w[1]}'
            else:
                assert (w[0], w[1]) not in CB_XY.values(), w
                s += f' to {w[0]} {w[1]} warp {w[2]}'
        if extra:
            s += ' ' + extra
        assert planet is not None or tuple(at) not in CB_XY.values(), at
        self.lines.append(s)
        self.pos[(owner, i)] = at
        if model:
            stacks = [(D[d] if owner == 0 else D[1], c) for d, c in sorted(ships.items())]
            f = Fleet((owner, i), at[0], at[1], stacks, fuel, sum(cargo), list(wps), ife=self.ife and owner == 0)
            self.model.append(f)
        return i

    def predict(self, years=1):
        """Run the KERNEL model over this run's fleets; returns {key: [state after year 1, 2, ...]}."""
        fl = copy.deepcopy(sorted(self.model, key=lambda f: f.key))
        out = {f.key: [] for f in fl}
        for _ in range(years):
            for f in fl:
                f.dry, f.warp_after = False, None
            year(fl)
            for f in fl:
                if f.warp_after is not None and f.wps:
                    w = f.wps[0]
                    f.wps[0] = (w[0], w[1], f.warp_after) if len(w) == 3 else (w[0], f.warp_after)
                warp = (f.wps[0][-1] if f.wps else None)
                out[f.key].append(dict(x=f.x, y=f.y, fuel=f.fuel, warp=warp))
        return out


def runs():
    out = []

    # ================================================================ FM-101: IFE and Cheap Engines
    r = FmRun('fm101', 'Improved Fuel Efficiency and Cheap Engines (player 0 IFE + NRSE CE OBRM LSP BET)', lrt0='0x1b81')
    keys = {}
    r.case('A', 'KERNEL IFE', 'QJ5 scout, warp 6, +100 x, 300 mg: factor 180 - 27 = 153')
    y = r.lane(); keys['A'] = r.fleet({0: 1}, (1005, y), 300, wps=[(1105, y, 6)])
    r.case('B', 'KERNEL IFE', 'LH6 scout, warp 5, +25 x, 300 mg: factor 100 - 15 = 85; arrives')
    y = r.lane(); keys['B'] = r.fleet({1: 1}, (1005, y), 300, wps=[(1030, y, 5)])
    r.case('C', 'KERNEL IFE', 'three QJ5 scouts, warp 4, +16 x: factor 100 - 15 = 85')
    y = r.lane(); keys['C'] = r.fleet({0: 3}, (1005, y), 300, wps=[(1021, y, 4)])
    r.case('D', 'KERNEL IFE / running dry', 'QJ5 scout, warp 6, +100 x, 2 mg: range with the IFE factor, ends 0, warp 1')
    y = r.lane(); keys['D'] = r.fleet({0: 1}, (1005, y), 2, wps=[(1105, y, 6)])
    r.case('E', 'KERNEL IFE / ram scoop', 'RHRS scout, warp 4, +100 x, 100 mg: free warp, gain 6 x 16 = 96 (IFE does not touch a zero factor)')
    y = r.lane(); keys['E'] = r.fleet({3: 1}, (1005, y), 100, wps=[(1105, y, 4)])
    pred = r.predict()
    for cid in 'ABCDE':
        p = pred[(0, keys[cid])][0]
        r.cur = cid
        r.expect('fleet', (0, keys[cid]), dict(x=p['x'], y=p['y'], fuel=p['fuel'], warp=p['warp']))
    r.case('F', 'KERNEL CE', '40 QJ5 scouts, one per fleet, warp 7, +49 x from one point: each fleet has a 1 in 10 '
           'chance of not moving (then 300 mg kept, waypoint kept); expect about 4 (0-9 covers 99%)')
    y = r.lane(); ce = [r.fleet({0: 1}, (1005, y), 300, wps=[(1054, y, 7)], model=False) for _ in range(40)]
    r.expect('ce', tuple((0, i) for i in ce), dict(start=(1005, y), dest=(1054, y), lo=0, hi=9))
    r.case('G', 'KERNEL CE', 'control: 20 QJ5 scouts, warp 6, +36 x: every fleet moves (warp 6 is exempt)')
    y = r.lane(); ce6 = [r.fleet({0: 1}, (1005, y), 300, wps=[(1041, y, 6)], model=False) for _ in range(20)]
    r.expect('ce', tuple((0, i) for i in ce6), dict(start=(1005, y), dest=(1041, y), lo=0, hi=0))
    out.append(r)

    # ================================================================ FM-102: JOAT, the rest
    r = FmRun('fm102', 'warp 10, two-engine ram scoops, an under-engined design, fuel generators, starbases, '
              'task gates, keeping warp, equal factors, chasers, rounding, RHRS colonists')
    keys = {}
    r.case('A', 'KERNEL warp 10', '100 LH6 scouts in one fleet, warp 10, +100 x, 30000 mg: each ship lost with chance '
           '1/10 (expect about 10; 2-20 covers 99.6%); the survivors\' fuel = 30000 - trunc(30000 x lost/100) - cost')
    y = r.lane(); a = r.fleet({1: 100}, (1005, y), 30000, wps=[(1105, y, 10)], model=False)
    r.expect('warp10', (0, a), dict(n0=100, lo=2, hi=20, design=1, fuel0=30000, dist=100, x=1105, y=y))
    r.case('B', 'KERNEL warp 10', '50 Trans-Star 10 scouts (rated), warp 10, +100 x: none lost')
    y = r.lane(); b = r.fleet({2: 50}, (1005, y), 15000, wps=[(1105, y, 10)])
    r.case('C', 'KERNEL warp 10', 'one fleet of 50 LH6 and 50 Trans-Star 10 scouts, warp 10: only LH6 scouts are lost')
    y = r.lane(); c = r.fleet({1: 50, 2: 50}, (1005, y), 30000, wps=[(1105, y, 10)], model=False)
    r.expect('warp10mix', (0, c), dict(lost_design=1, kept=f'2:50', lo=0, hi=13, x=1105, y=y))
    r.case('D', 'KERNEL ram scoop (e = 2)', 'Large Freighter with 2 RHRS, warp 4, +100 x, 1000 mg: 2 x 6 x 16 = 192')
    y = r.lane(); keys['D'] = r.fleet({7: 1}, (1005, y), 1000, wps=[(1105, y, 4)])
    r.case('E', 'KERNEL ram scoop (e = 2)', 'the same at warp 2 (free 3, 4, 5): 2 x 10 x 4 = 80')
    y = r.lane(); keys['E'] = r.fleet({7: 1}, (1005, y), 1000, wps=[(1105, y, 2)])
    r.case('F', 'decomp (engine slot not full)', 'Large Freighter with 1 of 2 LH6, warp 5, +100 x, 2600 mg: '
           'factor 99999, so it moves only its tiny range and ends with 0 (warp unchanged: no warp is free)')
    y = r.lane(); keys['F'] = r.fleet({8: 1}, (1005, y), 2600, wps=[(1105, y, 5)])
    r.case('G', 'KERNEL generators', 'AMG scout stationary in deep space, 100 of 250 mg: +50')
    y = r.lane(); keys['G'] = r.fleet({5: 1}, (1005, y), 100)
    r.case('H', 'KERNEL generators', 'AMG scout, warp 5, +25 x, 100 mg: pays the move, then +50')
    y = r.lane(); keys['H'] = r.fleet({5: 1}, (1005, y), 100, wps=[(1030, y, 5)])
    r.case('I', 'KERNEL generators', 'AMG scout stationary, 230 of 250 mg: capped at 250')
    y = r.lane(); keys['I'] = r.fleet({5: 1}, (1005, y), 230)
    r.case('J', 'KERNEL generators', '2 Super-Fuel Xports stationary, 1000 of 4500 mg: +200 each')
    y = r.lane(); keys['J'] = r.fleet({6: 2}, (1005, y), 1000)
    r.case('K', 'KERNEL generators', 'Super-Fuel Xport, warp 6, +36 x, 1000 mg: pays, then +200')
    y = r.lane(); keys['K'] = r.fleet({6: 1}, (1005, y), 1000, wps=[(1041, y, 6)])
    pred = r.predict()
    gen = {'G': 50, 'H': 50, 'I': 50, 'J': 400, 'K': 200}
    for cid in 'DEFGHIJK':
        p = pred[(0, keys[cid])][0]
        r.cur = cid
        tank = next(f for f in r.model if f.key == (0, keys[cid])).tank
        r.expect('fleet', (0, keys[cid]), dict(x=p['x'], y=p['y'], fuel=min(p['fuel'] + gen.get(cid, 0), tank)))
    r.cur = 'B'
    r.expect('fleet', (0, b), dict(ships='2:50', x=1105, y=r.pos[(0, b)][1]))
    # starbases (planets: player 1's 5 with an unarmed Space Dock, player 0's 0 with an Orbital Fort)
    r.case('L', 'decomp _FuelFleets', 'QJ5 scout (50 mg) orbiting player 1\'s planet 5 with a Space Dock; player 1 is an '
           'enemy toward player 0: not refuelled')
    r.lines.append('planet 5 owner 1 pop 87 starbase 1')
    l = r.fleet({0: 1}, CB_XY[5], 50, planet=5, model=False)
    r.expect('fleet', (0, l), dict(fuel=50))
    r.case('M', 'KERNEL (dock needed)', 'QJ5 scout (50 mg) orbiting player 0\'s planet 0 with an Orbital Fort: not refuelled')
    r.lines.append('planet 0 owner 0 pop 87 starbase 1')
    m = r.fleet({0: 1}, CB_XY[0], 50, planet=0, model=False)
    r.expect('fleet', (0, m), dict(fuel=50))
    r.case('N', 'KERNEL (fuel onto a planet)', 'MF LH6 at own planet 1 (no starbase), 300 mg, transport "unload all" fuel: '
           'the fleet ends with 0 (fuel unloaded onto a planet is lost)')
    r.lines.append('planet 1 owner 0 pop 87 starbase none')
    n_ = r.fleet({13: 1}, CB_XY[1], 300, planet=1, extra='task transport -,-,-,-,2:0', model=False)
    r.expect('fleet', (0, n_), dict(fuel=0))
    r.case('O', 'KERNEL task gate', 'minelayer scout with "lay mines" at waypoint 0 and a second waypoint 30 ly away, warp 5: '
           'does not move')
    y = r.lane(); o = r.fleet({12: 1}, (1005, y), 50, wps=[(1035, y, 5)], model=False)
    r.lines[-1] = r.lines[-1].replace(' to ', ' task lay to ', 1)
    r.expect('fleet', (0, o), dict(x=1005, y=y))
    r.case('P', 'decomp task gate', 'MF LH6 at own planet 2 with 50 Ir, transport "unload all" Ir at waypoint 0, second '
           'waypoint 30 ly away, warp 5: unloads before movement, the task ends, it moves (KERNEL\'s "transport does not '
           'move" holds only while the task is open)')
    r.lines.append('planet 2 owner 0 pop 87 starbase none')
    x2, y2 = CB_XY[2]
    p_ = r.fleet({13: 1}, (x2, y2), 300, cargo=(50, 0, 0, 0), planet=2, model=False,
                 extra=f'task transport 2:0,-,-,-,- to {x2 + 30} {y2} warp 5')
    r.expect('fleet', (0, p_), dict(x=x2 + 25, y=y2, fe=0))
    r.case('Q', 'KERNEL (BINARY-ONLY, no corpus case)', 'QJ5 scout, warp 6, +100 x, 10 mg: cannot afford the leg (14 mg) '
           'but keeps fuel after this year\'s 36 ly: keeps warp 6')
    y = r.lane(); keys['Q'] = r.fleet({0: 1}, (1005, y), 10, wps=[(1105, y, 6)])
    # equal factors: QJ5 and LH6 both have factor 100 at warp 5
    r.case('R', 'KERNEL (equal factors, BINARY-ONLY)', 'SF QJ5 (design 10) + SF LH6 (design 11), 50 kT, warp 5, +25 x: '
           'cargo on design 10 first: 140 tenths, 14 mg (design 11 first would give 141, 15 mg)')
    y = r.lane(); keys['R'] = r.fleet({10: 1, 11: 1}, (1005, y), 130, cargo=(50, 0, 0, 0), wps=[(1030, y, 5)])
    r.case('S', 'KERNEL (equal factors, BINARY-ONLY)', 'SF LH6 (design 14) + SF QJ5 (design 15), 50 kT, warp 5, +25 x: '
           'cargo on design 14 first: 141 tenths, 15 mg')
    y = r.lane(); keys['S'] = r.fleet({14: 1, 15: 1}, (1005, y), 130, cargo=(50, 0, 0, 0), wps=[(1030, y, 5)])
    # chasers of a stationary target (rule 6 with one round)
    r.case('T', 'KERNEL chaser rule 6', 'QJ5 scout (2 mg), warp 6, chasing a stationary scout 100 ly away: fuel-limited '
           'like an ordinary leg, ends with 0, warp 1')
    y = r.lane(); t0 = r.fleet({0: 1}, (1105, y), 300)
    keys['T'] = r.fleet({0: 1}, (1005, y), 2, wps=[((0, t0), 6)])
    r.case('U', 'KERNEL chaser rule 6', 'FM scout (100 mg), warp 4, chasing a stationary scout 100 ly away: ram scoop +16')
    y = r.lane(); u0 = r.fleet({0: 1}, (1105, y), 300)
    keys['U'] = r.fleet({4: 1}, (1005, y), 100, wps=[((0, u0), 4)])
    r.case('V', 'KERNEL chaser rule 6', 'QJ5 scout (102 mg), warp 9, chasing a stationary scout 126 ly away: topped up to 37')
    y = r.lane(); v0 = r.fleet({0: 1}, (1131, y), 300)
    keys['V'] = r.fleet({0: 1}, (1005, y), 102, wps=[((0, v0), 9)])
    r.case('W', 'KERNEL rounding (negative)', 'QJ5 scout, warp 5, from (1395, 1395) toward (1345, 1366): rounds half away '
           'from zero on both axes')
    keys['W'] = r.fleet({0: 1}, (1395, 1395), 300, wps=[(1345, 1366, 5)])
    r.case('X', 'KERNEL rounding (negative)', 'QJ5 scout, warp 6, from (1395, 1380) toward (1300, 1349)')
    keys['X'] = r.fleet({0: 1}, (1395, 1380), 300, wps=[(1300, 1349, 6)])
    r.case('Y', 'KERNEL rounding (mixed)', 'QJ5 scout, warp 7, from (1390, 1010) toward (1290, 1067)')
    keys['Y'] = r.fleet({0: 1}, (1390, 1010), 300, wps=[(1290, 1067, 7)])
    pred = r.predict()
    for cid in 'QRSTUVWXY':
        p = pred[(0, keys[cid])][0]
        r.cur = cid
        r.expect('fleet', (0, keys[cid]), dict(x=p['x'], y=p['y'], fuel=p['fuel'], warp=p['warp']))
    # RHRS colonist losses: JOAT radiation 15..85, mid 50: trunc((86 - 50)/2) = 18
    for cid, col, move in (('Z1', 100, True), ('Z2', 3, True), ('Z3', 100, False)):
        kill = max(1, col * 18 // 100) if move else 0
        r.case(cid, 'KERNEL RHRS colonists', f'MF RHRS with {col} kT colonists, ' + ('warp 4, +100 x' if move else 'stationary')
               + f': loses {kill}')
        y = r.lane()
        k = r.fleet({9: 1}, (1005, y), 300, cargo=(0, 0, 0, col), wps=[(1105, y, 4)] if move else (), model=False)
        r.expect('fleet', (0, k), dict(col=col - kill))
    # movement order between players: player 0's chaser has the higher fleet number
    r.case('ZO', 'KERNEL order (owner before number)', 'player 0 QJ5 scout (fleet number high) and player 1 LH6 scout '
           '(fleet 0) chase each other at warp 4, 20 ly apart: player 0 moves first (12 ly), player 1 meets it (8)')
    y = r.lane()
    q1 = r._fleet(1)
    r.lines.append(f'fleet 1 {q1} at 1025 {y} ships {P1_SCOUT}:1 plan 0 fuel 300 cargo 0 0 0 0')
    r.pos[(1, q1)] = (1025, y)
    q0 = r.fleet({0: 1}, (1005, y), 300, wps=[((1, q1), 4)], model=False)
    r.lines[-2] += f' to 1005 {y} fleet 0 {q0} warp 4'
    r.expect('fleet', (0, q0), dict(x=1017, y=y))
    r.expect('fleet', (1, q1), dict(x=1017, y=y))
    out.append(r)

    # ================================================================ FM-103: a friend's starbases
    r = FmRun('fm103', 'refuelling at a friend\'s starbases (player 1 friend toward player 0; player 0 enemy toward 1)',
              rel01=2, rel10=1)
    r.case('A', 'decomp _FuelFleets', 'QJ5 scout (50 mg) orbiting player 1\'s planet 5 with a Space Dock: refuelled to 300')
    r.lines.append('planet 5 owner 1 pop 87 starbase 1')
    a = r.fleet({0: 1}, CB_XY[5], 50, planet=5, model=False)
    r.expect('fleet', (0, a), dict(fuel=300))
    r.case('B', 'decomp _FuelFleets', 'QJ5 scout (50 mg) orbiting player 1\'s homeworld 8 (Space Station): refuelled to 300')
    b = r.fleet({0: 1}, CB_XY[8], 50, planet=8, model=False)
    r.expect('fleet', (0, b), dict(fuel=300))
    r.case('C', 'decomp _FuelFleets', 'QJ5 scout (50 mg) orbiting player 1\'s planet 3 with an Orbital Fort: not refuelled')
    r.lines.append('planet 3 owner 1 pop 87 starbase 2')
    c = r.fleet({0: 1}, CB_XY[3], 50, planet=3, model=False)
    r.expect('fleet', (0, c), dict(fuel=50))
    r.case('D', 'decomp _FuelFleets (direction)', 'player 1 LH6 scout (50 mg) orbiting player 0\'s homeworld 17 '
           '(Space Station); player 0 is an enemy toward player 1: not refuelled')
    d1 = r._fleet(1)
    x, y = CB_XY[17]
    r.lines.append(f'fleet 1 {d1} planet 17 at {x} {y} ships {P1_SCOUT}:1 plan 0 fuel 50 cargo 0 0 0 0')
    r.expect('fleet', (1, d1), dict(fuel=50))
    out.append(r)

    # ================================================================ FM-104: waypoint chains, two years
    r = FmRun('fm104', 'waypoint chains across two years', years=2)
    keys = {}
    r.case('A', 'KERNEL arrival 5 / chains', 'QJ5 scout: waypoint 20 ly away (warp 5), then 60 ly further (warp 6): '
           'year 1 stops at the first (no carry-over), year 2 moves 36 toward the second')
    y = r.lane(); keys['A'] = r.fleet({0: 1}, (1005, y), 300, wps=[(1025, y, 5), (1085, y, 6)])
    r.case('B', 'KERNEL arrival 5', 'QJ5 scout: first waypoint at its own position (warp 5), then 25 ly: year 1 no move, '
           'year 2 arrives')
    y = r.lane(); keys['B'] = r.fleet({0: 1}, (1005, y), 300, wps=[(1005, y, 5), (1030, y, 5)])
    r.case('C', 'KERNEL chains', 'QJ5 scout: three waypoints 10 ly apart (warp 5): one per year')
    y = r.lane(); keys['C'] = r.fleet({0: 1}, (1005, y), 300, wps=[(1015, y, 5), (1025, y, 5), (1035, y, 5)])
    r.case('D', 'KERNEL running dry, next year', 'QJ5 scout, warp 6, +100 x, 2 mg: year 1 runs dry (warp 1); '
           'year 2 moves 1 ly at warp 1 and its ram scoop gives 1 mg')
    y = r.lane(); keys['D'] = r.fleet({0: 1}, (1005, y), 2, wps=[(1105, y, 6)])
    r.case('E', 'KERNEL per-year rounding', 'QJ5 scout, warp 5, +100 x: 25 ly a year, rounded up each year')
    y = r.lane(); keys['E'] = r.fleet({0: 1}, (1005, y), 300, wps=[(1105, y, 5)])
    r.case('F', 'KERNEL chains (fuel-limited leg then next)', 'QJ5 scout, 4 mg: waypoint 10 ly away at warp 9, then '
           '50 ly further at warp 6')
    y = r.lane(); keys['F'] = r.fleet({0: 1}, (1005, y), 4, wps=[(1015, y, 9), (1065, y, 6)])
    pred = r.predict(2)
    for cid in 'ABCDEF':
        for yr in (1, 2):
            p = pred[(0, keys[cid])][yr - 1]
            r.cur = cid
            r.expect('fleet', (0, keys[cid]), dict(x=p['x'], y=p['y'], fuel=p['fuel']), year=yr)
    out.append(r)
    return out


def fmt(kind, args, v, year):
    yr = '' if year == 1 else f' (year {year})'
    if kind == 'fleet':
        return f'fleet {args[0]}/{args[1]}: ' + ', '.join(f'{k} {x}' for k, x in v.items()) + yr
    if kind == 'ce':
        return (f'{len(args)} fleets: between {v["lo"]} and {v["hi"]} stay at {v["start"]} with 300 mg; '
                f'the rest at {v["dest"]}')
    if kind == 'warp10':
        return f'fleet {args[1]}: {v["n0"]} - k ships with {v["lo"]} <= k <= {v["hi"]}, at ({v["x"]}, {v["y"]})'
    if kind == 'warp10mix':
        return f'fleet {args[1]}: design 2 keeps 50; design 1 loses {v["lo"]}-{v["hi"]}'
    return f'{kind} {args} {v}{yr}'


def table():
    for r in runs():
        print(f'### {r.name.upper()}: {r.title}')
        print()
        print(f'{r.years} year(s).')
        print()
        print('| Case | Source | Setup | Predicted |')
        print('|---|---|---|---|')
        for cid, rule, text in r.cases:
            pred = '; '.join(fmt(k, a, v, y) for c, k, a, v, y in r.checks if c == cid)
            print(f'| {cid} | {rule} | {text} | {pred} |')
        print()


if __name__ == '__main__':
    if sys.argv[1:] == ['--table']:
        table()
    else:
        o = sys.argv[1] if len(sys.argv) > 1 else HERE
        for r in runs():
            r.write(o)
            print(r.name, len(r.cases), 'cases', len(r.checks), 'checks')
