# LQ: production-queue edits through the client

Spec: `docs/LIMITS.md` "Production-queue replace" and "LQ". Record:
`docs/PARITY.md` "Production-queue edits through the client".

```sh
tools/fleetlab/combatlab build CB.HST experiments/lq/a.spec a.HST     # CB.HST: Combat Lab base2400
tools/fleetlab/pinned-turn a.HST BASE2400 base-a                      # the base year
tools/fleetlab/client-orders base-a/raw/after OUT experiments/lq/lq-1.cmds
# BASE = base-a/raw/after + OUT/CB.X1
tools/fleetlab/pinned-turn base-a/raw/after/CB.HST BASE run
```

`b.spec` is the 40-item base (LQ-6). LQ-3 starts the host year from
`combatlab build base-a/raw/after/CB.HST r3.spec r3.HST` instead. LQ-0 is
the same year with no order file.
