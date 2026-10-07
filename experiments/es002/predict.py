#!/usr/bin/env python3
"""ES-002 predictions from the generated year's host-file and .XY dumps
(experiments/es001/estimates.py, docs/ESTIMATES.md).

  (combatlab dump CB.HST; combatlab dump CB.XY) > after.dump
  python3 experiments/es002/predict.py after.dump [m1.dump] > predictions.tsv

m1.dump (optional, `combatlab dump CB.M1` of the generated year) gives
the planets player 0's report lists. predictions.tsv was made without it,
which treated every unowned planet as reported; that missed G8 (F07,
T07). With it the model gives "Uncertain" there (results in check.py).

Player 0: every waypoint's distance, travel time (stargate legs
included), est. fuel usage; fleet report ETA; production completion;
research dialog (Generalized Research). Player 1: research dialog for its
current field, and "Maxed Out" for energy.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'es001'))
import estimates as E

FIELDS = ('energy', 'weapons', 'prop', 'con', 'elec', 'bio')


def research_rows(st, race, owner, tag):
    owned = sorted(n for n, p in st['planets'].items() if p.get('owner') == str(owner))
    need = E.research_needed(race)
    budget = E.projected_budget(race, st, owned)
    allres = sum(E.resources(race, p['P'], p['factories'], p['max'])
                 for p in (E.planet_state(race, st, n) for n in owned))
    f = FIELDS[race.field]
    return [
        (tag + '1', 'research', 'player %d field %s level %d -> resources needed' % (owner, f, race.tech[race.field]),
         'Maxed Out' if need is None else str(need)),
        (tag + '2', 'research', "player %d next year's projected research budget" % owner, str(budget)),
        (tag + '3', 'research', 'player %d estimated time to completion%s' % (owner, ' (GR)' if race.lrt & 16 else ''),
         E.research_years(race, need, budget)),
        (tag + '4', 'research', 'player %d annual resources from all planets' % owner, str(allres)),
    ]


def reported(path):
    """Planet ids in the last .M file block of a combatlab dump."""
    seen = set()
    for line in open(path, encoding='latin-1'):
        b = line.split(' ', 1)[1]
        if b.startswith('file '):
            seen = set()
        elif b.startswith('seen planet ') or b.startswith('planet '):
            seen.add(int(b.split()[1 if b.startswith('planet ') else 2]))
    return seen


def main(path, mpath=None):
    rows = []
    st = E.parse_dump(path, 0)
    if mpath:
        st['reported'] = reported(mpath)
    for line in open(path, encoding='latin-1'):      # .XY positions
        b = line.split(' ', 1)[1]
        if b.startswith('xy planet '):
            p = b.split()
            st['xy'][int(p[2])] = (int(p[3][2:]), int(p[4][2:]))
    race = E.Race(st['player'])
    for f in st['fleets']:
        fid = 'F%02d' % f['id']
        for i in range(1, len(f['wps'])):
            rows.append((fid + '-w%d' % i, 'waypoints', 'fleet %d wp %d distance' % (f['id'], i),
                         E.distance_text(f, i - 1)))
            rows.append((fid + '-w%d' % i, 'waypoints', 'fleet %d wp %d travel time' % (f['id'], i),
                         E.travel_text(f, i, st=st)))
            fu = E.fuel_to(st, f, i)
            rows.append((fid + '-w%d' % i, 'waypoints', 'fleet %d wp %d est fuel usage' % (f['id'], i),
                         '%dmg%s' % (fu, ' (red)' if fu > f['fuel'] else '')))
        if len(f['wps']) > 1:
            rows.append(('T%02d' % f['id'], 'report', 'fleet %d report ETA' % f['id'],
                         E.travel_text(f, 1, short=True, st=st)))
    for n in sorted(st['queues']):
        if st['planets'].get(n, {}).get('owner') != '0':
            continue
        pl = E.planet_state(race, st, n)
        q = st['queues'][n]
        for t, item in enumerate(q):
            first, last = E.production_estimate(race, pl, q, t)
            rows.append(('P%02d-%d' % (n, t), 'production', 'planet %d item %d (id %d x%d, %d%%)' %
                         (n, t, item['id'], item['count'], item['pct']), E.production_text(first, last, item)))
    rows += research_rows(st, race, 0, 'R')
    st1 = E.parse_dump(path, 1)
    race1 = E.Race(st1['player'])
    rows += research_rows(st1, race1, 1, 'S')
    e = race1.field
    race1.field = 0
    rows.append(('S5', 'research', 'player 1 energy (level %d) selected: resources needed' % race1.tech[0],
                 'Maxed Out' if E.research_needed(race1) is None else str(E.research_needed(race1))))
    race1.field = e
    print('case\tscreen\titem\tprediction')
    for r in rows:
        print('\t'.join(r))


if __name__ == '__main__':
    main(*sys.argv[1:3])
