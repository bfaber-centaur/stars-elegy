#!/usr/bin/env python3
"""Write the FO (fleet operations) Combat Lab specs, with predictions.

FO tests the "Fleet operations" rules of docs/ORDERS.md (stars-elegy #40,
all BINARY-ONLY) that can be set up with waypoint tasks written into the
host file, with no order (.X) file:

- transport amounts and clamps: loads capped by the free cargo hold or the
  free fuel tank (independently), unloads capped by the cargo held and by
  the receiving fleet's free space; the transport actions (load all, load
  exactly, fill to %, wait for %, load optimal, set amount, set waypoint);
- transport between two of a player's own fleets, and cargo given to
  another player's fleet (relation check, colonists refused);
- the Merge with Fleet waypoint task (ship counts per design, the 32766
  cap, pooled cargo and fuel, damage, owner check, no distance check);
- the Transfer Fleet waypoint task (recipient's relation toward the giver,
  colonists refused, design slot);
- where these fall in the turn: before movement (load, merge), after
  movement (arrival unload, load and merge).

Split, the direct "transfer to fleet" order and direct merges need crafted
order files and wait on the serial decision (README).

Predictions come from ORDERS.md "Fleet operations" (#40) where it speaks,
and otherwise from the stars-decomp reading of the waypoint tasks
(orders-misc §3, fleet-gates-merge §3-4, fleet-fuel; OR-14..19 in
stars-decomp #12); each case names its source. They are written here
before the runs; check.py compares them with the run dumps.

Each run is one pinned generation (tools/fleetlab/pinned-turn, cycles
20000) of a start built by `tools/fleetlab/combatlab build` from Combat
Lab (CB, two JOAT players). Player 0 tech 26, research 0%. Freighter =
Medium Freighter + Long Hump 6 (cargo 210 kT, fuel 450 mg); Colonizer =
Colony Ship + Long Hump 6 + Colonization Module (cargo 25, fuel 200).
Player 1's freighter is its CB design 3 (Medium Freighter, Long Hump 6,
Rhino Scanner, Crobmnium: cargo 210, fuel 450). Cargo is in kT; colonists
in kT (100 colonists); populations in 100s.

  python3 experiments/fo/gen.py OUTDIR      # write foNN.spec files
  python3 experiments/fo/gen.py --table     # print the prediction table
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'tk'))
from gen2 import Run, cb_run, CB_XY, grow, D_FREIGHTER, D_COLONIZER  # noqa: E402

F, C = D_FREIGHTER, D_COLONIZER
P1F = 3          # player 1's Medium Freighter design in CB
HOLD, TANK = 210, 450
WARP6 = 36       # ly in one year at warp 6

# Deep-space spots more than 30 ly from every planet, 45 ly apart.
SPOTS = [(x, y) for x in (1010, 1385, 1205) for y in range(1010, 1386, 45)
         if x != 1205 or y <= 1235]


def far(p):
    return min(math.dist(p, q) for q in CB_XY.values())


def beside(p):
    """A deep-space point 30 ly from spot p, away from planets and the other spots."""
    for d in ((30, 0), (-30, 0), (0, 30), (0, -30)):
        q = (p[0] + d[0], p[1] + d[1])
        if 1000 < q[0] < 1400 and 1000 < q[1] < 1400 and far(q) > 30 \
                and all(math.dist(q, s) > 10 for s in SPOTS if s != p):
            return q
    raise ValueError(p)


class FoRun(Run):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.spots = list(SPOTS)

    def text(self):
        return super().text().replace('experiments/tk/gen2.py', 'experiments/fo/gen.py')

    def spot(self):
        p = self.spots.pop(0)
        assert far(p) > 30, p
        return p

    def fleet(self, owner, at, ships, cargo=(0, 0, 0, 0), fuel=200, extra='', planet=None, dmg=None):
        """A fleet at `at`; returns its id. `extra` is appended verbatim (target, task, to ...)."""
        i = self._fleet(owner)
        s = f'fleet {owner} {i} '
        if planet is not None:
            s += f'planet {planet} '
        s += f'at {at[0]} {at[1]} ships {ships} plan 0 fuel {fuel} cargo ' + ' '.join(map(str, cargo))
        if dmg:
            s += f' dmg {dmg}'
        if extra:
            s += ' ' + extra
        self.lines.append(s)
        return i

    def fleet_at(self, n, ships, **kw):
        return self.fleet(0, CB_XY[n], ships, planet=n, **kw)

    def own(self, n, pop=87, surface=(0, 0, 0)):
        fe, bo, ge = surface
        self.target(n, pop, owner=0, fe=fe, bo=bo, ge=ge, mines=0, factories=0)


def fo_run(name, title, rel01=2, rel10=2):
    r = cb_run(name, title)
    r.__class__ = FoRun
    r.spots = list(SPOTS)
    # cb_run writes a symmetric relation; override per direction
    r.hdr = [h for h in r.hdr if not h.startswith('relation')]
    r.h(f'relation 0 1 {rel01}\nrelation 1 0 {rel10}')
    return r


def T(*w):
    """transport task: five entries (Ir, Bo, Ge, colonists, fuel), each 'A:V' or '-'."""
    return 'task transport ' + ','.join(w)


def runs():
    out = []

    # ---------------------------------------------------------------- FO-01: planet loads
    r = fo_run('fo01', 'transport loads from an own planet: clamps, kinds in order, actions 3/5/6/8/9, fuel')
    r.case('A', 'ORDERS clamp', 'own planet 0 surface 500/500/500; empty Freighter in orbit loads all Ir: capped by the free hold')
    r.own(0, surface=(500, 500, 500)); f = r.fleet_at(0, f'{F}:1', extra=T('1:0', '-', '-', '-', '-'))
    r.expect('fleet', (0, f), dict(fe=210, bo=0, ge=0))
    r.expect('planet', (0,), dict(surface=[290, 500, 500]))
    r.case('B', 'decomp §3.1 order', 'planet 1 surface 150/150/0; load all Ir and all Bo: Ir first (150), Bo gets the rest (60)')
    r.own(1, surface=(150, 150, 0)); f = r.fleet_at(1, f'{F}:1', extra=T('1:0', '1:0', '-', '-', '-'))
    r.expect('fleet', (0, f), dict(fe=150, bo=60))
    r.expect('planet', (1,), dict(surface=[0, 90, 0]))
    r.case('C', 'ORDERS clamp', 'planet 2 surface 0/0/500; Freighter holding 50 Ir loads exactly 300 Ge: gets 160')
    r.own(2, surface=(0, 0, 500)); f = r.fleet_at(2, f'{F}:1', cargo=(50, 0, 0, 0), extra=T('-', '-', '3:300', '-', '-'))
    r.expect('fleet', (0, f), dict(fe=50, ge=160))
    r.expect('planet', (2,), dict(surface=[0, 0, 340]))
    r.case('D', 'ORDERS colonists', 'planet 3 P=87; Freighter loads exactly 30 colonists before growth: fleet 30, planet grows from 57')
    r.own(3); f = r.fleet_at(3, f'{F}:1', extra=T('-', '-', '-', '3:30', '-'))
    r.expect('fleet', (0, f), dict(col=30))
    r.expect('planet', (3,), dict(pop=grow(57)))
    r.case('E', 'decomp §3.1 fuel', 'planet 4 (no starbase) surface 100/0/0; Freighter fuel 200 loads all fuel and all Ir: '
           'no fuel from a planet, Ir 100')
    r.own(4, surface=(100, 0, 0)); f = r.fleet_at(4, f'{F}:1', extra=T('1:0', '-', '-', '-', '1:0'))
    r.expect('fleet', (0, f), dict(fe=100, fuel=200))
    r.case('F', 'decomp §3.1 a=5', 'planet 5 surface 500/0/0; fill to 50% Ir: 105 (half of 210)')
    r.own(5, surface=(500, 0, 0)); f = r.fleet_at(5, f'{F}:1', extra=T('5:50', '-', '-', '-', '-'))
    r.expect('fleet', (0, f), dict(fe=105))
    r.case('G', 'decomp §3.1 a=8', 'planet 6 surface 500/0/0; set amount Ir to 80: loads 80')
    r.own(6, surface=(500, 0, 0)); f = r.fleet_at(6, f'{F}:1', extra=T('8:80', '-', '-', '-', '-'))
    r.expect('fleet', (0, f), dict(fe=80))
    r.case('H', 'decomp §3.1 a=9', 'planet 7 surface 300/0/0; set waypoint Ir to 100: loads 200, planet keeps 100')
    r.own(7, surface=(300, 0, 0)); f = r.fleet_at(7, f'{F}:1', extra=T('9:100', '-', '-', '-', '-'))
    r.expect('fleet', (0, f), dict(fe=200))
    r.expect('planet', (7,), dict(surface=[100, 0, 0]))
    r.case('I', 'decomp §3.1 a=6', 'planet 9 surface 100/0/0, wait for 100% Ir, second waypoint planet 14: '
           'loads 100 and stays at planet 9')
    r.own(9, surface=(100, 0, 0))
    x, y = CB_XY[14]
    f = r.fleet_at(9, f'{F}:1', extra=T('6:100', '-', '-', '-', '-') + f' to {x} {y} planet 14 warp 6')
    r.expect('fleet', (0, f), dict(fe=100, x=CB_XY[9][0], y=CB_XY[9][1]))
    r.case('J', 'decomp §3.1 a=5 / turn placement', 'control for I: planet 11 surface 100/0/0, fill to 100% Ir, second '
           'waypoint planet 12 (35 ly): loads 100 before movement and arrives at planet 12 with it')
    r.own(11, surface=(100, 0, 0))
    x, y = CB_XY[12]
    f = r.fleet_at(11, f'{F}:1', extra=T('5:100', '-', '-', '-', '-') + f' to {x} {y} planet 12 warp 6')
    r.expect('fleet', (0, f), dict(fe=100, x=x, y=y))
    r.case('K', 'turn placement', 'Freighter 20 ly from own planet 13 (surface 300/0/0) arrives with load all Ir: '
           'loads after movement, 210')
    r.own(13, surface=(300, 0, 0))
    x, y = CB_XY[13]
    f = r.fleet(0, (x, y - 20), f'{F}:1', extra=f'to {x} {y} planet 13 warp 6 ' + T('1:0', '-', '-', '-', '-'))
    r.expect('fleet', (0, f), dict(fe=210, x=x, y=y))
    r.expect('planet', (13,), dict(surface=[90, 0, 0]))
    out.append(r)

    # ---------------------------------------------------------------- FO-02: own fleet to own fleet
    r = fo_run('fo02', 'transport between two of player 0\'s fleets (waypoint 0 targets the other fleet)')

    def pair(cid, rule, text, xc, yc, xtask, xfuel=200, yfuel=200, yextra=''):
        r.case(cid, rule, text)
        p = r.spot()
        y = r.fleet(0, p, f'{F}:1', cargo=yc, fuel=yfuel, extra=yextra)
        x = r.fleet(0, p, f'{F}:1', cargo=xc, fuel=xfuel, extra=f'target fleet 0 {y} ' + xtask)
        return x, y, p

    x, y, _ = pair('L', 'ORDERS clamp', 'X (0/0/100 Ge, free 110) loads all Ir and all Bo from Y (150/60): X gets 110 Ir, 0 Bo',
                   (0, 0, 100, 0), (150, 60, 0, 0), T('1:0', '1:0', '-', '-', '-'))
    r.expect('fleet', (0, x), dict(fe=110, bo=0, ge=100))
    r.expect('fleet', (0, y), dict(fe=40, bo=60))
    x, y, _ = pair('M', 'ORDERS clamp (hold and tank separate)', 'X full hold (210 Ir), fuel 200, loads all Ir and all fuel '
                   'from Y (50 Ir, fuel 450): no Ir, fuel capped by the free tank (250)',
                   (210, 0, 0, 0), (50, 0, 0, 0), T('1:0', '-', '-', '-', '1:0'), xfuel=200, yfuel=450)
    r.expect('fleet', (0, x), dict(fe=210, fuel=450))
    r.expect('fleet', (0, y), dict(fe=50, fuel=200))
    x, y, _ = pair('N', 'ORDERS clamp (shortfall stays)', 'X (200 Ir) unloads all Ir to Y (100 Ir, free 110): Y 210, X keeps 90',
                   (200, 0, 0, 0), (100, 0, 0, 0), T('2:0', '-', '-', '-', '-'))
    r.expect('fleet', (0, x), dict(fe=90))
    r.expect('fleet', (0, y), dict(fe=210))
    x, y, _ = pair('O', 'ORDERS clamp (fuel)', 'X fuel 400 unloads exactly 300 fuel to Y (fuel 300, free 150): Y 450, X 250',
                   (0, 0, 0, 0), (0, 0, 0, 0), T('-', '-', '-', '-', '4:300'), xfuel=400, yfuel=300)
    r.expect('fleet', (0, x), dict(fuel=250))
    r.expect('fleet', (0, y), dict(fuel=450))
    x, y, _ = pair('P', 'decomp §3.1 (own fleet)', 'X (50 colonists) unloads all colonists to Y: Y 50, X 0',
                   (0, 0, 0, 50), (0, 0, 0, 0), T('-', '-', '-', '2:0', '-'))
    r.expect('fleet', (0, x), dict(col=0))
    r.expect('fleet', (0, y), dict(col=50))
    x, y, _ = pair('Q', 'decomp §3.1 a=7', 'X (fuel 200, one waypoint) "load optimal" fuel: unloads all its fuel to Y (fuel 100): '
                   'Y 300, X 0', (0, 0, 0, 0), (0, 0, 0, 0), T('-', '-', '-', '-', '7:0'), xfuel=200, yfuel=100)
    r.expect('fleet', (0, x), dict(fuel=0))
    r.expect('fleet', (0, y), dict(fuel=300))
    r.case('R', 'turn placement / follow', 'X loads all Ir from Y (100 Ir); Y leaves for a point 30 ly away: X loads before '
           'movement, then follows Y (one fleet-targeted waypoint) to Y\'s destination')
    p = r.spot(); d = beside(p)
    y = r.fleet(0, p, f'{F}:1', cargo=(100, 0, 0, 0), extra=f'to {d[0]} {d[1]} warp 6')
    x = r.fleet(0, p, f'{F}:1', extra=f'target fleet 0 {y} ' + T('1:0', '-', '-', '-', '-'))
    r.expect('fleet', (0, x), dict(fe=100, x=d[0], y=d[1]))
    r.expect('fleet', (0, y), dict(fe=0, x=d[0], y=d[1]))
    for cid, task, xc, yc, want_x, want_y, text in (
            ('S', T('2:0', '-', '-', '-', '-'), (100, 0, 0, 0), (0, 0, 0, 0), 0, 100, 'unloads all Ir (100) to Y'),
            ('U', T('1:0', '-', '-', '-', '-'), (0, 0, 0, 0), (100, 0, 0, 0), 100, 0, 'loads all Ir (100) from Y')):
        r.case(cid, 'turn placement', f'X arrives (30 ly) at stationary Y, its second waypoint targeting Y, and {text} after movement')
        p = r.spot(); s = beside(p)
        y = r.fleet(0, p, f'{F}:1', cargo=yc)
        x = r.fleet(0, s, f'{F}:1', cargo=xc, extra=f'to {p[0]} {p[1]} fleet 0 {y} warp 6 ' + task)
        r.expect('fleet', (0, x), dict(fe=want_x, x=p[0], y=p[1]))
        r.expect('fleet', (0, y), dict(fe=want_y))
    out.append(r)

    # ---------------------------------------------------------------- FO-03: merge
    r = fo_run('fo03', 'Merge with Fleet waypoint task (deep space, stationary unless stated)')

    def merge(cid, rule, text, xs, ys, xc=(0, 0, 0, 0), yc=(0, 0, 0, 0), xf=200, yf=200, xd=None, yd=None,
              xat=None, yextra=''):
        r.case(cid, rule, text)
        p = r.spot()
        y = r.fleet(0, p, ys, cargo=yc, fuel=yf, dmg=yd, extra=yextra)
        x = r.fleet(0, xat or p, xs, cargo=xc, fuel=xf, dmg=xd, extra=f'target fleet 0 {y} task merge')
        return x, y, p

    x, y, _ = merge('A', 'ORDERS merge', 'X (2 Freighters, 100 Ir, fuel 300) merges into Y (3 Freighters, 50 Bo, fuel 400): '
                    'Y keeps its id, 5 ships, 100/50, fuel 700; X removed',
                    f'{F}:2', f'{F}:3', xc=(100, 0, 0, 0), yc=(0, 50, 0, 0), xf=300, yf=400)
    r.expect('fleet', (0, y), dict(ships=f'{F}:5', fe=100, bo=50, fuel=700))
    r.expect('nofleet', (0, x), None)
    x, y, _ = merge('B', 'ORDERS merge (per design)', 'X (1 Colonizer, 20 colonists, fuel 150) merges into Y (1 Freighter, fuel 100): '
                    'Y has both designs, 20 colonists, fuel 250', f'{C}:1', f'{F}:1', xc=(0, 0, 0, 20), xf=150, yf=100)
    r.expect('fleet', (0, y), dict(ships=f'{F}:1,{C}:1', col=20, fuel=250))
    r.expect('nofleet', (0, x), None)
    # damage: per slot D = max(1, pct*n/100) damaged ships per damaged stack, sum = D*units;
    # merged pct = ceil(100*sumD/n), units = sum/sumD (fleet-gates-merge §4.3); then the
    # year's repair, 10 units for a fleet stationary in deep space (orders-misc §6)
    x, y, _ = merge('C', 'ORDERS merge (damage)', 'X 10 Freighters 100 units on 50%, Y 10 Freighters 200 units on 20%: '
                    'D = 5 + 2, units (500+400)/7 = 128 on ceil(700/20) = 35%, then repair 10 -> 118/35',
                    f'{F}:10', f'{F}:10', xd=f'{F}:100:50', yd=f'{F}:200:20')
    r.expect('fleet', (0, y), dict(ships=f'{F}:20', dmg={F: (118, 35)}))
    x, y, _ = merge('D', 'ORDERS merge (damage)', 'X 10 Freighters 100 units on 50% into undamaged Y 10 Freighters: 100 units '
                    'on 25%, then repair -> 90/25 (if an undamaged stack counts as one damaged ship: 83 on 30% -> 73/30)',
                    f'{F}:10', f'{F}:10', xd=f'{F}:100:50')
    r.expect('fleet', (0, y), dict(ships=f'{F}:20', dmg={F: (90, 25)}))
    x, y, _ = merge('E', 'ORDERS merge (cap)', 'X 1000 Freighters into Y 32000 Freighters: 32766 (per-design cap)',
                    f'{F}:1000', f'{F}:32000')
    r.expect('fleet', (0, y), dict(ships=f'{F}:32766'))
    r.expect('nofleet', (0, x), None)
    q = r.spots[-1]; r.spots = r.spots[:-1]
    x, y, p = merge('F', 'decomp §3.5 (no distance check)', f'X (1 Freighter, 30 Ir) at {q} targets Y (1 Freighter) '
                    'at least 100 ly away with merge: merged anyway (the task has no position test)',
                    f'{F}:1', f'{F}:1', xc=(30, 0, 0, 0), xat=q)
    assert math.dist(p, q) >= 100, (p, q)
    r.expect('fleet', (0, y), dict(ships=f'{F}:2', fe=30, x=p[0], y=p[1]))
    r.expect('nofleet', (0, x), None)
    r.case('G', 'turn placement', 'X merges into Y before movement; Y then leaves for a point 30 ly away: Y arrives with 2 ships')
    p = r.spot(); d = beside(p)
    y = r.fleet(0, p, f'{F}:1', extra=f'to {d[0]} {d[1]} warp 6')
    x = r.fleet(0, p, f'{F}:1', cargo=(40, 0, 0, 0), extra=f'target fleet 0 {y} task merge')
    r.expect('fleet', (0, y), dict(ships=f'{F}:2', fe=40, x=d[0], y=d[1]))
    r.expect('nofleet', (0, x), None)
    r.case('H', 'turn placement', 'X arrives (30 ly) at stationary Y, its second waypoint targeting Y with merge: merged after movement')
    p = r.spot(); s = beside(p)
    y = r.fleet(0, p, f'{F}:1')
    x = r.fleet(0, s, f'{F}:1', cargo=(40, 0, 0, 0), extra=f'to {p[0]} {p[1]} fleet 0 {y} warp 6 task merge')
    r.expect('fleet', (0, y), dict(ships=f'{F}:2', fe=40, x=p[0], y=p[1]))
    r.expect('nofleet', (0, x), None)
    out.append(r)

    # ---------------------------------------------------------------- FO-04/05: other players
    for name, rel01, rel10 in (('fo04', 2, 0), ('fo05', 0, 2)):
        ok = rel10 != 2
        r = fo_run(name, f'cargo, merge and fleet transfer toward player 1; player 1 is '
                   f'{"neutral" if ok else "an enemy"} toward player 0, player 0 '
                   f'{"an enemy" if rel01 == 2 else "neutral"} toward player 1', rel01=rel01, rel10=rel10)
        p = r.spot()
        r.case('A', 'decomp §3.1 relation', f'X (50 Ir) unloads all Ir to player 1\'s freighter Z: '
               + ('Z gets 50' if ok else 'nothing moves (relation 2 toward the giver)'))
        z = r.fleet(1, p, f'{P1F}:1')
        x = r.fleet(0, p, f'{F}:1', cargo=(50, 0, 0, 0), extra=f'target fleet 1 {z} ' + T('2:0', '-', '-', '-', '-'))
        r.expect('fleet', (0, x), dict(fe=0 if ok else 50))
        r.expect('fleet', (1, z), dict(fe=50 if ok else 0))
        p = r.spot()
        r.case('B', 'decomp §3.1 (0x155)', 'X (30 colonists) unloads all colonists to player 1\'s freighter Z: refused, X keeps 30')
        z = r.fleet(1, p, f'{P1F}:1')
        x = r.fleet(0, p, f'{F}:1', cargo=(0, 0, 0, 30), extra=f'target fleet 1 {z} ' + T('-', '-', '-', '2:0', '-'))
        r.expect('fleet', (0, x), dict(col=30))
        r.expect('fleet', (1, z), dict(col=0))
        p = r.spot()
        r.case('C', 'decomp §3.1 (no steal)', 'X (no scanner) loads all Ir from player 1\'s freighter Z (100 Ir): nothing moves')
        z = r.fleet(1, p, f'{P1F}:1', cargo=(100, 0, 0, 0))
        x = r.fleet(0, p, f'{F}:1', extra=f'target fleet 1 {z} ' + T('1:0', '-', '-', '-', '-'))
        r.expect('fleet', (0, x), dict(fe=0))
        r.expect('fleet', (1, z), dict(fe=100))
        p = r.spot()
        r.case('D', 'ORDERS merge (owner)', 'X merges into player 1\'s freighter Z: refused, both unchanged')
        z = r.fleet(1, p, f'{P1F}:1')
        x = r.fleet(0, p, f'{F}:2', cargo=(20, 0, 0, 0), extra=f'target fleet 1 {z} task merge')
        r.expect('fleet', (0, x), dict(ships=f'{F}:2', fe=20))
        r.expect('fleet', (1, z), dict(ships=f'{P1F}:1'))
        p = r.spot()
        r.case('E', 'decomp §3.3', 'X (2 Freighters, 100 Ir, fuel 300) transfers to player 1: '
               + ('X removed; player 1 gets a fleet there with 2 ships of a copied Freighter design, 100 Ir, fuel 300'
                  if ok else 'refused, X unchanged'))
        x = r.fleet(0, p, f'{F}:2', cargo=(100, 0, 0, 0), fuel=300, extra='task transfer 0')
        if ok:
            r.expect('nofleet', (0, x), None)
            r.expect('fleetat', (1, p[0], p[1]), dict(n=2, fe=100, fuel=300, hull='Medium Freighter'))
        else:
            r.expect('fleet', (0, x), dict(ships=f'{F}:2', fe=100))
            r.expect('nofleetat', (1, p[0], p[1]), None)
        p = r.spot()
        r.case('F', 'decomp §3.3', 'X (1 Freighter, 10 colonists) transfers to player 1: refused (carries colonists)')
        x = r.fleet(0, p, f'{F}:1', cargo=(0, 0, 0, 10), extra='task transfer 0')
        r.expect('fleet', (0, x), dict(ships=f'{F}:1', col=10))
        r.expect('nofleetat', (1, p[0], p[1]), None)
        out.append(r)

    # ---------------------------------------------------------------- FO-06 (follow-up, after FO-01..05)
    # FO-03 C gave 35/35% where 118/35% was predicted, D held (90/25%), and E (32000 + 1000)
    # left a fleet with no ships. Candidate read off those results, predicted here before
    # FO-06 runs: when both stacks are damaged, units = sum(D*units) / (all ships of the
    # slot) with D = max(1, pct*n/100); when only one is, its units are kept; either way
    # pct = ceil(100*sumD/n). Ship counts add with no clamp, and a sum above 32767 (a
    # negative 16-bit count) empties the slot. Repair 10 after the merge as before.
    r = fo_run('fo06', 'follow-up: merge damage when both or one stack is damaged; ship counts near 32767')

    def dmg_case(cid, text, xn, xd, yn, yd, units, pct):
        r.case(cid, 'FO-03 follow-up', text)
        p = r.spot()
        y = r.fleet(0, p, f'{F}:{yn}', dmg=yd and f'{F}:{yd[0]}:{yd[1]}')
        r.fleet(0, p, f'{F}:{xn}', dmg=xd and f'{F}:{xd[0]}:{xd[1]}', extra=f'target fleet 0 {y} task merge')
        r.expect('fleet', (0, y), dict(ships=f'{F}:{xn + yn}', dmg={F: (units - 10, pct)}))

    dmg_case('A', 'X 10 at 100 units on 50% into Y 30 at 200 on 20%: D 5 + 6, units 1700/40 = 42 on 28%, repair -> 32/28 '
             '(sum/sumD would give 154 -> 144)', 10, (100, 50), 30, (200, 20), 42, 28)
    dmg_case('B', 'X 4 at 300 units on 100% into Y 6 at 100 on 50%: D 4 + 3, units 1500/10 = 150 on 70%, repair -> 140/70',
             4, (300, 100), 6, (100, 50), 150, 70)
    dmg_case('C', 'undamaged X 10 into Y 10 at 100 units on 50% (FO-03 D reversed): units kept, 25%, repair -> 90/25',
             10, None, 10, (100, 50), 100, 25)
    dmg_case('D', 'X 6 at 100 units on 50% into undamaged Y 14: units kept, ceil(300/20) = 15%, repair -> 90/15',
             6, (100, 50), 14, None, 100, 15)
    for cid, add, want in (('E', 766, f'{F}:32766'), ('F', 767, f'{F}:32767'), ('G', 768, '')):
        r.case(cid, 'FO-03 follow-up', f'X {add} Freighters into Y 32000: '
               + (f'{32000 + add} ships' if want else 'over 32767: the slot empties'))
        p = r.spot()
        y = r.fleet(0, p, f'{F}:32000')
        r.fleet(0, p, f'{F}:{add}', extra=f'target fleet 0 {y} task merge')
        r.expect('fleet', (0, y), dict(ships=want))
    out.append(r)

    # FO-07 (after FO-06): FO-06 A gave 33 where 32 was predicted, i.e. 1700/40 = 42.5 went
    # to 43. Rounded up (stars-decomp: "count-weighted, rounded up") or to nearest?
    r = fo_run('fo07', 'follow-up: rounding of merged damage units')
    r.case('A', 'FO-06 follow-up', 'X 2 at 101 units on 50% into Y 2 at 100 on 50%: units 201/4 = 50.25, rounded up 51 '
           '(nearest: 50), 50%; repair -> 41/50')
    p = r.spot()
    y = r.fleet(0, p, f'{F}:2', dmg=f'{F}:100:50')
    r.fleet(0, p, f'{F}:2', dmg=f'{F}:101:50', extra=f'target fleet 0 {y} task merge')
    r.expect('fleet', (0, y), dict(ships=f'{F}:4', dmg={F: (41, 50)}))
    out.append(r)
    return out


def fmt(kind, args, v):
    if kind == 'planet':
        return f'planet {args[0]}: ' + ', '.join(
            f'{k} {"/".join(map(str, x)) if isinstance(x, (list, tuple)) else x}' for k, x in v.items())
    if kind == 'fleet':
        parts = []
        for k, x in v.items():
            if k == 'dmg':
                parts += [f'dmg {d}: {u}/{p}%' for d, (u, p) in x.items()]
            else:
                parts.append(f'{k} {x}')
        return f'fleet {args[0]}/{args[1]}: ' + ', '.join(parts)
    if kind == 'nofleet':
        return f'fleet {args[0]}/{args[1]} gone'
    if kind == 'fleetat':
        return f'player {args[0]} fleet at {args[1]},{args[2]}: ' + ', '.join(f'{k} {x}' for k, x in v.items())
    if kind == 'nofleetat':
        return f'no player {args[0]} fleet at {args[1]},{args[2]}'
    return f'{kind} {args} {v}'


def table():
    for r in runs():
        print(f'### {r.name.upper()}: {r.title}')
        print()
        print('| Case | Source | Setup | Predicted |')
        print('|---|---|---|---|')
        for cid, rule, text in r.cases:
            pred = '; '.join(fmt(k, a, v) for c, k, a, v, y in r.checks if c == cid)
            print(f'| {cid} | {rule} | {text} | {pred} |')
        print()


if __name__ == '__main__':
    if sys.argv[1:] == ['--table']:
        table()
    else:
        out = sys.argv[1] if len(sys.argv) > 1 else HERE
        for r in runs():
            r.write(out)
            print(r.name, len(r.cases), 'cases', len(r.checks), 'checks')
