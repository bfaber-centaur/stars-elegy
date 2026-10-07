"""Scanning corpus (SC-) helpers: a behavior-level visibility model, case
placement, spec writing and checking against combatlab dumps.

The model restates the scanning predictions handed to this lane (stars-decomp
scanning predictions S-1..S-24) as formulas over observable game state. It is
a prediction device for the SC- runs, not a statement that the rules hold;
docs/PARITY.md "Scanning" records what the runs showed.

Alternative rules (ALTS) are the plausible variants each case is meant to
discriminate. For every expectation the case table lists which alternatives
predict a different outcome, so a mismatch points at a specific rule.
"""
import math, os, re, subprocess

# Ship scanner parts: normal range, penetrating range (S-1, docs/scanning
# predictions). Pick Pocket and Robber Baron also see cargo (S-20).
SCAN = {
    'Bat Scanner': (0, 0), 'Rhino Scanner': (50, 0), 'Mole Scanner': (100, 0),
    'DNA Scanner': (125, 0), 'Possum Scanner': (150, 0), 'Pick Pocket Scanner': (80, 0),
    'Chameleon Scanner': (160, 45), 'Ferret Scanner': (185, 50), 'Dolphin Scanner': (220, 100),
    'Gazelle Scanner': (225, 0), 'RNA Scanner': (230, 0), 'Cheetah Scanner': (275, 0),
    'Elephant Scanner': (300, 200), 'Eagle Eye Scanner': (335, 0),
    'Robber Baron Scanner': (220, 120), 'Peerless Scanner': (500, 0),
}
CLOAK_PTS = {'Transport Cloaking': 300, 'Stealth Cloak': 70, 'Super-Stealth Cloak': 140,
             'Ultra-Stealth Cloak': 540, 'Multi Function Pod': 60}
TACHYON = [100, 95, 93, 91, 90, 89, 88, 87, 86, 86, 85, 84, 84, 83, 83, 82, 82, 81]
# Masses (kT) from the game's item table, as StarsAPI lists them.
MASS = {
    'Small Freighter': 25, 'Medium Freighter': 60, 'Large Freighter': 125, 'Super Freighter': 175,
    'Quick Jump 5': 4, 'Long Hump 6': 9,
    'Transport Cloaking': 1, 'Stealth Cloak': 2, 'Super-Stealth Cloak': 3, 'Ultra-Stealth Cloak': 5,
    'Tachyon Detector': 1, 'Bat Scanner': 2, 'Rhino Scanner': 5, 'Mole Scanner': 2, 'DNA Scanner': 2,
    'Possum Scanner': 3, 'Pick Pocket Scanner': 15, 'Chameleon Scanner': 6, 'Ferret Scanner': 2,
    'Dolphin Scanner': 4, 'Gazelle Scanner': 5, 'Elephant Scanner': 6, 'Robber Baron Scanner': 20,
}
# Planetary scanners: (energy, elec, bio) requirement, normal, penetrating (S-7, S-8).
PSCAN = [((0, 0, 0), 50, 0), ((0, 1, 0), 90, 0), ((0, 3, 0), 150, 0), ((0, 6, 0), 220, 0),
         ((0, 8, 0), 280, 0), ((3, 10, 3), 320, 160), ((4, 13, 6), 400, 200),
         ((5, 16, 7), 500, 250), ((7, 23, 9), 620, 310)]

ALTS = {
    'A2': 'cloak bound floor((100-c)^2 R^2 / 10000) (one rounding)',
    'A3': 'cloak shrinks the range first: R\' = floor(R (100-c)/100), d <= R\'',
    'intdist': 'distance truncated to an integer before comparing with R',
    'notrunc': 'combined range not truncated (d^2 <= sqrt(sum r^4))',
    'stackcomb': 'a fleet combines scanners across stacks / ship counts (fourth-root sum)',
    'maxcloak': 'a fleet\'s cloak is its best stack\'s cloak (no mass weighting)',
    'fuel': 'fuel counts as cargo in cloak dilution',
    'tachm1': 'tachyon table indexed by count-1',
    'tachround': 'tachyon-scaled cloak rounded to nearest',
    'orbitR': 'an orbiting fleet needs only the normal range (no penetrating test)',
    'normplanets': 'normal scanners also reveal planets within R',
    'nocoloc': 'a co-located fleet still needs scanner range / passes the cloak test',
    'sbnohide': 'a cloaked starbase is never hidden from a planet report',
    'sbR': 'starbase hiding uses the normal range instead of the penetrating range',
    'installed': 'planet scanner is the installed one, not the best at current tech',
    'naszero': 'NAS also zeroes ship penetrating ranges',
    'nasplanetpen': 'NAS keeps penetrating planet scanners (normal range doubled)',
    'nomax': 'a JOAT hull built-in scanner and a scanner part are not combined (the larger one counts)',
    'wmpartial': 'War Monger viewers get partial designs like everyone else',
}


def pct_from_pts(u):
    if u <= 100:
        return u >> 1
    if u <= 300:
        return ((u - 100) >> 3) + 50
    if u <= 612:
        return (u - 300) // 24 + 75
    if u <= 1124:
        return ((u - 612) >> 6) + 88
    if u < 1612:
        return 97 if u >= 1380 else 96
    return 98


class Design:
    def __init__(self, owner, num, hull, slots, name, starbase=False):
        self.owner, self.num, self.hull, self.slots, self.name, self.sb = owner, num, hull, slots, name, starbase

    def spec(self):
        s = ', '.join('empty' if c == 0 else '%d %s' % (c, it) for c, it in self.slots)
        return '%s %d %d %s, %s = %s' % ('sbdesign' if self.sb else 'design', self.owner, self.num,
                                         self.hull, s, self.name)

    @property
    def mass(self):
        return MASS.get(self.hull, 0) + sum(c * MASS.get(it, 0) for c, it in self.slots)

    def cloak_pts(self):
        return sum(c * CLOAK_PTS.get(it, 0) for c, it in self.slots)

    def scanner(self, alt=(), race=None):
        """(normal, pen, tachyon count, pickpocket, robberbaron); normal -1 = blind.

        race: the owner's {'prt', 'lrt', 'elec'}. JOAT Scouts, Frigates and
        Destroyers carry a built-in 20*elec / 10*elec scanner (S-10); NAS
        doubles the normal range only (S-9)."""
        r4 = p4 = 0
        has = False
        if race and race['prt'] == 9 and self.hull in ('Scout', 'Frigate', 'Destroyer'):
            has = True
            r4 += (20 * race['elec']) ** 4
            p4 += (10 * race['elec']) ** 4
        tach = 0
        pp = rb = False
        for c, it in self.slots:
            if it in SCAN:
                has = True
                r, p = SCAN[it]
                r4 += c * r ** 4
                p4 += c * p ** 4
                pp |= it in ('Pick Pocket Scanner', 'Robber Baron Scanner')
                rb |= it == 'Robber Baron Scanner'
            if it == 'Tachyon Detector':
                tach += c
        if not has:
            return -1, 0, tach, pp, rb
        nas = race and race['lrt'] >> 10 & 1
        if 'notrunc' in alt:
            return r4 ** 0.25 * (2 if nas else 1), p4 ** 0.25, tach, pp, rb
        r, p = int(r4 ** 0.25 + 1e-9), int(p4 ** 0.25 + 1e-9)
        if nas:
            r *= 2
            if 'naszero' in alt:
                p = 0
        if 'nomax' in alt and race and race['prt'] == 9 and self.hull in ('Scout', 'Frigate', 'Destroyer'):
            parts = [SCAN[it] for c, it in self.slots if it in SCAN] + [(20 * race['elec'], 10 * race['elec'])]
            r, p = max(x[0] for x in parts) * (2 if nas else 1), max(x[1] for x in parts)
        return r, p, tach, pp, rb


class Fleet:
    def __init__(self, owner, fid, x, y, stacks, cargo=(0, 0, 0, 0), fuel=50, planet=-1, tag=''):
        self.owner, self.id, self.x, self.y = owner, fid, x, y
        self.stacks = stacks          # [(Design, count)]
        self.cargo, self.fuel, self.planet, self.tag = list(cargo), fuel, planet, tag

    def spec(self):
        s = 'fleet %d %d' % (self.owner, self.id)
        if self.planet >= 0:
            s += ' planet %d' % self.planet
        s += ' at %d %d ships %s fuel %d' % (self.x, self.y,
                                            ','.join('%d:%d' % (d.num, n) for d, n in self.stacks), self.fuel)
        if any(self.cargo):
            s += ' cargo %d %d %d %d' % tuple(self.cargo)
        return s + ('  # ' + self.tag if self.tag else '')

    def cloak(self, alt=()):
        if 'maxcloak' in alt:
            return max(pct_from_pts(d.cloak_pts()) for d, n in self.stacks)
        num = den = 0
        for d, n in self.stacks:
            m = d.mass * n
            num += d.cloak_pts() * m
            den += m
        if num == 0:
            return 0
        den += sum(self.cargo) + (self.fuel if 'fuel' in alt else 0)
        return pct_from_pts(num // den)

    def scanner(self, alt=(), race=None):
        sc = [d.scanner(alt, race) for d, n in self.stacks]
        if 'stackcomb' in alt:
            r4 = sum(n * max(s[0], 0) ** 4 for (d, n), s in zip(self.stacks, sc))
            p4 = sum(n * s[1] ** 4 for (d, n), s in zip(self.stacks, sc))
            nr = int(r4 ** 0.25 + 1e-9) if any(s[0] >= 0 for s in sc) else -1
            return nr, int(p4 ** 0.25 + 1e-9), min(s[2] for s in sc), any(s[3] for s in sc), any(s[4] for s in sc)
        return (max(s[0] for s in sc), max(s[1] for s in sc), max(s[2] for s in sc),
                any(s[3] for s in sc), any(s[4] for s in sc))


def cloak_ok(dd, r2, c, alt):
    """Detection test for a cloaked target at squared distance dd."""
    if c == 0:
        return True
    k = 100 - c
    if 'A2' in alt:
        return dd <= k * k * r2 // 10000
    if 'A3' in alt:
        r = math.isqrt(int(r2)) * k // 100
        return dd <= r * r
    return dd <= (int(k * r2) // 100) * k // 100


def in_range(dd, r2, alt):
    if 'intdist' in alt:
        return int(math.sqrt(dd)) ** 2 <= r2
    return dd <= r2


class Game:
    """One SC- run: designs, fleets, planet edits, tech; predicts each player's view."""
    def __init__(self, planets_xy):
        self.pxy = planets_xy
        self.designs, self.fleets = [], []
        self.planet_lines = []          # spec lines for planets
        self.owned = {17: 0, 8: 1}      # planet -> owner
        self.pscanner = {17: False, 8: False}
        # planet -> starbase Design; both homeworlds start with an uncloaked station
        self.sb = {17: Design(0, 0, 'Space Station', [], 'base', True),
                   8: Design(1, 0, 'Space Station', [], 'base', True)}
        self.tech = {0: [26] * 6, 1: [26] * 6}
        self.relations = []
        self.prt, self.lrt, self.hab = {0: 9, 1: 9}, {0: 0, 1: 0}, {}
        self.cases = []                 # (id, viewer, kind, key, expected, claims, note)
        self.groups = {}                # fleet key -> group name
        self.extra = []

    def design(self, *a, **k):
        d = Design(*a, **k)
        self.designs.append(d)
        return d

    def fleet(self, owner, stacks, x, y, group, **k):
        fid = sum(1 for f in self.fleets if f.owner == owner)
        f = Fleet(owner, fid, x, y, stacks, **k)
        self.fleets.append(f)
        self.groups[(owner, fid)] = group
        return f

    # ------------------------------------------------------------ the model
    def race(self, p):
        return {'prt': self.prt[p], 'lrt': self.lrt[p], 'elec': self.tech[p][4]}

    def planet_scan(self, pid, owner, alt):
        if not self.pscanner.get(pid):
            return 0, 0
        en, _, _, _, el, bio = self.tech[owner]
        nas = self.lrt[owner] >> 10 & 1
        best = PSCAN[0]
        for req, r, p in PSCAN:
            if nas and p and 'nasplanetpen' not in alt:
                continue
            if en >= req[0] and el >= req[1] and bio >= req[2]:
                best = (req, r, p)
        if 'installed' in alt:
            best = PSCAN[2]
        return best[1] * (2 if nas else 1), best[2]

    def predict(self, v, alt=(), only=None):
        """Player v's view: {('fleet', owner, id): level, ('planet', pid): level}."""
        view = {}

        def mark(key, lvl):
            if view.get(key, 0) < lvl:
                view[key] = lvl

        mine = [f for f in self.fleets if f.owner == v and (only is None or self.groups[(f.owner, f.id)] in only)]
        others = [f for f in self.fleets if f.owner != v]
        # orbiting viewers report their planet
        for f in mine:
            if f.planet >= 0:
                nr, pen, tach, pp, rb = f.scanner(alt, self.race(v))
                mark(('planet', f.planet), 4 if rb else (1 if nr < 0 else 3))
        scanners = []
        for f in mine:
            nr, pen, tach, pp, rb = f.scanner(alt, self.race(v))
            scanners.append(((f.x, f.y), max(nr, 0), pen, tach, pp, rb, f, nr < 0))
        if only is None:
            for pid, o in self.owned.items():
                if o == v:
                    r, p = self.planet_scan(pid, v, alt)
                    scanners.append((self.pxy[pid], r, p, 0, False, False, None, r == 0))
        for (xy, r, pen, tach, pp, rb, f, blind) in scanners:
            r2, p2 = r * r, pen * pen
            for g in others:
                dd = (g.x - xy[0]) ** 2 + (g.y - xy[1]) ** 2
                key = ('fleet', g.owner, g.id)
                if pp and f is not None and dd == 0:
                    mark(key, 4)
                if dd == 0 and 'nocoloc' not in alt and f is not None:
                    mark(key, 3)
                    continue
                if not in_range(dd, r2, alt) or (blind and f is not None):
                    continue
                if g.planet >= 0 and 'orbitR' not in alt and not in_range(dd, p2, alt):
                    continue
                c = g.cloak(alt)
                if tach and c:
                    t = TACHYON[min(17, max(0, tach - 1 if 'tachm1' in alt else tach))]
                    c = (c * t + 50) // 100 if 'tachround' in alt else c * t // 100
                if c and not cloak_ok(dd, r2, c, alt):
                    continue
                if c and g.planet >= 0 and 'orbitR' not in alt and not cloak_ok(dd, p2, c, alt):
                    continue
                mark(key, 3)
            # planets
            reach = r2 if 'normplanets' in alt else p2
            if reach > 0 or 'normplanets' in alt:
                for pid, pxy in enumerate(self.pxy):
                    dd = (pxy[0] - xy[0]) ** 2 + (pxy[1] - xy[1]) ** 2
                    if self.owned.get(pid) == v:
                        continue
                    if dd <= reach and reach > 0:
                        lvl = 3
                        sb = self.sb.get(pid)
                        if sb is not None and 'sbnohide' not in alt:
                            c = pct_from_pts(sb.cloak_pts()) if sb.cloak_pts() else 0
                            k2 = (100 - c) ** 2
                            ref = r2 if 'sbR' in alt else p2
                            if dd > k2 * ref // 10000:
                                lvl = 2
                        mark(('planet', pid), lvl)
        # designs of what was seen: partial, or full for a War Monger viewer (S-20)
        dl = 3 if self.prt[v] != 2 or 'wmpartial' in alt else 7
        for f in others:
            if view.get(('fleet', f.owner, f.id)):
                for d, n in f.stacks:
                    mark(('design', f.owner, d.num), dl)
        for pid, o in self.owned.items():
            if o != v and view.get(('planet', pid), 0) not in (0, 2) and pid in self.sb:
                mark(('sbdesign', o, self.sb[pid].num), dl)
        # other players' blocks: known players only; a Claim Adjuster viewer gets
        # them with habitability (and nothing else) filled in (S-20)
        known = {k[1] for k, l in view.items() if k[0] in ('fleet', 'design', 'sbdesign') and l}
        known |= {self.owned[k[1]] for k, l in view.items() if k[0] == 'planet' and l and k[1] in self.owned}
        for o in known - {v}:
            view[('player', o)] = 'hab' if self.prt[v] == 3 else 'partial'
        for pid, o in self.owned.items():
            if o == v:
                view[('planet', pid)] = 7
        for f in self.fleets:
            if f.owner == v:
                view[('fleet', f.owner, f.id)] = 7
        return view

    # ------------------------------------------------------------ cases
    def expect(self, cid, v, key, claims, note='', group=None):
        """Record an expectation: key observed at the model's level in player v's .M."""
        lvl = self.predict(v).get(key, 0)
        diff = [a for a in ALTS if self.predict(v, (a,)).get(key, 0) != lvl]
        if group is not None:
            solo = self.predict(v, only={group}).get(key, 0)
            assert solo == lvl, '%s: outcome depends on another group (%d vs %d)' % (cid, solo, lvl)
        self.cases.append((cid, v, key, lvl, claims, diff, note))

    def spec(self, title):
        out = ['# ' + title, '# generated by experiments/sc/gen.py; do not edit by hand']
        for p in (0, 1):
            for i, n in enumerate(('energy', 'weapons', 'prop', 'con', 'elec', 'bio')):
                out.append('tech %d %s %d' % (p, n, self.tech[p][i]))
            out.append('research %d 0' % p)
        for p in (0, 1):
            if self.prt[p] != 9:
                out.append('prt %d %d' % (p, self.prt[p]))
            if self.lrt[p]:
                out.append('lrt %d %#x' % (p, self.lrt[p]))
            if p in self.hab:
                out.append('hab %d %s' % (p, ','.join(map(str, self.hab[p]))))
        out += self.relations
        out += self.planet_lines
        for d in sorted(self.designs, key=lambda d: (d.sb, d.owner, d.num)):
            out.append(d.spec())
        for f in self.fleets:
            out.append(f.spec())
        out += self.extra
        return '\n'.join(out) + '\n'

    def table(self):
        lines = ['# case\tviewer\tobject\texpected\tclaims\talternatives that predict otherwise\tnote']
        for cid, v, key, lvl, claims, diff, note in self.cases:
            obj = 'fleet %d/%d' % key[1:] if key[0] == 'fleet' else 'planet %d' % key[1]
            lines.append('%s\t%d\t%s\t%d\t%s\t%s\t%s' % (cid, v, obj, lvl, ','.join(claims),
                                                         ','.join(diff) or '-', note))
        return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------- geometry

def reps(n):
    """All integer (dx, dy) with dx^2 + dy^2 = n."""
    out = []
    for a in range(math.isqrt(n) + 1):
        b2 = n - a * a
        b = math.isqrt(b2)
        if b * b == b2:
            for sa in (1, -1):
                for sb in (1, -1):
                    for p in ((a * sa, b * sb), (b * sb, a * sa)):
                        if p not in out:
                            out.append(p)
    return out


def rep_at_most(n, lo=0):
    """Largest representable m with lo < m <= n."""
    for m in range(n, lo, -1):
        if reps(m):
            return m
    return None


def rep_above(n):
    m = n + 1
    while not reps(m):
        m += 1
    return m


class Placer:
    """Picks free target positions around a viewer at a given squared distance."""
    def __init__(self, game):
        self.g = game
        self.used = set(map(tuple, game.pxy))

    def at(self, center, d2, avoid=()):
        """A free point at d2 from center; with avoid, the one farthest from those points."""
        cands = []
        for dx, dy in reps(d2):
            p = (center[0] + dx, center[1] + dy)
            if p not in self.used and 1000 < p[0] < 1400 and 1000 < p[1] < 1400:
                cands.append(p)
        if not cands:
            raise ValueError('no free point at d2=%d around %s' % (d2, center))
        if avoid:
            cands.sort(key=lambda p: -min((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2 for a in avoid))
        self.used.add(cands[0])
        return cands[0]

    def take(self, p):
        self.used.add(tuple(p))
        return p


# ---------------------------------------------------------------- tools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
COMBATLAB = os.path.join(ROOT, 'tools', 'fleetlab', 'combatlab')


def planets_xy(xyfile):
    out = subprocess.run([COMBATLAB, 'dump', xyfile], capture_output=True, text=True, check=True).stdout
    pts = {}
    for m in re.finditer(r'xy planet (\d+) x=(\d+) y=(\d+)', out):
        pts[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
    return [pts[i] for i in range(len(pts))]


def observed(dump_text, turn):
    """Per player view in the given turn's section of each .M file of a combatlab dump."""
    views, cur = {}, None
    for line in dump_text.splitlines():
        m = re.match(r'\S+\.M(\d+) file turn=(\d+)', line)
        if m:
            cur = views.setdefault(int(m.group(1)) - 1, {}) if int(m.group(2)) == turn else None
            continue
        if cur is None or '.M' not in line.split(' ')[0]:
            continue
        m = re.search(r' fleet owner=(\d+) id=(\d+) kind=(\d+).*cargo=(\d+)/(\d+)/(\d+)/(\d+)', line)
        if m:
            cur[('fleet', int(m.group(1)), int(m.group(2)))] = int(m.group(3))
            cur[('cargo', int(m.group(1)), int(m.group(2)))] = tuple(int(m.group(i)) for i in range(4, 8))
            continue
        m = re.search(r' seen planet (\d+) owner=(-?\d+) level=(\d+) starbase=(\w+)', line)
        if m:
            cur[('planet', int(m.group(1)))] = int(m.group(3))
            cur[('sbbit', int(m.group(1)))] = m.group(4) == 'true'
            continue
        m = re.search(r' (sb)?design owner=(\S+) n=(\d+) mass=(\d+) armor=(-?\d+) full=(\w+)', line)
        if m:
            cur.setdefault('sbdesigns' if m.group(1) else 'designs', []).append(m.group(6) == 'true')
            continue
        m = re.search(r' player (\d+) shipdesigns.*?(?: energy=(\d+) weapons=(\d+) prop=(\d+) con=(\d+) elec=(\d+) bio=(\d+).*hab=([\d,]+))?$', line)
        if m:
            n = int(m.group(1))
            cur[('player', n)] = ('full', [int(x) for x in m.group(8).split(',')],
                                  [int(m.group(i)) for i in range(2, 8)]) if m.group(8) else ('partial',)
    return views
