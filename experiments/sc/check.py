#!/usr/bin/env python3
"""Compare an SC- run with its predictions.

  experiments/sc/check.py RUN CB.XY AFTER.DUMP [TURN]

RUN is a gen.py run name (sc001 ...). AFTER.DUMP is `combatlab dump` of the
after-turn files (pinned-turn writes it). Prints one line per case
(OK / MISMATCH), then every difference between the model's full view and the
observed .M view for both players, then a summary line.

Observed planet levels: a model level 2 (starbase hidden) must appear as
level 3 with the starbase bit clear; a model level 3 for a planet with a
starbase must carry the starbase bit.
"""
import sys
import gen
from sclib import planets_xy, observed


def planet_obs(view, pid):
    return view.get(('planet', pid), 0), view.get(('sbbit', pid), False)


def planet_ok(g, lvl, obs, pid):
    olvl, osb = obs
    if lvl == 2:
        return olvl == 3 and not osb
    if lvl == 3 and pid in g.sb:
        return olvl == 3 and osb
    return olvl == lvl


def main():
    run, xy, dump = sys.argv[1:4]
    turn = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    pxy = planets_xy(xy)
    g = gen.RUNS[run](pxy)
    views = observed(open(dump).read(), turn)
    bad = 0
    for cid, v, key, lvl, claims, diff, note in g.cases:
        view = views.get(v, {})
        if key[0] == 'planet':
            obs = planet_obs(view, key[1])
            ok = planet_ok(g, lvl, obs, key[1])
            got = 'L%d%s' % (obs[0], ' sb' if obs[1] else '')
        else:
            got = view.get(key, 0)
            ok = got == lvl
            if ok and lvl == 4:   # pick-pocket view: cargo must match the fleet's
                f = [f for f in g.fleets if (f.owner, f.id) == key[1:]][0]
                c = view.get(('cargo',) + key[1:])
                ok = c == tuple(f.cargo)
                got = '%d cargo %s' % (got, c)
            if ok and lvl == 3:
                c = view.get(('cargo',) + key[1:])
                ok = not c or not any(c)
        bad += not ok
        print('%-8s %-28s viewer %d %-12s expected %d got %-14s %s [%s] alt-differ: %s' % (
            'OK' if ok else 'MISMATCH', cid, v, '%s %s' % (key[0], '/'.join(map(str, key[1:]))), lvl, got,
            note, ','.join(claims), ','.join(diff) or '-'))
    # full view comparison
    extra = 0
    for v in (0, 1):
        model = g.predict(v)
        view = views.get(v, {})
        keys = {k for k in list(model) + list(view) if k[0] in ('fleet', 'planet')}
        for k in sorted(keys, key=str):
            if k[0] == 'planet':
                if g.owned.get(k[1]) == v:
                    continue
                if not planet_ok(g, model.get(k, 0), planet_obs(view, k[1]), k[1]):
                    extra += 1
                    print('VIEW-DIFF player %d planet %d model %d observed %s' % (v, k[1], model.get(k, 0),
                                                                             planet_obs(view, k[1])))
            elif k[1] != v and model.get(k, 0) != view.get(k, 0):
                extra += 1
                f = [f for f in g.fleets if (f.owner, f.id) == k[1:]]
                print('VIEW-DIFF player %d fleet %d/%d model %d observed %d %s' % (
                    v, k[1], k[2], model.get(k, 0), view.get(k, 0), f[0].tag if f else ''))
    print('%s: %d cases, %d mismatches, %d other view differences' % (run, len(g.cases), bad, extra))
    return 1 if bad or extra else 0


if __name__ == '__main__':
    sys.exit(main())
