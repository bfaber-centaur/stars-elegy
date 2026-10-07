"""One year of fleet movement and fuel, as docs/KERNEL.md "Fleet movement" states it.

Used by gen.py to write the FM round-2 predictions. Only what those cases need
is modelled: ordinary legs (distance, arrival, rounding, fuel, running dry,
ram scoops, top-up) and chasers (rounds, rule 6 fuel). Every number comes from
KERNEL.md; where KERNEL.md is BINARY-ONLY the comment says so.
"""
import math

# Engine fuel tables, warp 0..10 (COMPONENTS.md / data/components.json).
ENGINES = {
    'Quick Jump 5': [0, 0, 25, 100, 100, 100, 180, 500, 800, 900, 1080],
    'Long Hump 6': [0, 0, 20, 60, 100, 100, 105, 450, 750, 900, 1080],
    'Fuel Mizer': [0, 0, 0, 0, 0, 35, 120, 175, 235, 360, 420],
    'Trans-Star 10': [0, 0, 5, 15, 20, 25, 30, 35, 40, 45, 50],
    'Radiating Hydro-Ram Scoop': [0, 0, 0, 0, 0, 0, 0, 165, 375, 600, 720],
}
NOENGINE = 99999   # factor for a design whose engine slot is not full (BINARY-ONLY, stars-decomp reading)


class Design:
    def __init__(self, num, mass, engine, e=1, full=True, cargo=0, tank=0):
        self.num, self.mass, self.engine, self.e, self.full = num, mass, engine, e, full
        self.cargo, self.tank = cargo, tank

    def f(self, w, ife=False):
        if not self.full:
            return NOENGINE
        f = ENGINES[self.engine][w]
        return f - 15 * f // 100 if ife else f


class Fleet:
    def __init__(self, key, x, y, stacks, fuel, cargo=0, wps=(), ife=False):
        """stacks: [(Design, n)] in design order; wps: [(x, y, warp)] or (fleet_key, warp)."""
        self.key, self.x, self.y, self.stacks, self.fuel, self.cargo = key, x, y, stacks, fuel, cargo
        self.wps, self.ife = list(wps), ife
        self.tank = sum(d.tank * n for d, n in stacks)
        self.dry = False
        self.warp_after = None

    # ---- fuel
    def tenths(self, w, dist):
        t, left = 0, self.cargo
        for d, n in sorted(self.stacks, key=lambda s: (s[0].f(w, self.ife), s[0].num)):
            take = min(left, n * d.cargo)
            left -= take
            f = d.f(w, self.ife)
            if f:
                t += f * dist * (n * d.mass + take) // 2000
        return t

    def cost(self, w, dist):
        return (self.tenths(w, dist) + 9) // 10

    def rng(self, w, fuel=None):
        fuel = self.fuel if fuel is None else fuel
        c = self.tenths(w, 1000) // 10
        if c == 0:
            return 10 ** 9
        return fuel * 1000 // c if c <= 100000 else fuel // (c // 1000)

    def gain(self, w, dist):
        g = 0
        for d, n in self.stacks:
            t = ENGINES[d.engine] if d.full else None
            if t is None or w > 9 or t[w]:
                continue
            k = d.e
            if t[w + 1] == 0:
                k = 3 * d.e
                if w <= 8 and t[w + 2] == 0:
                    k = 6 * d.e
                    if w <= 7 and t[w + 3] == 0:
                        k = 10 * d.e
            g += n * k * dist
        return g


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def step_to(x0, y0, tx, ty, A, D):
    """Distance and arrival rules 2-3: returns (x, y, arrived)."""
    E = math.trunc(D - 0.99999)
    if E < A or E <= 0:
        return tx, ty, True
    def ax(o, t):
        v = (t - o) * A / D
        return o + math.trunc(v + 0.5 if t > o else v - 0.5)
    return ax(x0, tx), ax(y0, ty), False


def leg_cost_free_warp(fl, legd, w0):
    """Running dry: the lowest warp with a non-zero cost for the whole leg, minus one."""
    for w in range(1, 11):
        if fl.cost(w, legd):
            return w - 1 if w > 1 else w0   # no free warp: warp left unchanged
    return w0


def move_ordinary(fl):
    """One ordinary leg toward wps[0] = (x, y, warp)."""
    tx, ty, w = fl.wps[0]
    D = dist((fl.x, fl.y), (tx, ty))
    legd = math.trunc(D + 0.9999)
    need = fl.cost(w, legd)
    R = fl.rng(w)
    enough = fl.fuel >= need
    allow = max(R, w * w) if enough else R
    A = min(legd, w * w)
    burned = False
    if A > allow:
        fl.fuel, A, burned = 0, allow, True
    else:
        c = fl.cost(w, A)
        burned = c > 0
        fl.fuel = max(0, fl.fuel - c)
    if fl.fuel == 0 and burned and not enough and (A + 0.99999 <= D or allow == 0):
        fl.dry = True
        fl.warp_after = leg_cost_free_warp(fl, legd, w)
    if allow == 0:
        return
    E = math.trunc(D - 0.99999)
    fl.x, fl.y, arrived = step_to(fl.x, fl.y, tx, ty, A, D)
    if not fl.dry:
        fl.fuel = min(fl.tank, fl.fuel + fl.gain(w, min(E, A))) if fl.fuel < fl.tank else fl.fuel
    if enough and not arrived:
        need2 = fl.cost(w, math.trunc(dist((fl.x, fl.y), (tx, ty)) + 0.9999))
        if fl.fuel < need2:
            fl.fuel = min(fl.tank, need2)
    if arrived:
        fl.wps.pop(0)


def year(fleets):
    """fleets: list in host order (owner, number). Moves ordinary fleets, then chasers."""
    by = {f.key: f for f in fleets}
    chasers = []
    for f in fleets:
        if not f.wps:
            f.done = True
            continue
        if isinstance(f.wps[0][0], tuple):
            f.done = False
            f.rem, f.moved, f.f0 = f.wps[0][1] ** 2, 0, f.fuel
            chasers.append(f)
        else:
            move_ordinary(f)
            f.done = True
    for _ in range(10):
        for c in chasers:
            if c.done:
                continue
            t = by[c.wps[0][0]]
            w = c.wps[0][1]
            step = c.rem if t.done else min(c.rem, (c.rem + c.moved + 4) // 5)
            D = dist((c.x, c.y), (t.x, t.y))
            legd = math.trunc(D + 0.9999)
            A = min(legd, step)
            # rule 6 (BINARY-ONLY): R reduced by moved; charge on moved + step from year-start fuel
            R0 = c.rng(w, c.f0)
            need = c.cost(w, legd)
            enough = c.fuel >= need
            allow = (max(R0, w * w) if enough else R0) - c.moved
            burned = False
            if A > allow:
                A, c.fuel, burned = max(allow, 0), 0, True
            else:
                cst = c.cost(w, c.moved + A)
                burned = cst > 0
                c.fuel = max(0, c.f0 - cst)
            E = math.trunc(D - 0.99999)
            if c.fuel == 0 and burned and not enough and (A + 0.99999 <= D or allow <= 0):
                c.dry, c.warp_after = True, leg_cost_free_warp(c, legd, w)
            if A > 0:
                c.x, c.y, arrived = step_to(c.x, c.y, t.x, t.y, A, D)
            else:
                arrived = False
            if not c.dry and c.fuel < c.tank:
                c.fuel = min(c.tank, c.fuel + c.gain(w, min(E, A)))
            if enough and not arrived:
                need2 = c.cost(w, math.trunc(dist((c.x, c.y), (t.x, t.y)) + 0.9999))
                if c.fuel < need2:
                    c.fuel = min(c.tank, need2)
            c.f0 = c.fuel + c.cost(w, c.moved + A)   # refund base for the next round
            if arrived:
                c.done = True
                if not t.done and t in chasers:
                    t.done = True
                continue
            if c.dry:
                c.done = True
                continue
            c.moved += A
            c.rem -= A
            if c.rem <= 0:
                c.done = True
    return fleets
