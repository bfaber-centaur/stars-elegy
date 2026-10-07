#!/usr/bin/env python3
"""ES-001 predictions: what the original client should show player 0 for
the generated year, computed from the year's host-file dump with the
public rules (experiments/es001/estimates.py, docs/ESTIMATES.md).

  python3 experiments/es001/predict.py AFTER.DUMP > predictions.tsv

Columns: case, screen, item, prediction. Screens: waypoints (Fleet
Waypoints tile, waypoint selected), range (Fleet Composition "Est.
Range"), production (Production tile "Completion:" of the selected queue
item), research (Research dialog), population (planet population
summary), value (planet report Value column).
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import estimates as E

NAMES = {}      # planet names are read from the screen; rows use numbers


def main(path):
    st = E.parse_dump(path)
    race = E.Race(st['player'])
    rows = []
    for f in st['fleets']:
        fid = 'F%02d' % f['id']
        for i in range(1, len(f['wps'])):
            try:
                tt = E.travel_text(f, i)
            except ValueError as e:
                tt = 'unmodelled: %s' % e
            rows.append((fid + '-w%d' % i, 'waypoints', 'fleet %d wp %d distance' % (f['id'], i),
                         E.distance_text(f, i - 1)))
            rows.append((fid + '-w%d' % i, 'waypoints', 'fleet %d wp %d travel time' % (f['id'], i), tt))
            rows.append((fid + '-w%d' % i, 'waypoints', 'fleet %d wp %d est fuel usage' % (f['id'], i),
                         '%dmg%s' % (E.fuel_to(st, f, i), ' (red)' if E.fuel_to(st, f, i) > f['fuel'] else '')))
        rows.append((fid, 'range', 'fleet %d est. range (fuel %d, ideal warp %d)' % (f['id'], f['fuel'], E.ideal_warp(st, f)),
                     E.est_range(st, f)))
    owned = sorted(n for n, p in st['planets'].items() if p.get('owner') == '0')
    for n in owned:
        pl = E.planet_state(race, st, n)
        q = st['queues'].get(n, [])
        for t, item in enumerate(q):
            first, last = E.production_estimate(race, pl, q, t)
            rows.append(('P%02d-%d' % (n, t), 'production', 'planet %d item %d (id %d x%d, %d%%)' %
                         (n, t, item['id'], item['count'], item['pct']), E.production_text(first, last, item)))
        rows.append(('V%02d' % n, 'value', 'planet %d value / optimal' % n,
                     '%d%% / %d%%' % (pl['hab'], E.opt_value(race, pl['env'], [int(v) for v in st['planets'][n].get('orig', st['planets'][n]['env']).split('/')]))))
        rows.append(('G%02d' % n, 'population', 'planet %d population %d00 of %d00' % (n, pl['P'], pl['max']),
                     E.pop_text(race, pl, 'planet %d' % n)))
        rows.append(('M%02d' % n, 'value', 'planet %d mining rate' % n,
                     '/'.join(str(v) for v in E.mine_estimate(race, pl))))
    need = E.research_needed(race)
    budget = E.projected_budget(race, st, owned)
    allres = sum(E.resources(race, *(lambda p: (p['P'], p['factories'], p['max']))(E.planet_state(race, st, n))) for n in owned)
    rows.append(('R1', 'research', 'resources needed to complete', str(need)))
    rows.append(('R2', 'research', "next year's projected research budget", str(budget)))
    rows.append(('R3', 'research', 'estimated time to completion', E.research_years(race, need, budget)))
    rows.append(('R4', 'research', 'annual resources from all planets', str(allres)))
    rows.append(('R5', 'research', 'total resources spent on research last year', str(race.res_last)))
    print('case\tscreen\titem\tprediction')
    for r in rows:
        print('\t'.join(r))


if __name__ == '__main__':
    main(sys.argv[1])
