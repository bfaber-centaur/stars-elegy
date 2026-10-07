# Stars! J-RC3 Oracle

The oracle is the original Stars! J-RC3, run headlessly, so experiments can be
carried out against it and compared with Elegy:

```text
Xvfb → DOSBox → Windows 3.1 → Stars! J-RC3
        ↑ xdotool (keys, mouse)    ↓ screenshots, files on the Linux side
```

All control goes through `scripts/oracle/`. The proprietary apparatus stays
outside the repository, under `$ORACLE_HOME` (default `~/.stars-oracle`).

## Evidence levels used in this document

- **Observed:** seen directly in a screenshot, a decoded file header, or
  command output. The number of runs is given where it matters.
- **Inferred:** a conclusion drawn from observations, which could still be
  wrong.
- **Hypothesis:** plausible, but not tested here.
- **Documented:** taken from external documentation or prior art (e.g.
  StarsAPI), not checked here.

Unlabeled procedural text ("run X, then Y") describes the harness itself.

## Status

All observations below are from 2026-10-06, with the StarsBox +
`stars_games` apparatus described below.

| Capability | Evidence |
|---|---|
| Xvfb + DOSBox start/stop unattended | Observed, many runs. |
| Windows 3.1 boots; Stars! starts from autoexec | Observed, many runs. Measured once at about 3 s from `start` to the first Stars! dialog. |
| Full-window screenshots (1152x864 guest) | Observed. |
| Keyboard input reaches Windows and Stars! | Observed (keys listed under [Keyboard](#keyboard)). |
| Mouse click and double-click reach the intended target | Observed for 2 targets: a Program Manager menu and an icon. Positional accuracy is under [Mouse](#mouse). |
| Pristine → run copy → snapshot → reset | Observed (`selftest`, and real resets between runs). |
| Header decode of real game files | Observed (`files` on `stars_games`). |
| Serial accepted | Observed: the dialog closed after `register`, and Stars! started with no serial prompt from the `registered` snapshot (3 boots). |
| PG001 loads from D: | Observed: title "A Barefoot JayWalk — pg000 — pg001.m1", year 2407, Endeavor population 48,600. |
| One turn generated; change visible from Linux | Observed, 3 runs: see [One PG001 turn](#one-pg001-turn-observed). |
| Growth is not the halved-growth penalty | Observed: 48,600 → 53,500 (penalty predicts 51,100). Read from the UI in runs 1 and 2; not read in run 3. |
| Same UI result across runs | Observed for runs 1 and 2, both from the same `registered` snapshot. Output files differ byte-wise (see below). |

That the oracle now has "normal registered behavior" is **inferred** from
two things: the serial was accepted, and the growth matches the
non-penalized PG-001 value. The About dialog shows the version (2.60j) but
neither a registrant nor an "unregistered" marker, so it neither confirms
nor refutes registration. Only one mechanic (uncrowded growth on one planet)
has been compared with a known value.

## Required apparatus (not in Git)

- `starsbox-macapp.tar.gz`: the macOS `StarsBox.app`. Only its DOS/Windows
  payload is used: `Contents/Resources/c_drive` (Windows 3.1 in `WINDOWS`,
  Stars! in `STARS`, Stars! Notebook in `NOTEBOOK`). The bundled macOS DOSBox
  binary and config are not used.
- `stars_games.tar.gz`: historical game files (`PG000.*`, `PG001.*`,
  `TESTSSG1.*`, `TEST_SS.R1`, `BACKUP/`).
- The Stars! serial number. It is entered into Stars!' first-run dialog, and
  must never be written into the repository, logs, docs, or PRs.

The PG-002 run (2026-10-06) registered by hand, using the manual steps
below: archives from a checkout of the apparatus repository, and the serial
from `STARS_SERIAL`, written without printing to a mode-0400 file under
`$ORACLE_HOME`. That predates `bootstrap` (see Durable setup); the hook was
not exercised by that session.

Never commit any of these, or screenshots that show registration details or
proprietary UI unless clearly safe. Raw game files, screenshots and recorder
logs produced by experiments are evidence: preserve them in the private
apparatus repository under `evidence/<experiment-id>/` (see `CLAUDE.md`,
"Preserving raw experiment evidence"), not here.

Linux packages (installed by the environment setup script): `dosbox` 0.74-3,
`xvfb`, `xdotool`, `imagemagick`, `x11-utils`, `unzip`, `p7zip-full`, plus Go.

## Layout

```text
$ORACLE_HOME/
├── oracle.conf          local configuration (see scripts/oracle/oracle.conf.example)
├── sources/             optional read-only copies of the supplied archives
├── sources.txt          SHA-256 of the archives setup was run from
├── pristine/            unpacked apparatus, read-only
│   ├── StarsBox.app/…/c_drive    → mounted as C:
│   └── games/stars_games         → mounted as D:
├── pristine.sha256      manifest of pristine/
├── run/                 disposable copy that DOSBox actually uses
├── snapshots/NAME/      saved run copies, read-only
├── refs/                local reference crops for wait-for (proprietary UI; keep out of Git)
├── state/               pid files, logs, generated DOSBox config
└── shots/               screenshots
```

Read-only bits guard against accidents, not against root, and the container
runs as root. The archives themselves are the real source of truth, and
`setup --force` rebuilds `pristine/` from them.

## Durable setup (cloud sessions)

Cloud sessions start on a fresh machine, so nothing under `$ORACLE_HOME`
survives between sessions. Instead, the oracle is rebuilt from three
durable inputs. None of them is in this repository:

1. **Apparatus archives** `starsbox-macapp*.tar.gz` and `stars_games*.tar.gz`,
   kept in the private repository `bfaber-centaur/stars-oracle-apparatus`
   (with the owner's apparatus notes; never make it public). Add that
   repository to the cloud environment's repositories, so sessions clone it
   next to this one. `bootstrap` looks for the archives in order:
   - its argument;
   - `$ORACLE_APPARATUS_DIR`;
   - a checkout named `stars-oracle-apparatus` next to this repository (where
     a session cloning that repo as a second source would put it);
   - a shallow clone of `$ORACLE_APPARATUS_GIT`.
2. **The serial**, in the environment variable `STARS_SERIAL`, set in the
   cloud environment's settings. Every session in that environment can read
   it. Scripts never print it.
3. **This repository's** scripts and `.claude/hooks/session-start.sh`.

`scripts/oracle/bootstrap` does setup → reset → start → register → exit
Stars! → stop → `snapshot registered` → `reset registered`. It creates the
two `wait-for` reference crops from the live screen, detecting each screen
by counts of exact pixel colours in a fixed region. The colours and counts
are in the script; the crops stay local. If the `registered` snapshot
already exists, it only resets to it.

The SessionStart hook (`.claude/settings.json` → `.claude/hooks/session-start.sh`)
runs `bootstrap` in cloud sessions only (`CLAUDE_CODE_REMOTE=true`). It
writes the log to `$ORACLE_HOME/bootstrap.log` and prints one line. It never
fails the session: with inputs missing, it reports what is missing and exits 0.

Observed on 2026-10-06, with `STARS_SERIAL` set:
- a fresh clone of `stars-oracle-apparatus` from GitHub had archives
  byte-identical (SHA-256) to the originally supplied ones;
- with that repository checked out at `/home/user/stars-oracle-apparatus`
  and no `ORACLE_APPARATUS_*` variables, the hook found it on its own and
  built the `registered` snapshot in an empty `ORACLE_HOME`;
- with archives from a local directory, and separately from a local git
  repository via `ORACLE_APPARATUS_GIT`:
  - a fresh `ORACLE_HOME` was bootstrapped in about 9 s (local directory);
  - the generated crops were pixel-identical to hand-made ones;
  - the resulting snapshot started Stars! without a serial prompt, and
    `turn PG001.M1` advanced the header from 7 / 2407 to 8 / 2408;
  - a second hook run only reset (under 1 s).

Observed at the start of a real new cloud session (2026-10-06), with the
apparatus repository cloned next to this one and `STARS_SERIAL` set, before
the session ran any command of its own:
- `$ORACLE_HOME/bootstrap.log` was written between 22:59:50Z and 23:00:04Z
  (about 14 s) and ended with
  `bootstrap: done; registered snapshot saved and run copy reset to it`;
- the archives it hashed (`sources.txt`) were
  `starsbox-macapp.tar.gz` `662a8ed45de5d1dcb69dc2bfb3788fc4082435e10d8b10bbe713f1eebe8cd35e`
  and `stars_games.tar.gz` `0153fb07550799b4e7083cb94cd7d544c9f97b9568d63f117427fef0c314e861`;
- `selftest` passed, and from the `registered` snapshot `turn PG001.M1`
  advanced the header from 7 / 2407 to 8 / 2408 with no serial prompt.

## Configure and initialize (by hand)

```sh
mkdir -p ~/.stars-oracle/sources
cp /path/to/starsbox-macapp.tar.gz /path/to/stars_games.tar.gz ~/.stars-oracle/sources/
chmod a-w ~/.stars-oracle/sources/*
cp scripts/oracle/oracle.conf.example ~/.stars-oracle/oracle.conf   # already set up for StarsBox

scripts/oracle/setup --bundle ~/.stars-oracle/sources/starsbox-macapp.tar.gz \
    --drive ~/.stars-oracle/sources/stars_games.tar.gz --drive-dest games
scripts/oracle/reset
```

The generated DOSBox config mirrors the original macOS launcher:

```text
[dosbox] machine=svga_s3  memsize=30
[autoexec]
mount c "<run>/StarsBox.app/Contents/Resources/c_drive"
mount d "<run>/games/stars_games"
c:
set PATH=C:\WINDOWS;C:\STARS;C:\NOTEBOOK
d:
win /n stars.exe
```

Mount paths are absolute and point into the run copy. Game files stay on D:,
separate from the application drive. Headless overrides set no audio devices,
`output=surface`, `scaler=none`, and `autolock=false`. `cycles=max` replaces
the original `cycles=auto`. No problem attributable to it has been observed,
but no comparison with `cycles=auto` has been made either.

The original `stars_dosbox_macos.conf` targets an SDL2 DOSBox build
(`output=texture`, an SDL2 mapper file), so it is a reference and is not
loaded.

### Deliberate deviation from pristine

At each `start`, if `ORACLE_MOUSE_NOACCEL=1` (the default), `MouseSpeed=0` is
added to the `[windows]` section of the **run copy's** `WINDOWS/WIN.INI`, to
turn off Windows pointer acceleration for `click`.

- *Hypothesis:* this affects only cursor movement, not anything Stars!
  computes. It has not been tested, e.g. by comparing turn results with and
  without it.
- *Observed:* `status` reports `WIN.INI` as modified because of this. After
  any boot it also reports `WINDOWS/WIN386.SWP` as modified, and, after
  Stars! has run once, `WINDOWS/STARS.INI` as added.

## Start, observe, operate, stop

```sh
scripts/oracle/start                  # Xvfb + DOSBox, detached; waits for the window
scripts/oracle/status                 # processes, window title, changes vs pristine
scripts/oracle/screenshot [OUT.png]   # prints the PNG path
scripts/oracle/wait-stable [TIMEOUT] [QUIET]   # waits until the screen stops changing
scripts/oracle/wait-for REF.png X Y [TIMEOUT]  # waits until REF appears at X,Y
scripts/oracle/key alt+f Down Return  # xdotool keysyms, sent in order
scripts/oracle/type 'text'            # literal text, no Return
scripts/oracle/click X Y [BUTTON] [--double]   # guest coordinates from a screenshot
scripts/oracle/register [SERIAL_FILE] # type the serial ($STARS_SERIAL by default) into the first-run dialog
scripts/oracle/bootstrap [DIR]        # fresh machine → registered snapshot (see Durable setup)
scripts/oracle/turn GAME.M1           # open a game, press F9 once, exit Stars!
scripts/oracle/stop
```

Screenshots capture the DOSBox window alone, at the guest resolution
(1152x864 with this Windows install). Screenshot pixel coordinates are guest
coordinates.

`start` pins the window at the screen origin (`SDL_VIDEO_WINDOW_POS=0,0`) on
a 1600x1200 Xvfb screen. *Observed:* without this, the window opened at
+192+184 (and +480+400 on a larger screen) and was clipped once Windows
switched to 1152x864.

### Waiting

- *Observed:* the Stars! title screen animates, and `wait-stable` timed out
  while it was visible. Use `wait-for` with a reference crop of the expected
  screen instead. `bootstrap` creates both crops below automatically; by
  hand, make them from a screenshot:
  - `convert shot.png -crop 290x16+440+344 +repage ~/.stars-oracle/refs/serial-dialog-title.png`
    is the title bar of the "Stars! Serial Number" dialog;
  - `convert shot.png -crop 130x20+367+802 +repage ~/.stars-oracle/refs/main-menu-open.png`
    is the "Open Game..." button of the title screen.
- `wait-stable` has worked on Program Manager and the Stars! map view.

### Keyboard

Keys go to the focused DOSBox window, and each script focuses it first.
Observed in this setup:

| Keys | Effect |
|---|---|
| `Escape` on the serial dialog | cancels; Stars! exits to Program Manager |
| `alt+o` on the title screen | Open Game dialog, directory `d:\` |
| type `pg001.m1`, `Return` in that dialog | loads PG001 |
| `alt+t` | Turn menu: "Wait for New", "Generate F9" |
| `g` in the Turn menu (run 1), or `F9` (runs 2–3) | generates a turn |
| `alt+h` `a` | About Stars! dialog; `Return` there opened "Order Info..." (the default button), and two `Escape`s closed both dialogs |
| `alt+f` `x` | File → Exit, back to Windows |
| `alt+x` on the title screen | exits Stars! |

### Mouse

Measurements with DOSBox 0.74-3 and this Windows 3.1 install, finding the
cursor by diffing screenshots:

- **Unlocked** (DOSBox's state after `start`): with slow 1–3 px host steps,
  the guest cursor moved about 0.56× the host distance horizontally and
  about 0.23× vertically. *Hypothesis:* DOSBox scales motion to a 640x200
  range (640/1152 ≈ 0.556, 200/864 ≈ 0.231).
- **Locked** (DOSBox hotkey `ctrl+F10`), with Windows acceleration on:
  2 px steps 10 ms apart landed exactly in 4 of 4 probes in one session,
  but overshot by 4 px in a later session. Faster pacing overshot by about
  2×.
- **Locked, with `MouseSpeed=0`**, at `click`'s default pacing (8 px steps,
  5 ms apart): (47,31), (600,400), and (777,123) measured exactly. (1000,800)
  measured (999,799), and (5,5) measured (0,0). *Inferred, not confirmed:*
  the last two are artefacts of the diff method near the cursor's outline
  and the screen corner. No other pacing was measured with acceleration
  off.

`click` locks the mouse the first time it runs after `start` (tracked in
`state/mouse-locked`). It parks the host pointer at the bottom-right of the
X screen, sweeps the guest cursor past the top-left corner, walks to (X,Y),
and clicks. It took about 1 s per click. Functional checks: one click opened
Program Manager's File menu, and one double-click on the Stars! icon
launched Stars!. Check positions with a screenshot before relying on
clicks near small targets.

Don't send `ctrl+F10` by hand. It would toggle the lock out of sync with
`state/mouse-locked`.

## Game files

Stars! writes game files to D:, i.e. `run/games/stars_games`, and they were
visible from Linux as soon as Stars! finished. DOSBox caches directory
listings (documented DOSBox behavior), so make Linux-side changes to the run
copy only while the oracle is stopped.

```sh
scripts/oracle/status   # added / modified / deleted relative to pristine
scripts/oracle/files    # every .HST/.Mn/.Xn/.Hn/.XY in run/, with decoded headers
go run ./cmd/stars-header FILE...                     # the same decode for arbitrary files
go run ./cmd/stars-record -watch DIR -out DIR         # archive every distinct .HST state
```

Only the plaintext file header (game ID, version, turn, year, player, flags)
is decoded today. The rest of each file is not decoded by Elegy.
*Documented (StarsAPI):* the rest is encrypted, with a key seeded from the
header's salt and game ID.

Pristine `stars_games` headers (observed with `scripts/oracle/files`; "turn
N / year" is the header's turn field and the year derived from it):

| Game | ID | Files |
|---|---|---|
| PG001 | 92584875 | `.HST` 7 / 2407, `.M1` 7 / 2407, `.H1` 6 / 2406, `.XY` 0 / 2400; `BACKUP/` `.HST`/`.M1`/`.X1` 6 / 2406 |
| PG000 | 7144149 | `.HST`/`.M1` 36 / 2436, `.H1` 35 / 2435, `.XY` 0; `.MAP`/`.PLA`/`.FLE`/`.R1` not decoded; `BACKUP/` 35 / 2435 |
| TESTSSG1 | 290058 | `.HST`/`.M1` 9 / 2409, `.H1` 8 / 2408, `.XY` 0; `BACKUP/` 8 / 2408 |

In all three games the `.H1` header turn is one less than the `.HST`/`.M1`
header turn. What the `.H1` file contains has not been examined.

### One PG001 turn (observed)

Three runs, each starting from the `registered` snapshot (PG001 files as in
the table above):

- Run 1: by hand. Loaded PG001, opened Help → About and Order Info, and
  generated via the Turn menu.
- Runs 2 and 3: `scripts/oracle/turn PG001.M1`.

Headers after the turn. All files were decoded after runs 1 and 3, with
identical results apart from the flags byte. After run 2 only `PG001.HST`
and `PG001.M1` were decoded, and they match too.

| File | Before | After |
|---|---|---|
| `PG001.HST` | 7 / 2407 | 8 / 2408 |
| `PG001.M1` | 7 / 2407 | 8 / 2408 |
| `PG001.H1` | 6 / 2406, 254 bytes | 7 / 2407, 280 bytes |
| `PG001.XY` | 0 / 2400 | unchanged (same SHA-256) |
| `BACKUP/PG001.HST` | 6 / 2406 | 7 / 2407, byte-identical to the pre-turn `PG001.HST` |
| `BACKUP/PG001.M1` | 6 / 2406, 603 bytes | 7 / 2407, byte-identical to the pre-turn `PG001.M1` |
| `BACKUP/PG001.X1` | 6 / 2406 | 7 / 2407, 39 bytes (no pre-turn `PG001.X1` existed) |

Other observations:

- The game ID was unchanged in every file.
- Endeavor's population read in the UI after the turn: 53,500 (runs 1
  and 2).
- Output bytes differ between runs. Matching files have equal lengths but
  different header salt values (`.HST` 1377 vs 827 in runs 1 and 2), and
  most bytes differ. *Inferred from the documented encryption:* the files
  cannot be compared by hash, only by decoded content or the UI.
- The header flags byte of the new `.HST`/`.M1` was `0xa0`, `0x80`, and
  `0x20` in runs 1–3 (pre-turn: `0x20`). Its meaning is unknown and not
  investigated here.
- *Not established:* why Stars! writes `BACKUP/` and `.X1` as it does. The
  table only records what happened.

## Registration

*Observed:* the pristine StarsBox shows a "Stars! Serial Number" dialog when
Stars! starts. Cancel exits Stars!, so no game can be opened. The bundle's
`WINDOWS/SERIALNO.INI` has `[mswindows]` keys. *Inferred:* it is the Windows
3.1 install record, not Stars! registration.

`scripts/oracle/bootstrap` does all of this. By hand, register once per
pristine base, then keep a snapshot:

```sh
scripts/oracle/reset
scripts/oracle/start
scripts/oracle/wait-for ~/.stars-oracle/refs/serial-dialog-title.png 440 344 120
scripts/oracle/register              # reads $STARS_SERIAL (or pass a serial file)
scripts/oracle/wait-for ~/.stars-oracle/refs/main-menu-open.png 367 802 30
scripts/oracle/key alt+x            # exit Stars! before stopping
scripts/oracle/wait-stable 30 2
scripts/oracle/stop
scripts/oracle/snapshot registered  # later: scripts/oracle/reset registered
```

Where the registration is kept:

- *Observed:* the `registered` snapshot differs from pristine in exactly
  three files: `WINDOWS/STARS.INI` (added), `WINDOWS/WIN.INI` (the
  `MouseSpeed` tweak), and `WINDOWS/WIN386.SWP`. The serial does not appear
  in plaintext in any file of the run copy. An unregistered run also
  creates `STARS.INI`, with the same key names.
- *Hypothesis:* the registration is encoded in `STARS.INI`.
- *Observed* on the second registration (2026-10-06, fresh pristine base):
  the serial was accepted again and the `registered` snapshot differed from
  pristine in `STARS.INI` (added) and `WIN.INI` only; `WIN386.SWP` was not
  reported modified that time. The 2407 → 2408 check on that base read
  53,500 again.
- Either way, treat `STARS.INI` and every snapshot as registration-bearing:
  they stay under `$ORACLE_HOME`, and `STARS.INI` is git-ignored.
- Game files written by a registered copy are encrypted, so a plaintext
  search cannot show that they carry no registration data. The PG-002
  `.HST` files were therefore kept out of this public repository (see
  `docs/PARITY.md`, PG-002).

Before collecting parity data on a new base, run the behavioral check.
PG001 is at 2407 with 48,600 colonists and a growth carry of 80
(`docs/PARITY.md`). Predictions:

- uncrowded 10% growth: 486×10 + 80 = 4,940 → +49 → **53,500** in 2408;
- the halved-growth penalty (5%): 486×5 + 80 = 2,510 → +25 → 51,100.

Read the population from the planet Status panel; Elegy cannot decode it
from the `.HST` yet. Observed on 2026-10-06: 53,500 (runs 1 and 2).

## Smoke tests

Plumbing only, without apparatus (about 10 s, own temporary `ORACLE_HOME`,
display `:78`):

```sh
scripts/oracle/selftest      # ends with "selftest: PASS"
```

Real apparatus, boot to Stars! (unregistered base):

```sh
scripts/oracle/reset
scripts/oracle/start
scripts/oracle/wait-for ~/.stars-oracle/refs/serial-dialog-title.png 440 344 120
scripts/oracle/key Escape             # Stars! exits to Program Manager
scripts/oracle/click 50 84 1 --double # relaunch Stars! from its icon
scripts/oracle/wait-for ~/.stars-oracle/refs/serial-dialog-title.png 440 344 60
scripts/oracle/stop
scripts/oracle/reset
```

Real apparatus, one turn of PG001 (needs the `registered` snapshot):

```sh
scripts/oracle/reset registered
scripts/oracle/start
scripts/oracle/wait-for ~/.stars-oracle/refs/main-menu-open.png 367 802 60
scripts/oracle/turn PG001.M1
#   before: game=92584875 version=2.83.0 turn=7 year=2407 ...
#   after:  game=92584875 version=2.83.0 turn=8 year=2408 ...   (flags vary)
scripts/oracle/stop
scripts/oracle/status          # PG001.HST/.M1/.H1 and BACKUP/PG001.HST/.M1/.X1 modified
scripts/oracle/reset registered
```

`turn` took about 8 s. It gives no orders; it only opens the file and
presses F9 once. Run `stars-record` on `run/games/stars_games` alongside it
to keep every `.HST` state.

### Reading a value after `turn` (observed, PG-002)

`turn` ends with File → Exit, which leaves Stars! and returns to Program
Manager, not to the title screen. To read the new state in the UI without
restarting the oracle:

```sh
scripts/oracle/click 50 84 1 --double   # Stars! icon
scripts/oracle/wait-for ~/.stars-oracle/refs/main-menu-open.png 367 802 60
scripts/oracle/key alt+o; scripts/oracle/type 'd:\pg001.m1'; scripts/oracle/key Return
scripts/oracle/wait-stable 30 2; scripts/oracle/screenshot
```

- *Observed twice:* keys sent without first waiting for the title screen
  went to Program Manager instead (once after a double-click sent right
  after `turn`, once with no relaunch at all). Always `wait-for` first.
- After relaunching from the icon, the Open dialog was given the full path
  `d:\pg001.m1`. *Not tested:* whether the bare name works there.
- With PG001 open, Endeavor is selected and its population shows in both
  the Status panel and the Summary at the bottom right.
- Opening the game and exiting with File → Exit did not create a
  `PG001.X1` (checked once, at 2408).

Advancing many turns (PG-002 used this, 17 times in a row, about 17 s per
turn; every turn advanced the header by one):

```sh
for i in $(seq 1 17); do
  scripts/oracle/start
  scripts/oracle/wait-for ~/.stars-oracle/refs/main-menu-open.png 367 802 60
  scripts/oracle/turn PG001.M1
  scripts/oracle/stop
done
```

## Synthetic fleet starts (FleetLab, observed 2026-10-07)

`tools/fleetlab` builds controlled starting states for movement experiments
by editing a host file with StarsAPI (pinned commit, built on first use into
`~/.cache/fleetlab`; needs a JDK and network once).

```sh
tools/fleetlab/fleetlab dump FILE...                  # fleets, waypoints, designs, events
tools/fleetlab/fleetlab build BASE.HST SPEC OUT.HST   # spec format: header of FleetLab.java
tools/fleetlab/oracle-turn START.HST OUTDIR           # reset registered, install as PG001.HST, one turn
python3 tools/fleetlab/summarize.py OUTDIR            # per-fleet start/end/fuel/events
```

- Re-encoding PG001.HST unchanged with FleetLab reproduces the original
  bytes except one waypoint target-type byte (`0x91` is written as `0x11`).
- Edited files (replaced fleets, cloned designs, changed tech) loaded and
  generated a turn without any visible complaint (FM-000 to FM-003). Only
  `PG001.HST` is replaced; the old `PG001.M1` is opened, and the turn reads
  the host file. The 2408 `.M1` reflects the edited fleets.
- `OUTDIR` holds registered-copy output: preserve it in the apparatus
  repository, never here.

## Known fragility

- `stop` kills DOSBox outright. Exit Stars! first (`turn` does), and take
  snapshots only while stopped.
- Observed once: a `ctrl+F10` sent from `start` right after the window
  appeared did not lock the mouse. *Hypothesis:* DOSBox wasn't yet
  processing keys. `click` therefore locks lazily, on first use.
- No window manager runs: `wmctrl` reports nothing, and `xdotool windowmove`
  had no effect. Use `xdotool` and `SDL_VIDEO_WINDOW_POS`.
- Keystrokes go to the focused window. Don't run two input scripts at once.
- The xkbcomp warnings in `state/xvfb.log` and the ALSA warning in
  `state/dosbox.log` have had no visible effect.
- One oracle per `ORACLE_DISPLAY`. Use different `ORACLE_HOME` and
  `ORACLE_DISPLAY` values to run several side by side.
- The container can be recycled while idle (this happened once), which
  kills the oracle. `$ORACLE_HOME` survived that time; re-run `start`.
