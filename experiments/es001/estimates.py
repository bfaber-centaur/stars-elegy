#!/usr/bin/env python3
"""Reference model of the client estimates in docs/ESTIMATES.md.

The functions here compute what the original client displays for one
player, from that player's view of the game: travel time, fuel use and
range of fleets, production completion years, research estimates,
population growth, planet value and mining rate. They use the turn rules
in docs/KERNEL.md (habitability, growth, resources, mining, production,
fuel) and the component table in data/components.json.

The ES-001 corpus drives it from a `combatlab dump` of the player's file
(`parse_dump`). Elegy can use the outputs as test vectors.
"""
import json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TABLE = json.load(open(os.path.join(HERE, '..', '..', 'data', 'components.json')))
BYNAME = {r['name']: r for r in TABLE['items']}
ENGINES = {r['name']: r for r in TABLE['items'] if r['category'] == 'engine'}
ENGINE_INDEX = {r['name']: r['index'] for r in ENGINES.values()}
WARP10_NO_CAP = {'Interspace-10', 'Enigma Pulsar', 'Trans-Star 10',
                 'Trans-Galactic Mizer Scoop', 'Galaxy Scoop'}
NO_SCOOP_ADJUST = {'Trans-Galactic Mizer Scoop', 'Galaxy Scoop'}
FUEL_TRANSPORTS = {'Fuel Transport', 'Super-Fuel Xport'}

BASE_COST = [0, 50, 80, 130, 210, 340, 550, 890, 1440, 2330, 3770, 6100, 9870, 13850,
             18040, 22440, 27050, 31870, 36900, 42140, 47590, 53250, 59120, 65200,
             71490, 77990, 84700]


# ---------------------------------------------------------------- dumps

def kv(s):
    return dict(re.findall(r'(\w+)=(\S+)', s))


def parse_dump(path, owner=0):
    """Read a `combatlab dump` of an .HST or .M file: the given player's
    race, designs, fleets (with waypoints), planets and queues."""
    st = dict(player=None, designs={}, fleets=[], planets={}, queues={}, xy={}, owner=str(owner))
    fleet = None
    nship = 0
    for line in open(path, encoding='latin-1'):
        _, _, body = line.partition(' ')
        body = body.rstrip('\n')
        if body.startswith('player %d ' % owner):
            st['player'] = kv(body)
        elif body.startswith('design owner=%d ' % owner):
            d = kv(body.split('::')[0])
            parts = [p.strip() for p in body.split('::')[1].split(',')]
            st['designs'][int(d['n'])] = dict(mass=int(d['mass']), hull=parts[0], slots=parts[1:])
        elif body.startswith('fleet '):
            f = kv(body)
            fleet = None
            if int(f['owner']) == owner:
                ships = {int(a): int(b) for a, b in (s.split(':') for s in f['ships'].split(','))}
                fleet = dict(id=int(f['id']), x=int(f['x']), y=int(f['y']), ships=ships,
                             cargo=[int(c) for c in f['cargo'].split('/')], fuel=int(f['fuel']), wps=[])
                st['fleets'].append(fleet)
        elif body.startswith('  wp ') and fleet is not None:
            w = kv(body)
            fleet['wps'].append(dict(x=int(w['x']), y=int(w['y']), obj=int(w['obj']),
                                     type=int(w['type'], 16), warp=int(w['warp']), task=int(w['task'])))
        elif body.startswith('pdetail '):
            n = int(body.split()[1])
            d = kv(body)
            d['homeworld'] = ' homeworld' in body
            st['planets'].setdefault(n, {}).update(d)
        elif body.startswith('planet '):
            n = int(body.split()[1])
            d = kv(body)
            st['planets'].setdefault(n, {}).update(starbase=d['starbase'] == 'true', sbdesign=int(d['design']))
        elif body.startswith('queue planet='):
            q = kv(body)
            items = []
            for it in q.get('items', '').split(','):
                if it:
                    iid, cnt, pct, kind = (int(v) for v in it.split(':'))
                    items.append(dict(id=iid, count=cnt, pct=pct, kind=kind))
            st['queues'][int(q['planet'])] = items
        elif body.startswith('xy planet'):
            p = body.split()
            st['xy'][int(p[2])] = (int(p[3][2:]), int(p[4][2:]))
        elif body.startswith('sbdesign owner=%d ' % owner):
            d = kv(body.split('::')[0])
            st.setdefault('sbdesigns', {})[int(d['n'])] = body.split('::')[1].strip()
    return st


# ---------------------------------------------------------------- race

class Race:
    def __init__(self, p):
        r = [int(v) for v in p['race'].split(',')]
        self.growth, self.pop_eff, self.f_out, self.f_cost, self.f_op, self.m_out, self.m_cost, self.m_op = r
        h = [int(v) for v in p['hab'].split(',')]
        self.centre, self.lo, self.hi = h[0:3], h[3:6], h[6:9]
        self.prt = int(p['prt'])
        self.lrt = int(p['lrt'], 16)
        self.tech = [int(p[k]) for k in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')]
        self.accum = [int(v) for v in p['accum'].split(',')]
        self.research_pct = int(p['researchPct'])
        self.field = int(p['field'])
        self.rcost = [int(v) for v in p['rcost'].split(',')]
        self.res_last = int(p['resLast'])

    def immune(self, axis):
        return self.lo[axis] == 255


def hab(race, env):
    """KERNEL.md "Habitability"."""
    hostile = 0
    for a in range(3):
        if race.immune(a):
            continue
        v, lo, hi = env[a], race.lo[a], race.hi[a]
        if v < lo:
            hostile += min(15, lo - v)
        elif v > hi:
            hostile += min(15, v - hi)
    if hostile:
        return -hostile
    S, M = 0, 10000
    for a in range(3):
        if race.immune(a):
            S += 10000
            continue
        v, c = env[a], race.centre[a]
        d = abs(v - c)
        w = c - race.lo[a] if v < c else race.hi[a] - c
        e = 100 - 100 * d // w
        S += e * e
        if 2 * d - w > 0:
            M = M * (2 * w - (2 * d - w)) // (2 * w)
    x = int(math.sqrt(S / 3) + 0.9)
    return x * M // 10000


def max_pop(race, h):
    """KERNEL.md "Maximum population" (ordinary races, JOAT)."""
    m = 100 * h if h >= 5 else 500
    if race.prt == 9:   # JOAT
        m += m // 5
    return m


def growth(race, P, k, h, mx):
    """KERNEL.md "Population growth": returns (units gained or lost, new carry)."""
    if P == 0:
        return 0, k
    if h < 0:
        t = max(1, -h * P // 10)
        q, r = t // 100, t % 100
        k -= r
        if k < 0:
            k += 100
            q += 1
        return -q, k
    g = race.growth * h
    if P >= mx // 4:
        c = 1000 * P // mx
        if P < mx:
            if g < 1000:
                g = g * (1000 - c) ** 2 // 562500
            else:
                g = 10 * ((g // 10) * (1000 - c) ** 2 // 562500)
        elif P <= mx + 10:
            return 0, k
        else:
            g = 4 * max(-300, int(c / -10) + 99)
    if (g // 100) * P >= 10000000:
        t = (g // 100) * P
    else:
        t = int(g * P / 100)
    q, r = int(t / 100), t - 100 * int(t / 100)
    if q == 0 and r == 0:
        r = 1
    k += r
    if k >= 100:
        q += 1
        k -= 100
    elif k < 0:
        q -= 1
        k += 100
    return q, k


def effective_pop(P, mx):
    return P if P <= mx else min(2 * mx, mx + (P - mx) // 2)


def max_factories(race, mx):
    return max(10, mx * race.f_op // 100)


def max_mines(race, mx):
    return max(10, mx * race.m_op // 100)


def max_defenses(h):
    return min(100, max(10, 4 * h))


def operable_factories(race, P, mx):
    return max(1, min(max_factories(race, mx), P * race.f_op // 100))


def operable_mines(race, P, mx):
    return max(1, min(max_mines(race, mx), P * race.m_op // 100))


def operable_defenses(P, h):
    return min(max_defenses(h), 1000, -(-P // 25))


def resources(race, P, factories, mx):
    """KERNEL.md "Resources per planet" (non-AR)."""
    if P == 0:
        return 0
    E = effective_pop(P, mx)
    n = min(factories, operable_factories(race, P, mx))
    r = E // race.pop_eff + (race.f_out * n + 9) // 10
    return max(1, r)


def mine_estimate(race, pl, apply=False):
    """Minerals mined in a year, without the random +1 (KERNEL.md "Mining");
    with apply, also deplete the concentrations."""
    P, mx = pl['P'], pl['max']
    m = min(pl['mines'], operable_mines(race, P, mx))
    out = []
    for i in range(3):
        conc = pl['conc'][i]
        cu = 30 if (conc < 30 and pl['homeworld']) else conc
        prod = cu * m
        amt = prod * race.m_out // 10
        out.append(amt // 100)
        if apply:
            pl['surface'][i] += amt // 100
            p = prod // 100
            while p > 0 and pl['conc'][i] > 1:
                c = pl['conc'][i]
                cc = 100 if c > 100 else (10 if c < 5 else (25 if c < 25 else c))
                s = pl['frac'][i] or 256
                need = (s * 12500 // 256) // cc
                if need <= p:
                    p -= need
                    pl['conc'][i] -= 1
                    pl['frac'][i] = 0
                    continue
                f = (need - p) * 256 // (12500 // cc)
                f = max(1, f)
                if f >= s:
                    f = s - 1
                pl['frac'][i] = f
                if f == 0:
                    pl['conc'][i] -= 1
                break
    return out


# ---------------------------------------------------------------- production

AUTO_TARGET = {0: 8, 1: 7, 2: 9, 3: 11}


def unit_cost(race, iid):
    if iid in (0, 8):
        return [0, 0, 0, race.m_cost]
    if iid in (1, 7):
        return [0, 0, 4, race.f_cost]
    if iid in (2, 9):
        return [5, 5, 5, 15]
    if iid in (3, 11):
        return [0, 0, 0, 100]
    raise ValueError('item %d not modelled' % iid)


def build_item(race, pl, item, carry, avail, f_alch):
    """One item's turn in the queue walk (KERNEL.md "Production"); returns
    (units built, status). Status: 0 done, 1 auto done and built, 2 auto with
    nothing to do, 3/4 auto mineral-blocked (built / not), 5 built some and
    stopped, 6 progress only, 7 no progress."""
    iid = item['id']
    cost = unit_cost(race, iid)
    pct0 = item['pct']
    spent = [c * pct0 // 100 for c in cost]
    auto = item['kind'] == 1 and iid < 7
    count = item['count']
    if auto:
        g, _ = growth(race, pl['P'], pl['k'], pl['hab'], pl['max'])
        P2 = pl['P'] + g
        if iid == 0:
            cap = operable_mines(race, P2, pl['max']) - pl['mines']
        elif iid == 1:
            cap = operable_factories(race, P2, pl['max']) - pl['factories']
        elif iid == 2:
            cap = operable_defenses(P2, pl['hab']) - pl['defenses']
        elif iid == 3:
            cap = 1000
        else:
            raise ValueError('auto item %d not modelled' % iid)
        count = min(count, max(0, cap))
    built, blocked, pct = 0, False, pct0
    while count > 0:
        need = [cost[i] - spent[i] for i in range(4)]
        if all(need[i] <= avail[i] for i in range(4)):
            for i in range(4):
                avail[i] -= need[i]
            spent = [0] * 4
            pct = 0
            count -= 1
            built += 1
            continue
        pmin, lim = None, None
        for i in range(4):
            if cost[i] <= 0:
                continue
            if avail[i] >= cost[i]:
                p = 100
            else:
                a = avail[i] + spent[i]
                p = max((a + 1) * 100 // cost[i] - 1, a * 100 // cost[i])
            if pmin is None or p < pmin:
                pmin, lim = p, i
        mineral_short = any(need[i] > avail[i] for i in range(3))
        shortfall = cost[lim] - avail[lim] - spent[lim]
        if auto and mineral_short and not f_alch:
            blocked = True
            break
        if not (auto and mineral_short and f_alch):
            for i in range(4):
                d = cost[i] * pmin // 100 - spent[i]
                avail[i] -= d
                spent[i] += d
            pct = pmin
            if not (f_alch and lim < 3):
                break
        rate = 100
        k = min(avail[3] // rate, shortfall)
        for i in range(3):
            avail[i] += k
        avail[3] -= k * rate
        if k == shortfall:
            continue
        if avail[3] > 0 and carry is not None and carry['count'] == 0:
            r = avail[3]
            pa = max((r + 1) * 100 // rate - 1, r * 100 // rate)
            carry.update(id=11, kind=1, count=1, pct=pa)
            avail[3] -= pa * rate // 100
        break
    if iid in (3, 11):
        for i in range(3):
            avail[i] += built
    if not auto:
        item['count'], item['pct'] = count, pct
    elif pct > 0 and carry is not None and carry['count'] == 0:
        carry.update(id=AUTO_TARGET[iid], kind=1, count=1, pct=pct)
    if auto and blocked:
        status = 3 if built else 4
    elif auto and count == 0:
        status = 1 if built else 2
    elif built:
        status = 0 if count == 0 else 5
    else:
        status = 7 if pct == pct0 else 6
    return built, status


def planet_state(race, st, n):
    d = st['planets'][n]
    pl = dict(n=n, P=int(d['pop']), k=int(d['excess']), env=[int(v) for v in d['env'].split('/')],
              conc=[int(v) for v in d['conc'].split('/')], frac=[int(v) for v in d['frac'].split('/')],
              surface=[int(v) for v in d['surface'].split('/')], mines=int(d['mines']),
              factories=int(d['factories']), defenses=int(d['defenses']),
              leftover=d['leftover'] == 'true', homeworld=d['homeworld'])
    pl['hab'] = hab(race, pl['env'])
    pl['max'] = max_pop(race, pl['hab'])
    return pl


def production_estimate(race, pl, queue, target, years=99):
    """Completion estimate for queue item `target` (KERNEL production run on a
    copy of the planet for up to `years` years). Returns (first, last):
    first/last year a unit / the last unit completes, 100 = not within the
    horizon, (0, 0) = skipped, (-1, -1) = as needed. With target -1 or -2
    returns the resources left after the first year's walk (plus the
    research tax for -1)."""
    pl = json.loads(json.dumps(pl))
    q = json.loads(json.dumps(queue))
    carry = dict(id=0, kind=1, count=0, pct=0)
    first = last = 0
    n = len(q)
    for year in range(1, years + 1):
        mine_estimate(race, pl, apply=True)
        avail = pl['surface'][:] + [resources(race, pl['P'], pl['factories'], pl['max'])]
        tax = 0
        if not pl['leftover']:
            tax = avail[3] * race.research_pct // 100
            avail[3] -= tax
        f_alch = False
        i = -1
        while i < n:
            item = carry if i == -1 else q[i]
            if item['count'] == 0:
                i += 1
                continue
            if item['kind'] == 1 and item['id'] == 3:
                if i >= n - 1:
                    item['count'] = (item['count'] & 3) | 0x3fc
                elif i != target:
                    f_alch = True
                    i += 1
                    continue
                else:
                    return -1, -1
            built, status = build_item(race, pl, item, carry if i != -1 else None, avail, f_alch)
            if i == target:
                if built > 0 and first == 0:
                    first = year
                if status == 2:
                    if first == 0:
                        return 0, 0
                    return first, year - 1
                if status in (0, 1):
                    return first, year
            f_alch = False
            if item['kind'] == 1:
                if item['id'] in (0, 8):
                    pl['mines'] += built
                elif item['id'] in (1, 7):
                    pl['factories'] += built
            if status >= 5:
                break
            i += 1
        if target < 0:
            return avail[3] + (tax if target == -1 else 0), None
        pl['surface'] = avail[:3]
        g, pl['k'] = growth(race, pl['P'], pl['k'], pl['hab'], pl['max'])
        pl['P'] += g
    if first == 0:
        first = 100
    return first, 100


def production_text(first, last, item):
    """What the production tile and dialog print for an estimate."""
    if first == 100:
        auto = item['kind'] == 1 and item['id'] < 7
        return 'Unknown' if auto else 'Never'
    if last == 100:
        return '%d - ??? years' % first
    if last != first:
        return '%d - %d years' % (first, last)
    if first == 0:
        return 'Skipped'
    if first == -1:
        return 'As Needed'
    return '%d year%s' % (first, '' if first == 1 else 's')


# ---------------------------------------------------------------- fleets

def design_engine(d):
    for s in d['slots']:
        m = re.match(r'(\d+) (.*)', s)
        if m and m.group(2) in ENGINES:
            return m.group(2), int(m.group(1))
    return None, 0


def cargo_capacity(d):
    return BYNAME[d['hull']]['stats'].get('cargo_capacity') or 0


def factor(st, dn, w):
    eng, _ = design_engine(st['designs'][dn])
    if eng is None:
        return 99999
    return ENGINES[eng]['stats']['fuel_table'][w]


def fuel_cost(st, fleet, w, L, range_mode=False):
    """KERNEL.md "Fuel cost" for L light-years at warp w. In range mode the
    cost of 1000 ly in mg, truncated (KERNEL.md "Not enough fuel")."""
    cargo = sum(fleet['cargo'])
    order = sorted(fleet['ships'], key=lambda dn: (factor(st, dn, w), dn))
    tenths = 0
    for dn in order:
        n = fleet['ships'][dn]
        d = st['designs'][dn]
        take = min(cargo, cargo_capacity(d) * n)
        cargo -= take
        f = factor(st, dn, w)
        if f > 0:
            tenths += f * L * (n * d['mass'] + take) // 2000
    return tenths // 10 if range_mode else (tenths + 9) // 10


def ram_gain(st, fleet, w, L):
    """Fuel a year's move of L ly gains from engines free at warp w."""
    if w >= 10:
        return 0
    g = 0
    for dn, n in fleet['ships'].items():
        eng, e = design_engine(st['designs'][dn])
        if eng is None:
            continue
        t = ENGINES[eng]['stats']['fuel_table']
        k = 0
        if t[w] == 0:
            k = e
            if t[w + 1] == 0:
                k = 3 * e
                if w < 9 and t[w + 2] == 0:
                    k = 6 * e
                    if w < 8 and t[w + 3] == 0:
                        k = 10 * e
        g += n * k
    return g * L


def ideal_warp(st, fleet):
    """The warp the client uses for "Est. Range"."""
    w = 10
    for dn in sorted(fleet['ships']):
        eng, _ = design_engine(st['designs'][dn])
        if eng is None:
            return 0
        t = ENGINES[eng]['stats']['fuel_table']
        while w > 0:
            if t[w] <= 120:
                if t[w] > 0 and eng not in NO_SCOOP_ADJUST:
                    if w >= 5 and t[w - 1] == 0:
                        w -= 1
                    elif w >= 6 and t[w - 2] == 0:
                        w -= 2
                    elif w > 6 and t[w - 3] == 0:
                        w -= 3
                if w == 10 and eng not in WARP10_NO_CAP:
                    w = 9
                break
            w -= 1
    return w


def est_range(st, fleet):
    w = ideal_warp(st, fleet)
    c = fuel_cost(st, fleet, w, 1000, range_mode=True)
    if c == 0:
        return 'Infinite'
    if c <= 100000:
        r = fleet['fuel'] * 1000 // c
    else:
        r = fleet['fuel'] // (c // 1000)
    return '%d l.y.' % r


def leg(fleet, j):
    a, b = fleet['wps'][j], fleet['wps'][j + 1]
    return math.hypot(b['x'] - a['x'], b['y'] - a['y']), b['warp']


GATE = re.compile(r'Stargate (\w+)/(\w+)')


def gate_of(st, n):
    """(mass limit, range) of the stargate on planet n's starbase, None
    for "any"; None when it has no gate. Only the viewer's own starbase
    designs are known (the client tests ownership first)."""
    p = st['planets'].get(n, {})
    if not p.get('starbase'):
        return None
    m = GATE.search(st.get('sbdesigns', {}).get(p.get('sbdesign'), ''))
    if not m:
        return None
    return tuple(None if v == 'any' else int(v) for v in m.groups())


def planet_at(st, x, y):
    for n, (px, py) in st['xy'].items():
        if (px, py) == (x, y):
            return n
    return None


def gate_check(st, fleet, j):
    """The client's stargate check for leg j (a warp-11 leg): 0 = refused,
    -1 = not known, else 1 | 2 if some design takes losses | 4 if the
    fleet carries cargo (unloaded before the jump unless IT)."""
    a, b = fleet['wps'][j], fleet['wps'][j + 1]
    dst = planet_at(st, b['x'], b['y'])
    if dst is None:
        return 0
    dp = st['planets'].get(dst, {})
    if dp.get('owner') != st['owner']:
        # an unowned planet reported this year: refused; anyone else's: unknown
        return 0 if dp.get('owner') == '-1' else -1
    dgate = gate_of(st, dst)
    if dgate is None:
        return 0
    src = planet_at(st, a['x'], a['y'])
    sgate = gate_of(st, src) if src is not None and st['planets'].get(src, {}).get('owner') == st['owner'] else None
    if sgate is None:
        return 0
    D, _ = leg(fleet, j)
    d = int(D)
    R = 8000 if sgate[1] is None else sgate[1]
    danger = False
    for dn in fleet['ships']:
        mass = st['designs'][dn]['mass']
        if d > 5 * R:
            return 0
        f = 10000
        if d > R:
            f = (5 * R - d) * 2500 // R
        for M in (sgate[0], dgate[0]):
            if M is not None and 0 < M < mass:
                if 5 * M < mass:
                    return 0
                f = ((5 * M - mass) * 2500 // M) * f // 10000
        pct = 100 if f <= 0 else (10000 - f) // 100
        if pct >= 100 and f <= 0:
            return 0
        if pct > 0:
            danger = True
    cargo = any(fleet['cargo']) and int(st['player']['prt']) != 7
    return 1 | (2 if danger else 0) | (4 if cargo else 0)


GATE_TEXT = {0: 'Never', -1: 'Uncertain'}


def travel_time(fleet, i, st=None):
    """Years to reach waypoint i (sum over legs); None = "Never"; a string
    for a stargate leg the client cannot price."""
    total = 0
    for j in range(i):
        D, w = leg(fleet, j)
        if w == 0:
            return None
        if w > 10:
            if st is None:
                raise ValueError('stargate legs need the game state')
            g = gate_check(st, fleet, j)
            if g == 0:
                return None
            if g == -1:
                return 'Uncertain'
            if g & 2:
                return 'Danger'
            if g != 1:
                return 'Unload'
            total += 1
            continue
        v = w * w
        t = int(D)
        total += 1 if t <= v else (t + v - 1) // v
    return total


def travel_text(fleet, i, short=False, st=None):
    t = travel_time(fleet, i, st)
    if t is None:
        return 'Never'
    if isinstance(t, str):
        return t
    if short:
        return '%dy' % t
    return '%d year%s' % (t, '' if t == 1 else 's')


def leg_fuel(st, fleet, j, own_player=0):
    D, w = leg(fleet, j)
    if w == 0 or w > 10:
        return 0
    dd = D + 0.99999
    Li = int(dd)
    years = int(dd / (w * w) * 1.0 + 0.9999)
    fuel = fuel_cost(st, fleet, w, int(D + 0.9999))
    if years > 1:
        b = fuel_cost(st, fleet, w, w * w)
        split = (years - 1) * b + fuel_cost(st, fleet, w, Li - (years - 1) * w * w)
        fuel = max(fuel, split)
        g = ram_gain(st, fleet, w, w * w)
        for dn, n in fleet['ships'].items():
            if st['designs'][dn]['hull'] in FUEL_TRANSPORTS:
                g += 200 * n
        if g > 0:
            if g >= b:
                fuel = b
            else:
                fuel = min(fuel, b + (b - g) * (years - 1))
    return fuel


DOCK_HULLS = {r['name'] for r in TABLE['items'] if r['category'] == 'starbase_hull' and r['stats']['dock_capacity'] != 0}


def refuels_at(st, wp):
    """A waypoint at one of the player's planets whose starbase can build
    ships (its hull has a dock)."""
    if (wp['type'] & 15) != 1:
        return False
    p = st['planets'].get(wp['obj'], {})
    if p.get('owner') != st['owner'] or not p.get('starbase'):
        return False
    hull = st.get('sbdesigns', {}).get(p.get('sbdesign'), '').split(',')[0].strip()
    return hull in DOCK_HULLS


def fuel_to(st, fleet, i):
    """"Est Fuel Usage" to waypoint i: the largest running total of leg fuel,
    the total restarting from 0 after each refuelling waypoint."""
    run = best = 0
    for j in range(i):
        run += leg_fuel(st, fleet, j)
        best = max(best, run)
        if refuels_at(st, fleet['wps'][j + 1]):
            run = 0
    return best


def distance_text(fleet, j):
    D, _ = leg(fleet, j)
    c = int(D * 100 + 0.5)
    return '%d.%d l.y.' % (c // 100, c % 100)


# ---------------------------------------------------------------- research

def level_cost(race, field, level):
    c = BASE_COST[level] + 10 * sum(race.tech)
    s = race.rcost[field]
    if s == 0:
        c = 2 * c - c // 4
    elif s == 2:
        c = c // 2
    return c


def research_needed(race):
    f = race.field
    if race.tech[f] >= 26:
        return None
    return max(0, level_cost(race, f, race.tech[f] + 1) - race.accum[f])


def projected_budget(race, st, owned):
    total = 0
    for n in owned:
        pl = planet_state(race, st, n)
        q = st['queues'].get(n)
        if q:
            r, _ = production_estimate(race, pl, q, -1)
        else:
            r = resources(race, pl['P'], pl['factories'], pl['max'])
        total += r
    return total


def research_years(race, needed, budget):
    if needed is None:
        return 'Maxed Out'
    if needed == 0:
        y = 1
    else:
        if budget == 0:
            return 'Never'
        b = budget
        if race.lrt & (1 << 4):     # Generalized Research: half to the current field
            b = budget - budget // 2
        y = (needed + b - 1) // b
    return '%d year%s' % (y, '' if y == 1 else 's')


# ---------------------------------------------------------------- planets

def terraform_reach(race):
    """Best terraforming amount per axis with the player's tech (no LRTs)."""
    best = [0, 0, 0]
    for r in TABLE['items']:
        if r['category'] != 'terraform' or r['restriction']['lrt_required']:
            continue
        t = r['tech']
        have = [race.tech[0], race.tech[1], race.tech[2], race.tech[3], race.tech[4], race.tech[5]]
        need = [t['energy'], t['weapons'], t['propulsion'], t['construction'], t['electronics'], t['biotechnology']]
        if any(h < q for h, q in zip(have, need)):
            continue
        ax = {'gravity': 0, 'temperature': 1, 'radiation': 2}[r['stats']['axis']]
        best[ax] = max(best[ax], r['stats']['amount'])
    return best


def opt_value(race, env, orig):
    """Planet value after the terraforming the player's tech allows."""
    reach = terraform_reach(race)
    new = env[:]
    for a in range(3):
        if race.immune(a) or reach[a] == 0 or env[a] == race.centre[a]:
            continue
        lo, hi = orig[a] - reach[a], orig[a] + reach[a]
        lo = max(1, lo) if lo < env[a] else -1
        hi = min(99, hi) if env[a] < hi else -1
        c = race.centre[a]
        if env[a] < c and hi != -1:
            new[a] = min(c, hi)
        elif env[a] > c and lo != -1:
            new[a] = max(c, lo)
    return hab(race, new)


def pop_text(race, pl, name):
    """The population summary for one of the player's planets."""
    h = pl['hab']
    if h < 0:
        return '%s will kill off approximately %d.%d%% of your colonists each turn.' % (name, -h // 10, -h % 10)
    g, _ = growth(race, pl['P'], pl['k'], h, pl['max'])
    if pl['P'] < pl['max'] and g > 0:
        return 'grow by %d00 to %d00 next year' % (g, pl['P'] + g)
    return 'no growth line'
