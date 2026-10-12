#!/usr/bin/env python3
"""Fleet numbering after a fleet leaves during the year (FN-01..FN-05).

  experiments/fn/gen.py OUTDIR      # writes OUTDIR/<name>/spec.txt and OUTDIR/<name>/year2.txt

Combat Lab base (game CB). Player 1 (homeworld planet 8) owns fleets 1 and 2
at planet 8 and, in each variant but the control, a fleet 0 that leaves
before production. Planet 8 builds two Scouts. year2.txt queues one more
Scout on the year-1 result (keepfleets).
Predictions and results: experiments/fn/README.md.
"""
import os, sys

COMMON = ('planet 8 owner 1 pop 1000 starbase 0\n'
          'planetset 8 env=50,50,50 factories=100 fe=20000 bo=20000 ge=20000\n'
          'queue 8 0:1:2,0:1:2\nqueue 17 none\n'
          'fleet 0 0 planet 17 at 1306 1060 ships 1:1 fuel 300\n'
          'fleet 1 1 planet 8 at 1169 1145 ships 1:1 fuel 300\n'
          'fleet 1 2 planet 8 at 1169 1145 ships 1:1 fuel 300\n')
FLEET0 = {
    'fn-ctl': '',
    # waypoint-0 colonize, in orbit of unowned planet 5 (step 2, before movement)
    'fn-colonize': 'fleet 1 0 planet 5 at 1146 1180 ships 2:1 fuel 200 cargo 0 0 0 25 task colonize\n',
    # colonize on arrival: 10 ly from planet 5, so the task runs after movement (still before production)
    'fn-colonize-arrive': 'fleet 1 0 at 1146 1190 ships 2:1 fuel 200 cargo 0 0 0 25 to 1146 1180 planet 5 warp 5 task colonize\n',
    # waypoint-0 scrap at its own starbase planet (step 2)
    'fn-scrap': 'fleet 1 0 planet 8 at 1169 1145 ships 1:1 fuel 300 task scrap\n',
    # waypoint-0 merge into fleet 1 (step 2, load tasks)
    'fn-merge': 'fleet 1 0 planet 8 at 1169 1145 ships 1:1 fuel 300 target fleet 1 1 task merge\n',
}
YEAR2 = 'keepfleets\nqueue 8 0:1:2\nqueue 17 none\n'

if __name__ == '__main__':
    for name, f0 in FLEET0.items():
        d = os.path.join(sys.argv[1], name)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'spec.txt'), 'w') as f:
            f.write(f'# {name} (experiments/fn/gen.py)\n' + COMMON + f0)
        with open(os.path.join(d, 'year2.txt'), 'w') as f:
            f.write(f'# {name} year 2 (experiments/fn/gen.py)\n' + YEAR2)
