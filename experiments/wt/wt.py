"""Spec helpers for the WT (wormholes and Mystery Trader) corpus.

A WT run is a Combat Lab start (tools/fleetlab/combatlab build) with
wormholes and Traders inserted as host-file object records (`thing` lines,
docs/ORACLE.md "Universe objects"), generated for one or more years with
the random stream pinned (tools/fleetlab/pinned-turn, tools/fleetlab/years).
experiments/wt/trace.py reads the years back.

Positions use the Combat Lab base game (tiny, 2400; planets as in
experiments/ob/gen.py XY). Player 0 is at tech 26 everywhere, player 1 at
tech 3, so player 1 can still gain from a Trader. Mutual enemies unless a
run says otherwise.
"""
import math

XY = {0: (1045, 1291), 1: (1071, 1087), 2: (1090, 1295), 3: (1129, 1265), 4: (1143, 1103),
      5: (1146, 1180), 6: (1166, 1017), 7: (1166, 1382), 8: (1169, 1145), 9: (1208, 1297),
      10: (1224, 1359), 11: (1243, 1123), 12: (1245, 1158), 13: (1249, 1354), 14: (1268, 1317),
      15: (1281, 1064), 16: (1284, 1383), 17: (1306, 1060), 18: (1324, 1192), 19: (1342, 1123),
      20: (1348, 1290), 21: (1359, 1121), 22: (1368, 1292), 23: (1380, 1295)}

WORMHOLE, TRADER = 2 << 13, 3 << 13      # object id bases (type << 13 | number)

TECH26 = ''.join('tech 0 %s 26\n' % f for f in ('energy', 'weapons', 'prop', 'con', 'elec', 'bio'))

COMMON = """\
relation 0 1 {rel01}
relation 1 0 {rel10}
{tech}research 0 0
research 1 0
# player 0 ship designs (all parts within tech 26)
design 0 0 Scout, 1 Long Hump 6, empty, empty = Scout
design 0 1 Destroyer, 1 Long Hump 6, 1 Laser, 1 Laser, empty, empty, empty, empty = Laser DD
design 0 2 Super Freighter, 3 Long Hump 6, empty, empty, empty = Super Freighter
design 0 3 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
# player 0 starbase designs: 0 = the 2400 homeworld design, unchanged
sbdesign 0 0 Space Station, empty, 8 Laser, 8 Mole-skin Shield, 8 Laser, 8 Mole-skin Shield, 8 Mole-skin Shield, empty, 8 Laser, empty, 8 Laser, empty, 8 Mole-skin Shield = Starbase
# player 1 ship designs (tech 3)
design 1 0 Medium Freighter, 1 Long Hump 6, empty, empty = Freighter
design 1 1 Scout, 1 Long Hump 6, empty, empty = Scout
plan 0 0 4 1 0 1 = Enemies
"""


class Run:
    """One spec. Cases record what each placement is for; predictions are
    added by the batch generator, never here."""

    def __init__(self, rid, title, rel01=2, rel10=2, tech=TECH26, extra=''):
        self.rid, self.title = rid, title
        self.rel01, self.rel10, self.tech, self.extra = rel01, rel10, tech, extra
        self.lines, self.cases = [], []
        self.nfleet = {0: 0, 1: 0}
        self.nworm = 0
        self.ntrader = 0

    # ---- fleets
    def fleet(self, owner, x, y, ships, plan=0, fuel=50, extra=''):
        fid = self.nfleet[owner]
        self.nfleet[owner] += 1
        self.lines.append('fleet %d %d at %d %d ships %s plan %d fuel %d %s'
                          % (owner, fid, x, y, ships, plan, fuel, extra))
        return fid

    # ---- wormholes
    def pair(self, a, b, cls=(0, 0), years=(0, 0), seen=(0, 0), seen2=(0, 0), extra=('', '')):
        """A wormhole pair: ends at a and b, each with its class (0..3), years
        since its last jump (0..1023) and the two player masks. Returns the
        two object ids, for `to X Y thing ID` waypoints."""
        n = self.nworm
        self.nworm += 2
        for k, (x, y) in enumerate((a, b)):
            self.lines.append('thing wormhole %d %d %d %d %d years %d seen %#x seen2 %#x %s'
                              % (n + k, x, y, n + 1 - k, cls[k], years[k], seen[k], seen2[k], extra[k]))
        return WORMHOLE | n, WORMHOLE | (n + 1)

    def enter(self, owner, start, worm_id, worm_xy, warp, ships='0:1', fuel=200, extra=''):
        """A fleet at `start` whose waypoint 1 is the wormhole (waypoint type
        0x18, an object target)."""
        return self.fleet(owner, start[0], start[1], ships, fuel=fuel,
                          extra='to %d %d thing %#x warp %d %s' % (worm_xy[0], worm_xy[1], worm_id, warp, extra))

    # ---- Mystery Trader
    def trader(self, at, dest, warp, met=0, item=0, extra=''):
        """A Trader at `at` heading for `dest` (its heading is the line from
        at to dest) at `warp`. Returns its object id."""
        n = self.ntrader
        self.ntrader += 1
        self.lines.append('thing trader %d %d %d %d %d %d met %#x item %#x %s'
                          % (n, at[0], at[1], dest[0], dest[1], warp, met, item, extra))
        return TRADER | n

    def meet(self, owner, trader_end, back, warp, ships, cargo, fuel=2000):
        """Stage a meeting: a fleet `back` ly west of where the Trader is
        expected to end its move (`trader_end`, a prediction the caller
        supplies), flying onto that point at `warp` (warp² >= back so it
        arrives this year). OB-004 measured that a stationary fleet at the
        Trader does not trade, so the fleet always moves."""
        assert warp * warp >= back, 'the meeting fleet must arrive this year'
        x, y = trader_end
        return self.fleet(owner, x - back, y, ships, fuel=fuel,
                          extra='cargo %s to %d %d warp %d' % (cargo, x, y, warp))

    # ---- bookkeeping
    def case(self, cid, what, prediction='', alt='', check=None):
        self.cases.append(dict(id='%s-%s' % (self.rid, cid), what=what, prediction=prediction, alt=alt,
                               check=check))

    def spec(self):
        head = '# %s: %s (experiments/wt)\n' % (self.rid, self.title)
        return head + COMMON.format(rel01=self.rel01, rel10=self.rel10, tech=self.tech) + self.extra + \
            '\n'.join(self.lines) + '\n'


def axis_move(at, dest, warp):
    """End of an axis-aligned Trader move of warp² ly toward dest (OB-004:
    warp 8 moved 64 ly east, before fleets move). Only for staging; the
    diagonal rounding is a decomp prediction."""
    (x, y), (dx, dy) = at, dest
    assert x == dx or y == dy, 'axis-aligned headings only'
    step = warp * warp
    if y == dy:
        return (x + max(-step, min(step, dx - x)), y)
    return (x, y + max(-step, min(step, dy - y)))


def dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])
