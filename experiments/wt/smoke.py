#!/usr/bin/env python3
"""WT-000: tooling smoke run (no predictions). Shows that the WT helpers
place wormhole pairs, a transit, a damaged fleet in transit, two Traders
(axis-aligned and diagonal) and a staged Trader meeting, and that
tools/fleetlab/years + trace.py follow them over three years.

  python3 experiments/wt/smoke.py OUTDIR      # writes OUTDIR/wt000.spec
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wt import Run, axis_move

r = Run('WT-000', 'tooling smoke: wormholes, transit, Traders, a meeting (three years)')
w0, w1 = r.pair((1050, 1180), (1290, 1240), cls=(0, 0))
r.enter(0, (1050, 1210), w0, (1050, 1180), 6)                       # scout, 30 ly, arrives year 1
r.case('A', 'scout enters a class-0 wormhole 30 ly away at warp 6')
w2, w3 = r.pair((1080, 1360), (1360, 1040), cls=(3, 3), years=(200, 200))
r.enter(0, (1080, 1340), w2, (1080, 1360), 5, ships='1:2', extra='', fuel=300)
r.lines[-1] = r.lines[-1].replace('fuel 300', 'fuel 300 dmg 1:100:50')
r.case('B', 'two damaged Laser DDs enter a class-3, 200-year wormhole 20 ly away')
start, dest = (1010, 1210), (1395, 1210)
r.trader(start, dest, 8)
end = axis_move(start, dest, 8)
r.meet(1, end, 20, 5, '0:24', '5000 0 0 0')
r.case('C', 'Trader heading east at warp 8; player 1 freighters with 5000 kT fly onto its end point')
r.trader((1395, 1010), (1005, 1390), 9)
r.case('D', 'Trader heading south-west at warp 9 (diagonal path)')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    open(os.path.join(out, 'wt000.spec'), 'w').write(r.spec())
    print('wrote %s/wt000.spec' % out)
