#!/usr/bin/env python3
"""Write the MF- (minefield) Combat Lab specs and their predictions.

Same apparatus as experiments/ob (Combat Lab universe, fields inserted as
host-file object records, one pinned generation per run). The predictions
are the stars-decomp minefield reading MF-1..MF-12 (private
docs/minefield-predictions.md, stars-decomp #23), restated here as behavior
before any MF run. Mines per year, decay and sweeping are already settled
(OB-001..027) and are only used, not tested.

  python3 experiments/mf/gen.py OUTDIR      # writes OUTDIR/mfNN.spec
  python3 experiments/mf/gen.py --list      # case table with predictions

Model used for the predicted numbers (behavior level):
- A fleet moving through another player's field, when the field owner's
  relation toward the fleet's owner is not friend, makes one draw per whole
  ly travelled inside the field and is stopped with probability
  (e - safe) * {3, 10, 35} per mille per ly for standard, heavy and speed-bump
  fields (safe warp 4, 6, 5), e = the smallest warp 3..10 with e^2 >= d - 1,
  d = the distance travelled this year.
- Damage per design on a hit: (ships * {100, 500} + shortfall) * engines,
  {125, 600} for engines that burn no fuel at warp 4; shortfall = up to a
  fleet minimum of {500, 2000} ({600, 2500}) for fleets under 5 ships, all
  of it on the first design; shields absorb at most half.
- The field that loses mines after a hit is the hitting kind's non-friendly
  field with the smallest d^2 - count at the stop point; it loses
  max(10, count/20), or max(50, count/100) when count/20 > 50.
"""
import importlib.util, os, sys

_spec = importlib.util.spec_from_file_location(
    'obgen', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'ob', 'gen.py'))
_ob = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ob)
XY = _ob.XY  # Combat Lab planet positions

TECH = ''.join('tech %d %s 26\n' % (p, f) for p in (0, 1)
               for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))

# design numbers, the same for both players
TANK, CLOAK, SCOOP, MIZER, SHIELD, LAYER, LASERDD = range(7)
DESIGNS = [
    'Destroyer, 1 Trans-Galactic Drive, empty, empty, empty, 2 Superlatanium, empty, empty = Tank',
    'Destroyer, 1 Trans-Galactic Drive, empty, empty, empty, 2 Superlatanium, empty, 1 Super-Stealth Cloak = Cloak Tank',
    'Destroyer, 1 Trans-Galactic Fuel Scoop, empty, empty, empty, 2 Superlatanium, empty, empty = Scoop Tank',
    'Destroyer, 1 Fuel Mizer, empty, empty, empty, 2 Superlatanium, empty, empty = Mizer Tank',
    'Destroyer, 1 Trans-Galactic Drive, empty, empty, 1 Complete Phase Shield, 2 Superlatanium, empty, empty = Shield Tank',
    'Mini Mine Layer, 1 Trans-Galactic Drive, 2 Mine Dispenser 40, empty, empty = Layer',
    'Destroyer, 1 Trans-Galactic Drive, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD',
]
ARMOR = {TANK: 3200, CLOAK: 3200, SCOOP: 3200, MIZER: 3200, SHIELD: 3200, LAYER: None, LASERDD: 200}
SHIELDS = {SHIELD: 500}
NOFUEL4 = {SCOOP, MIZER}      # engines with fuel factor 0 at warp 4
SAFE, HIT = {'std': 4, 'heavy': 6, 'bump': 5}, {'std': 3, 'heavy': 10, 'bump': 35}
DMG = {'std': (100, 125), 'heavy': (500, 600), 'bump': (0, 0)}
DMGMIN = {'std': (500, 600), 'heavy': (2000, 2500), 'bump': (0, 0)}

COMMON = ''.join('design %d %d %s\n' % (p, i, d) for p in (0, 1) for i, d in enumerate(DESIGNS)) + \
    'research 0 0\nresearch 1 0\n'


def eff_warp(d):
    for e in range(3, 11):
        if e * e >= d - 1:
            return e
    return 10


def pml(kind, e):
    return max(0, e - SAFE[kind]) * HIT[kind]


def word(dmg, armor):
    """Damage word of a surviving ship: units of 500 of armor, 100% of ships."""
    return dmg * 500 // armor


def hit_damage(kind, stacks, prior=None):
    """stacks: [(design, n)] in slot order -> per design (destroyed?, units/500).
    prior: {design: units} already on 100% of ships."""
    prior = prior or {}
    N = sum(n for _, n in stacks)
    out = []
    for i, (d, n) in enumerate(stacks):
        c = 1 if d in NOFUEL4 else 0
        per, mn = DMG[kind][c], DMGMIN[kind][c]
        extra = 0 if N >= 5 else max(0, mn - per * N)
        D = n * per + (extra if i == 0 else 0)          # one engine per ship
        X = n * ARMOR[d] * prior.get(d, 0) // 500
        tot = X + D - min(D // 2, SHIELDS.get(d, 0) * n)
        avg = tot // n
        out.append((True, None) if avg > ARMOR[d] else (False, word(avg, ARMOR[d])))
    return out


def shrink(count):
    c = count // 20
    if c > 50:
        c = max(50, count // 100)
    return max(10, c)


def planets_in(x, y, count):
    return sorted(n for n, (a, b) in XY.items() if (a - x) ** 2 + (b - y) ** 2 <= count)


def decay(count, planets, kind='std', sd=False, det=False):
    pct = min(50, (1 if sd else 4) * planets + 2) + (25 if det else 0)
    d = max(pct, count * pct // 100)
    if kind != 'bump' and d < 10:
        d = 10
    return 0 if d >= count else count - d


class Run:
    def __init__(self, rid, title, rel01=2, rel10=2, extra=''):
        self.rid, self.title, self.rel01, self.rel10, self.extra = rid, title, rel01, rel10, extra
        self.lines, self.cases, self.fields, self.fleets = [], [], [], []
        self.nfleet = {0: 0, 1: 0}
        self.nfield = {0: 0, 1: 0}

    def fleet(self, owner, x, y, stacks, to=None, warp=9, follow=None, dmg=None, fuel=280, tag=''):
        fid = self.nfleet[owner]
        self.nfleet[owner] += 1
        s = 'fleet %d %d at %d %d ships %s fuel %d' % (owner, fid, x, y, ','.join('%d:%d' % sn for sn in stacks), fuel)
        if dmg:
            s += ' dmg ' + ','.join('%d:%d:100' % du for du in dmg.items())
        if follow is not None:
            tx, ty, tid = follow
            s += ' to %d %d fleet %d warp %d' % (tx, ty, tid, warp)
        elif to is not None:
            s += ' to %d %d warp %d' % (to[0], to[1], warp)
        self.lines.append(s)
        self.fleets.append(dict(owner=owner, id=fid, x=x, y=y, stacks=stacks, to=to, follow=follow, tag=tag,
                                prior=dmg or {}))
        return fid

    def field(self, owner, x, y, count, kind='std', det=False, tag=''):
        n = self.nfield[owner]
        self.nfield[owner] += 1
        self.lines.append('thing minefield %d %d %d %d %d kind %s%s' % (owner, n, x, y, count, kind,
                                                                        ' det' if det else ''))
        self.fields.append(dict(owner=owner, num=n, x=x, y=y, count=count, kind=kind, det=det, tag=tag,
                                planets=planets_in(x, y, count)))
        return n

    def case(self, cid, pred, what, expect, alt='', check=None):
        self.cases.append(dict(id='%s-%s' % (self.rid, cid), pred=pred, what=what, expect=expect, alt=alt,
                               check=check))

    def spec(self):
        head = '# %s: %s (experiments/mf/gen.py)\n' % (self.rid, self.title)
        rel = 'relation 0 1 %d\nrelation 1 0 %d\n' % (self.rel01, self.rel10)
        return head + rel + TECH + COMMON + self.extra + '\n'.join(self.lines) + '\n'


RUNS = []


def run(*a, **k):
    r = Run(*a, **k)
    RUNS.append(r)
    return r


C = (1200, 1200)
BIG = 50000


def rows(n, lo=1131, hi=1269):
    step = (hi - lo) / (n - 1)
    return [int(round(lo + i * step)) for i in range(n)]


def crossing(r, kind, n_p1=24, own=0, design=lambda i: TANK if i % 2 == 0 else CLOAK):
    """Fleets on straight 81-ly east legs at warp 9 through the big field at C."""
    ys = rows(n_p1 + own)
    owners = [1] * (n_p1 + own)
    for k in range(own):                     # spread the own fleets through the rows
        owners[(k * (n_p1 + own)) // own + 1] = 0
    i1 = 0
    for y, o in zip(ys, owners):
        if o == 1:
            r.fleet(1, 1160, y, [(design(i1), 1)], to=(1241, y), tag='p1')
            i1 += 1
        else:
            r.fleet(0, 1160, y, [(TANK, 1)], to=(1241, y), tag='own')


# ------------------------------------------------------------------ MF-1, MF-6: hit rate, cloak, own fleets
r = run('MF-01', 'hit rate per ly in a heavy field, cloak, own fleets (mutual enemies)')
r.field(0, C[0], C[1], BIG, kind='heavy')
crossing(r, 'heavy', own=6)
r.case('A', 'MF-1', '24 player-1 single Tanks (12 with a Super-Stealth Cloak), warp 9, 81-ly legs inside '
       'a player-0 heavy field (e 9, 30 per mille per ly)',
       'per-ly stop rate: 95% interval contains 30 per mille; cloaked and uncloaked alike; '
       'about 22 of 24 stopped', 'one roll per year; 3 or 300 per mille; cloak lowering the odds',
       ('rate', 'heavy', 9, None))
r.case('B', 'MF-9', 'each stopped Tank (1 ship, 1 ordinary engine, 3200 armor)',
       'damage 2000: dmg %d/100%% (cloak no effect), stopped at its message position' % word(2000, 3200), '',
       ('dmg', 'heavy'))
r.case('C', 'MF-6', '6 player-0 Tanks crossing their own heavy field', 'all reach x=1241, no damage', '',
       ('own',))

# ------------------------------------------------------------------ MF-5: relation direction
r = run('MF-05a', 'relation direction: field owner treats the victim as friend', rel01=1, rel10=2)
r.field(0, C[0], C[1], BIG, kind='heavy')
crossing(r, 'heavy')
r.case('A', 'MF-5', 'MF-01 layout; player 0 (field owner) friend to player 1, player 1 enemy to player 0',
       'no player-1 fleet stopped', "the victim's relation decides (hits)", ('nohits',))
r = run('MF-05b', 'relation direction: field owner treats the victim as enemy', rel01=2, rel10=1)
r.field(0, C[0], C[1], BIG, kind='heavy')
crossing(r, 'heavy')
r.case('A', 'MF-5', 'MF-01 layout; player 0 enemy to player 1, player 1 friend to player 0',
       'stops at the MF-1 rate (interval contains 30 per mille)', "the victim's relation decides (no hits)",
       ('rate', 'heavy', 9, None))

# ------------------------------------------------------------------ MF-2: chaser chains
r = run('MF-02', 'follower chains crossing a heavy field (mutual enemies)')
r.field(0, C[0], C[1], BIG, kind='heavy')
for k, y in enumerate(rows(12, 1134, 1266)):
    order = 'ABC' if k < 6 else 'CBA'
    ids = {}
    # ids are given in creation order; a follower needs its target's id, so fill in two steps
    nxt = r.nfleet[1]
    for j, w in enumerate(order):
        ids[w] = nxt + j
    for w in order:
        if w == 'C':
            r.fleet(1, 1180, y, [(TANK, 1)], to=(1261, y), tag='chain-C-' + order)
        elif w == 'B':
            r.fleet(1, 1170, y, [(TANK, 1)], follow=(1180, y, ids['C']), tag='chain-B-' + order)
        else:
            r.fleet(1, 1160, y, [(TANK, 1)], follow=(1170, y, ids['B']), tag='chain-A-' + order)
r.case('A', 'MF-2', '12 chains on one line: C flies 81 ly east at warp 9, B (10 ly behind) follows C, '
       'A (10 ly behind B) follows B; 6 chains numbered A<B<C, 6 numbered C<B<A',
       'C and B stopped at about the MF-1 rate; A never stopped (it moves in warp-4 steps)',
       'A stopped like B (effective warp per year for followers)', ('chain',))

# ------------------------------------------------------------------ MF-3: effective warp from a short leg
r = run('MF-03s', 'effective warp of a short final leg, standard field (mutual enemies)')
r.field(0, C[0], C[1], BIG, kind='std')
ys = rows(36, 1130, 1270)
for i, y in enumerate(ys):
    leg = (17, 26, 81)[i % 3]
    r.fleet(1, 1160, y, [(TANK, 1)], to=(1160 + leg, y), tag='leg%d' % leg)
r.case('A', 'MF-3', '12 Tanks, warp 9, waypoint 17 ly ahead inside a standard field (e 4 = safe)',
       'none stopped', 'waypoint warp 9 used (15 per mille per ly: 23% per fleet)', ('legs', 17, 0))
r.case('B', 'MF-3', '12 Tanks, warp 9, waypoint 26 ly ahead (e 5: 3 per mille per ly, 7.5% per fleet)',
       'rare stops (expected 0.9 of 12)', 'waypoint warp (32% per fleet)', ('legs', 26, 3))
r.case('C', 'MF-3', '12 Tanks, warp 9, 81-ly legs (e 9: 15 per mille per ly)', 'rate interval contains 15',
       '', ('legs', 81, 15))
r = run('MF-03h', 'effective warp of a short final leg, heavy field (mutual enemies)')
r.field(0, C[0], C[1], BIG, kind='heavy')
for i, y in enumerate(rows(24, 1131, 1269)):
    leg = (36, 50)[i % 2]
    r.fleet(1, 1160, y, [(TANK, 1)], to=(1160 + leg, y), tag='leg%d' % leg)
r.case('A', 'MF-3', '12 Tanks, warp 9, waypoint 36 ly ahead inside a heavy field (e 6 = safe)',
       'none stopped', 'waypoint warp (30 per mille per ly: 66% per fleet)', ('legs', 36, 0))
r.case('B', 'MF-3', '12 Tanks, warp 9, waypoint 50 ly ahead (e 7: 10 per mille per ly, 39% per fleet)',
       'rate interval contains 10', 'waypoint warp (78% per fleet)', ('legs', 50, 10))

# ------------------------------------------------------------------ MF-4: which field pays
r = run('MF-04', 'which field loses mines: a small field deep inside a big one (mutual enemies)')
f1 = r.field(0, 1160, 1200, 10000, kind='heavy', tag='F1')
f2 = r.field(0, 1210, 1200, 400, kind='heavy', tag='F2')
for y in range(1195, 1207):
    r.fleet(1, 1190, y, [(TANK, 1)], to=(1271, y), tag='mf4')
r.case('A', 'MF-4', 'player-0 heavy fields F1 10000 at (1160,1200) and F2 400 at (1210,1200); 12 Tanks start '
       'at x=1190 (inside both) and fly 81 ly east at warp 9',
       'every stop is paid by F1 (smallest d^2 - count): F1 -100 per stop; F2 only decays (400 -> 390)',
       'nearest centre or nearest edge: F2 pays (-20) for stops inside F2', ('payer',))

# ------------------------------------------------------------------ MF-7, MF-8, MF-12: detonation, laying order
H, B, S = (1040, 1200), (1070, 1370), (1220, 1050)
r = run('MF-07', 'detonation of heavy, speed-bump and standard fields; laying order (mutual enemies)')
r.field(0, H[0], H[1], 1000, kind='heavy', det=True, tag='H')
r.fleet(1, H[0] + 5, H[1], [(TANK, 1)], tag='H-enemy')
r.fleet(0, H[0] - 5, H[1], [(TANK, 1)], tag='H-own')
r.fleet(0, H[0], H[1] + 5, [(LAYER, 1)], tag='H-layer')
r.case('A', 'MF-7', 'player-0 heavy field 1000 set to detonate (non-SD owner): enemy Tank, own Tank, own '
       'Mini Mine Layer inside', 'both Tanks dmg %d/100%% (2000), layer undamaged, nobody moves; field 730'
       % word(2000, 3200), 'only SD or standard fields detonate; own warships exempt', ('det', 'H'))
r.field(0, B[0], B[1], 1000, kind='bump', det=True, tag='B')
r.fleet(1, B[0] + 5, B[1], [(TANK, 1)], tag='B-enemy')
r.fleet(0, B[0] - 5, B[1], [(TANK, 1)], tag='B-own')
r.case('B', 'MF-7', 'player-0 speed-bump field 1000 set to detonate: enemy Tank and own Tank inside',
       'no damage; field 730 (27%, no minimum 10)', 'damage or a stop', ('det', 'B'))
r.field(0, S[0], S[1], 1000, kind='std', det=True, tag='S')
r.fleet(0, S[0] - 5, S[1], [(LASERDD, 1)], dmg={LASERDD: 250}, tag='S-own-dd50')
r.fleet(1, S[0] + 5, S[1], [(TANK, 5)], dmg={TANK: 250}, tag='S-enemy-5x50')
r.fleet(1, S[0], S[1] + 5, [(TANK, 1)], tag='S-enemy-1')
r.case('C', 'MF-8', 'player-0 standard field 1000 set to detonate: own Laser DD at 50% (dmg 250/500) and '
       'enemy fleet of 5 Tanks at 50%, enemy single Tank',
       'Laser DD destroyed (100 + 500 > 200 armor); 5 Tanks dmg %d/100%% (1600 + 100 each); single Tank '
       'dmg %d/100%% (500); field 730' % (hit_damage('std', [(TANK, 5)], {TANK: 250})[0][1], word(500, 3200)),
       'damage replaces the old damage', ('det', 'S'))
# MF-12: sequential laying, two layers in one field
for tag, (x, y), first in (('L1', (1300, 1250), 'east'), ('L2', (1380, 1050), 'north')):
    r.field(0, x, y, 400, tag=tag)
    pts = {'east': (x + 10, y), 'north': (x, y + 10)}
    for w in (first, 'north' if first == 'east' else 'east'):
        r.fleet(0, pts[w][0], pts[w][1], [(LAYER, 1)], tag='%s-%s' % (tag, w))
        r.lines[-1] += ' task lay'
r.case('D', 'MF-12', 'own standard field 400 (390 after decay) at (1300,1250); layers (160 each) at '
       '+10 east (lower fleet number) then +10 north', 'one field 710 at (1301,1252)',
       'simultaneous merge (1302,1252)', ('fieldat', 0, 1301, 1252, 710))
r.case('E', 'MF-12', 'the same at (1380,1050) with the north layer numbered first',
       'one field 710 at (1382,1051)', 'simultaneous merge (1382,1052)', ('fieldat', 0, 1382, 1051, 710))

r = run('MF-07f', 'detonation hits friends: field owner treats the victim as friend', rel01=1, rel10=2)
r.field(0, H[0], H[1], 1000, kind='heavy', det=True, tag='H')
r.fleet(1, H[0] + 5, H[1], [(TANK, 1)], tag='H-friend')
r.case('A', 'MF-7', 'player-0 detonating heavy field 1000; player 0 friend to player 1; player-1 Tank inside',
       'Tank dmg %d/100%%; field 730' % word(2000, 3200), 'friends exempt', ('det', 'H'))

r = run('MF-07sd', 'SD owner learns the designs its detonation damages', extra='prt 0 5\n')
r.field(0, H[0], H[1], 1000, kind='std', det=True, tag='S')
r.fleet(1, H[0] + 5, H[1], [(SCOOP, 1)], tag='S-enemy-scoop')
r.fleet(1, H[0] - 5, H[1], [(SHIELD, 1)], tag='S-enemy-shield')
r.case('A', 'MF-7', 'SD player 0 detonating standard field 1000 with player-1 Scoop Tank and Shield Tank '
       'inside', "Scoop Tank dmg %d/100%% (600), Shield Tank %d/100%% (250); player 0's .M carries full "
       "designs of both; field 1000 -> 730 (SD: 1*0+2+25 = 27%%)" %
       (word(600, 3200), word(250, 3200)), 'no design learning on detonation', ('det', 'S'))

# ------------------------------------------------------------------ MF-9: damage details
for kind in ('std', 'heavy'):
    r = run('MF-09' + kind[0], 'damage by engine, shield and fleet size, %s field (mutual enemies)' % kind)
    r.field(0, C[0], C[1], BIG, kind=kind)
    mix = [[(TANK, 1)], [(SCOOP, 1)], [(MIZER, 1)], [(SHIELD, 1)], [(TANK, 1), (CLOAK, 1)]]
    for i, y in enumerate(rows(30, 1142, 1258)):
        r.fleet(1, 1160, y, mix[i % 5], to=(1241, y), tag='mix%d' % (i % 5))
    exp = []
    for m, name in zip(mix, ('Tank', 'Scoop Tank (TG Fuel Scoop)', 'Mizer Tank (Fuel Mizer, not a ram scoop)',
                             'Shield Tank (500 shields)', 'Tank + Cloak Tank (2 ships)')):
        exp.append('%s: %s' % (name, '/'.join('%d' % w for _, w in hit_damage(kind, m))))
    r.case('A', 'MF-9', '30 single- and two-ship fleets, warp 9, 81-ly legs through a player-0 %s field' % kind,
           'per stopped fleet, dmg units/500 at 100%: ' + '; '.join(exp),
           'Mizer like the Tank (ram scoops only); shields absorbing all; shortfall split', ('mix', kind))

# ------------------------------------------------------------------ MF-10: merge cap
for rid, count in (('MF-10a', 2100000), ('MF-10b', 1999000)):
    r = run(rid, 'merge cap: own field of %d mines containing a layer' % count)
    r.field(0, C[0], C[1], count, tag='big')
    r.fleet(0, 1100, 1300, [(LAYER, 1)], tag='layer')
    r.lines[-1] += ' task lay'
    after = decay(count, len(planets_in(C[0], C[1], count)))
    if after > 999999:
        r.case('A', 'MF-10', 'own standard field %d (decays to %d, > 999,999) containing a Mini Mine Layer'
               % (count, after), 'a new 160 field at (1100,1300); the big field only decays (and is swept)',
               'merge', ('newfield', 0, 1100, 1300, 160))
    else:
        r.case('A', 'MF-10', 'own standard field %d (decays to %d) containing a Mini Mine Layer' % (count, after),
               'merge: no field at the layer; the big field gains 160', 'a new field', ('nonewfield', 0, 1100, 1300))

# ------------------------------------------------------------------ MF-11: per-player field limit
for rid, n in (('MF-11a', 511), ('MF-11b', 510)):
    r = run(rid, 'per-player minefield limit: %d tiny own fields already exist' % n)
    for i in range(n):
        r.field(0, 1005 + i % 23, 1005 + i // 23, 100, tag='tiny')
    r.fleet(0, 1100, 1300, [(LAYER, 1)], tag='open')
    r.lines[-1] += ' task lay'
    r.fleet(0, 1010, 1010, [(LAYER, 1)], tag='inside')
    r.lines[-1] += ' task lay'
    if n == 511:
        r.case('A', 'MF-11', '511 own standard fields of 100 (numbers 0..510) and a layer in open space',
               'no new field; "failed to lay" message (0x17e) for that layer', 'a new field (no limit)',
               ('limit', True))
    else:
        r.case('A', 'MF-11', '510 own standard fields of 100 and a layer in open space',
               'a new 160 field at (1100,1300)', '', ('limit', False))
    r.case('B', 'MF-11', 'a layer at (1010,1010) inside the tiny fields', 'merges (a tiny field there gains 160)',
           '', ('merge_tiny',))


def main():
    if sys.argv[1:] == ['--list']:
        for r in RUNS:
            print('\n### %s: %s\n' % (r.rid, r.title))
            print('| Case | Prediction | Setup | Predicted | Rules out |\n|---|---|---|---|---|')
            for c in r.cases:
                print('| %s | %s | %s | %s | %s |' % (c['id'], c['pred'], c['what'], c['expect'], c['alt']))
        return
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for r in RUNS:
        open(os.path.join(out, r.rid.lower().replace('-', '') + '.spec'), 'w').write(r.spec())


if __name__ == '__main__':
    main()
