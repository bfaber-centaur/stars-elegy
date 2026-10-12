#!/usr/bin/env python3
"""A waypoint aimed at another player's fleet, in the host file and in the
owner's file (WF-01..WF-03).

  experiments/wf/gen.py OUTDIR      # writes OUTDIR/<name>/spec.txt

Combat Lab base (game CB), unarmed Scouts (design 1, fuel tank) in deep space.
Player 0's fleet 0 has waypoint 1 aimed at player 1's fleet 0, which flies
south at warp 5. Player 0's fleet 1 has waypoint 1 aimed at its own fleet 2,
which also flies south (control). Two years: year 2 runs on year 1's host
file unchanged.
Predictions and results: experiments/wf/README.md.
"""
import os, sys

FLEETS = ('fleet 0 0 at 1100 1230 ships 1:1 fuel 300 to 1200 1230 fleet 1 0 warp 5\n'
          'fleet 1 0 at 1200 1230 ships 1:1 fuel 300 to 1200 1400 warp 5\n'
          'fleet 0 1 at 1100 1180 ships 1:1 fuel 300 to 1200 1180 fleet 0 2 warp 5\n'
          'fleet 0 2 at 1200 1180 ships 1:1 fuel 300 to 1260 1340 warp 5\n'
          'queue 17 none\nqueue 8 none\n')
SPECS = {'wf-enemy': 'relation 0 1 2\nrelation 1 0 2\n' + FLEETS,
         'wf-friend': 'relation 0 1 1\nrelation 1 0 1\n' + FLEETS}

if __name__ == '__main__':
    for name, spec in SPECS.items():
        os.makedirs(os.path.join(sys.argv[1], name), exist_ok=True)
        with open(os.path.join(sys.argv[1], name, 'spec.txt'), 'w') as f:
            f.write(f'# {name} (experiments/wf/gen.py)\n' + spec)
