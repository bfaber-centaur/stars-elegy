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

## Setting up a state (observed, PQ-001)

`turn` only presses F9, so experiments that need a particular planet state
edit the game files instead. `scripts/oracle/hst-edit` decodes and
re-encodes `.HST`/`.M1` files with StarsAPI (pinned commit, built under
`$ORACLE_HOME`); `scripts/oracle/edit-turn OUTDIR key=value...` resets to
the `registered` snapshot, applies the same edit to `PG001.HST` and
`PG001.M1`, generates `TURNS` years and keeps every file plus a decoded
dump.

```sh
scripts/oracle/hst-edit dump FILE.HST FILE.M1      # planet, queue, research, events
scripts/oracle/edit-turn /tmp/pq-case mines=0 factories=0 researchPct=0 \
    pop=1050 queue=7:20:0:1                        # Factory x20 on planet 7
```

Observed on 2026-10-07 (PQ-001, about 20 generated years):

- The unmodified PG001 2407 `.HST` round-trips byte-identically through the
  codec.
- Stars! loaded every edited pair and generated the turn from the edited
  state: population, minerals, mines, factories, defenses, the leftover-only
  box, the research budget and the production queue all took effect. No
  checksum or consistency complaint was seen.
- The production queue is a type-28 block right after the planet block, in
  both files. Queue item: `id = (dword >> 10) & 0x7f`, count = low 10 bits,
  kind `(w1 >> 1) & 7` (1 = planetary item), percent `(w1 >> 4) & 0x7f`.
- The `.M1` event block (type 12) lists the year's messages; each record
  starts with the message id (e.g. 0x3e "completed its orders").
- Edits are made only while the oracle is stopped (DOSBox caches directory
  listings). Both files are edited because the client opens `.M1` before
  generating; whether editing the `.HST` alone suffices was not tested.
- Set mines to 0 to keep surface minerals fixed during the year; mining
  happens before production.
- `dump` prints `scannerField` = planetary scanner index, 31 = none. The
  game omits a planet's 8-byte installations block when growth carry,
  mines, factories, defenses and the leftover-only box are all 0 and there
  is no scanner. `dump` prints 31 for such a planet; before 2026-10-07 it
  printed 16 (StarsAPI's zeroed default), which is the same game state
  (TK-001..007: all 36 such records).
- Race and starbase keys (added for KX-001): `prt=N` (0 HE … 4 IS … 8 AR,
  9 JOAT), `lrt=HEX` (the 32-bit lesser-trait word; bit 6 Mineral
  Alchemy, bit 31 "factories cost 1 kT less germanium"),
  `stat=I:V/...` (race stat I: 0 colonists per resource ÷100, 1 factory
  output, 2 factory cost, 3 factories operated, 4 mine output, 5 mine
  cost, 6 mines operated), `hab=C,C,C,L,L,L,H,H,H` (centre, low, high per
  axis) and `starbase=0|1` on the planet. They edit player 1 only; `dump`
  prints the race line and the planet's starbase design slot. All of them
  took effect in KX-001 (2026-10-07).
- Keys added for KX-002 (2026-10-07), all of which took effect:
  `stat=8:V` … `stat=13:V` are the six research cost settings (energy …
  biotech; 0 costs 75% more, 1 normal, 2 costs 50% less);
  `field=CUR,NEXT` sets the research field byte (current field 0–5; next
  field 0–5, 6 same field, 7 lowest field); `conc=I,B,G` sets the
  planet's mineral concentrations and keeps its fraction bytes. `dump` now
  prints `next=` on the research line and `frac=` (the stored length byte,
  then one byte per mineral; a mineral with 2 length bits of 0 has no
  byte) on the planet line. LRT bits used: 1 Total
  Terraforming, 4 Generalized Research, 9 Only Basic Remote Mining.
  `TURNS=3 edit-turn …` ran three years in a row without trouble.
- Added for KX-003 (2026-10-07): `hst-edit xy IN.XY OUT.XY OFF:HEX…`
  sets bytes of the game record (block type 7 in the `.XY` file):
  `0x10` game options (bit 1 slower tech, bit 7 no random events; CB has
  `0x80`), `0x14 + i` victory condition i (bit 7 enabled, low 7 bits the
  value; `KERNEL.md`, "Victory conditions"). An unedited `.XY` round-trips
  byte for byte. Put the edited `CB.XY` in the `pinned-turn` base
  directory: the generated year used it (S2's slower tech took effect).
  `dump` prints `game` (the record's first 32 bytes) for a `.XY` and
  `scores` (block type 45) for a `.M`: per record, word 0 the flag word,
  word 1 the rank, then score (32 bits), resources (32), planets,
  starbases, unarmed, escort and capital ship counts and the tech-level
  sum (16 bits each). A player's `.M` held only its own record. The
  `race` line now prints 14 stats (8–13 the research cost settings). On
  a Combat Lab file, `hst-edit edit` needs `planet=` set to a planet player
  0 owns (the default 7 is not).
- An edited race must stay within the race wizard's point budget. KX-001
  M3 (cheaper factories and mines, nothing paid for them) was flagged in
  the generated year: message id 0x117 in the `.M1`, and the race's
  colonists-per-resource stat raised from 10 to 24 before production, which
  changes every resource figure. Check the `race` line of the after-dump
  and the event list for 0x117 before trusting a race-edit case.
  JOAT → Super Stealth (`prt 1 1`) is over budget (KX-003 S3: 0x117,
  colonists-per-resource 24); LRTs `0x1b80` made it legal (S3L). JOAT →
  Claim Adjuster is legal.
- KX-004 (2026-10-07): long runs go one year per `pinned-turn` process
  (`experiments/kx004/run-kx4.sh`, about 13 s a year), with a different
  cycles value each year so each year draws from a different random
  stream. Running several `stars.exe -g` in one DOSBox autoexec does not
  work: Windows stays up after the first generated year.
- Event records in a `.M` file's events block (the `events` hex from
  `hst-edit dump`): a 16-bit word whose low 9 bits are the message id and
  whose bits 9 and up flag which parameters take 2 bytes; a 16-bit
  object word; then the parameters, 1 byte each unless flagged. The number
  of parameters depends on the message id (a table in the original
  program; the private KX-004 checker carries it). Example: `5901 feff 00
  17` is message 0x159 with object −2 and parameters 0 and 23.
- A state the game cannot process shows a Windows "Application Error"
  dialog (KX-001 Z1: "integer divide by 0") and no year is written; `turn`
  and `host-turn` then time out with the dialog still open. Take a
  screenshot, then `stop`.

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
- FM-004 also loaded cloned designs with engines the race cannot normally
  build (Fuel Mizer, Settler's Delight), fleets placed in orbit
  (`fleet ID planet P at X Y`), and fuel above tank capacity; the turn used
  them as given. `fleetlab dump` lists planets with starbases and the
  starbase hulls.
- `OUTDIR` holds registered-copy output: preserve it in the apparatus
  repository, never here.

## Combat Lab: multi-player turns in Host Mode (observed 2026-10-07)

Battles need at least two players, and the preserved PG001 game has one.
"Combat Lab" (`CB`, game id 82222) was made once with the Advanced New
Game wizard: two Humanoid players (JOAT), tiny universe, sparse, no random
events, 24 planets. Player 0's homeworld is planet 17 at (1306,1060),
player 1's planet 8 at (1169,1145); y = 1230 between x = 1020 and 1300 has
no planet nearby, which leaves room for eight deep-space battles 40 ly
apart. The 2400 files (`CB.HST`, `CB.M1`, `CB.M2`, `CB.XY`) are kept in
the apparatus repository (`evidence/cb/base2400/`).

```sh
tools/fleetlab/combatlab dump FILE...               # players, designs, plans, fleets, objects, battles
tools/fleetlab/combatlab build CB.HST SPEC OUT.HST  # spec format: header of CombatLab.java
tools/fleetlab/host-turn OUT.HST BASEDIR OUTDIR     # reset registered, generate one year in Host Mode
```

- Opening a `.HST` from the title screen (File → Open, `cb.hst`) shows
  the "Stars! Host Mode" dialog. "Generate Now" is at (737,361) and asks
  for confirmation (alt+y). `host-turn` waits for the host file's turn
  number to change (the header flags change as soon as the file is
  opened), closes the dialog (alt+c) and exits (alt+x).
- Players need not submit turns. A player's `.M` file then carries every
  year since its last submission (the client reports "2 years of data
  read"; `combatlab dump` shows both years). Both players' `.M` files
  carry the same battle records.
- `combatlab build` replaced ship and starbase designs (the game
  recomputed armor for Regenerating Shields), battle plans, relations,
  tech levels, LRTs and every fleet; all loaded without complaint.
- **Movement inside battles was not reproducible with host-turn.**
  CB-001, generated twice from the same file after a reset, gave
  different token moves. This qualifies "restarted runs reuse nearly the
  same random draws" (fleet movement corpus). Use pinned-turn below.
- `OUTDIR` holds registered-copy output (and a screenshot of the Host
  Mode dialog): preserve it in the apparatus repository, never here.
- `planet N owner P pop X starbase D|none` gives a player extra planets
  with chosen starbases (fields copied from the player's homeworld; no
  installations); `fleet … dmg D:UNITS:PCT` starts a stack damaged;
  `research P PCT` sets the research share. All were accepted by the
  game (CB-011..018).

### Pinned battle RNG (observed 2026-10-07)

```sh
tools/fleetlab/pinned-turn START.HST BASEDIR OUTDIR [CYCLES] [GAME]
```

The binary reading says Stars! seeds its random stream once at startup
from the Windows tick count, so a rerun differs whenever startup timing
differs. `pinned-turn` removes host timing from that: DOSBox runs with
`cycles=fixed CYCLES` (default 20000) and the autoexec starts
`win /n stars.exe -g cb.hst`. With `-g` Stars! generates the year and
exits on its own, with no window input (no Host Mode dialog). It uses
`ORACLE_CYCLES_OVERRIDE` / `ORACLE_AUTOEXEC_OVERRIDE`, which win over
`oracle.conf`.

- Repeats of the same start and CYCLES gave byte-identical battle records
  and host files: CB-001, CB-002 and CB-008 starts twice each, CB-008 a
  third time through the committed tool.
- Different CYCLES values usually give different streams, but few
  distinct ones: on the CB-018 start, 14 values gave 6 streams (every
  value from 50000 to 100000 gave the same one). 20000 reproduced the
  Host Mode CB-001 run1 and 30000 reproduced CB-001 run2 and CB-002 run1.
  To sample a random outcome, compare record hashes and count streams,
  not runs.
- A generation takes a few seconds after DOSBox starts.
- **Which stream a cycles value reaches** (KX-004, 2026-10-07). The
  startup tick is `trunc(k·54.925)` ms for a small integer k, about
  `k ≈ 70000/cycles`. Ticks identified by replaying random events: 35000
  and 45000 → 109; 11500 → 329; 10500, 9800 → 384; 6000 → 659; 5200 → 768;
  3700 → 1098; 2260, 2190 → 1812; 1985–1955 → 2032; 1750, 1710 → 2306;
  1490 → 2691; 1210 → 3295; 1190, 1170, 1160 → 3405; 1165, 1155 → 3460;
  1135, 1130, 1090 → 3570; 930 → 4284; 890 → 4613; 880 → 4503. Below
  about 1200 the mapping is not monotonic. Runs down to cycles 880 still
  took well under a minute each.
- A range like `15000 + 37·year` reaches only two or three ticks, so a
  long run of pinned years repeats the same few streams; with nothing else
  drawing, yearly random events read the same draws every year (KX-004 E1:
  148 years, no event). To sample random outcomes, choose cycles values
  that reach different ticks.

- In the round-5 starts, 20000 and 25000 always gave the same stream,
  and so did 30000, 35000, 40000 and 45000: twelve values from 5000 to
  50000 gave 8 streams. On CB-041, 6000, 7000, 9000 and 14000 added new
  streams; 11000 repeated 10000, 18000 repeated 14000, and 22000 and
  27000 repeated 20000.

### Production queues and Mystery Trader parts (observed 2026-10-07, CL-TOOL)

CombatLab `queue N ITEMS|none` replaces planet N's production queue in
the host file, and `mt P HEX` sets the Mystery Trader items player P owns
(a 16-bit mask; `combatlab dump` prints it as `mt=`). Queue items use
hst-edit's layout, `ID:COUNT[:PCT]:KIND`, with kind 2 for a ship design
and kind 1 for a planetary item. Designs may name Mystery Trader parts
like any other part (StarsAPI names, e.g. `Anti Matter Torpedo`,
`Multi Cargo Pod`, `Mini Morph`).

One turn on the Combat Lab base (`experiments/cltool`, cycles 20000):

- `queue 8 1:2:2` (two of player 1's design 1, a bare Scout): the
  homeworld built both that year, as one new fleet, and the queue was
  empty afterwards.
- Player 0 owned no Mystery Trader items (`mt=0000`). Its Anti Matter
  Torpedo Destroyer and a Mini Morph with Multi Cargo Pods, a Multi
  Function Pod, a Mega Poly Shell and a Langston Shell were both kept by
  the turn. The torpedoes fired, and the stars-decomp checker replayed
  all 10 hits. Parts the owner lacks the tech for are still stripped
  (SC-021); hidden Mystery Trader parts are not.
- `mt 1 0x0003` survived the turn unchanged.

### Route destinations and fleet ranges (observed 2026-10-07, SL-TOOL)

- `planetset N route=DEST` gives planet N a route destination. DEST is
  a planet number, and the tool writes DEST + 1. `route=raw:HEX` writes
  the whole word, and `route=none` clears it. `combatlab dump` prints
  the word as `route=` in the `pdetail` line.
- `fleets OWNER FROM-TO <fleet tokens>` makes one fleet per id in the
  range. Fleet ids are 0..511.
- Fleet lines now show bytes 2, 3 and 5 and the waypoint count. A
  fleet-name block (block 21), if present, prints as `fleetname`.
- Starbase design ids in a queue are 16 + slot, kind 2 (`17:1:2` builds
  starbase design 1).
- Giving `sbdesign` lines for a player replaces that player's whole
  starbase design list. Restate slot 0 if a planet's existing starbase
  uses it.

One turn on the Combat Lab base (`experiments/sltool`, cycles 30000):

- Both route words came back unchanged.
- Each new fleet had waypoint 1 at the route destination, task 8
  (route).
- Two Scouts from one queue item became one fleet with full fuel.
- An Orbital Fort in the queue replaced a Space Station.
- A player at 510 fleets built one more (fleet 510). Its queue kept the
  rest at 28%, which looks resource-limited.
- No fleet-name blocks were written.

### Client orders (observed 2026-10-07, BP)

`tools/fleetlab/client-orders DIR OUTDIR CMDS [MFILE] [GAME]` opens a
player's turn in the original client, runs a command file, saves with
File > Save and keeps the order file (`GAME.Xn`, with `GAME.Hn`), a
screenshot per command, and `orders.dump`. Then run the year with
`pinned-turn START.HST BASE OUT`, where BASE holds DIR's files plus the
order file: the registered host read the client's `.X1` (BP-1, BP-L).
The command list is in the script's header. Order files carry the
registration, so OUTDIR stays private. Getting a consistent `.M1` for a
Combat Lab start: one `pinned-turn` year, then open `raw/after/cb.m1`.

What the client did, at 1152x864:

- Opening `cb.m1` shows "Note: N years of data read." (Return). The
  homeworld is selected in the planet view.
- File > Save is `alt+f s`. `ctrl+s` did nothing after an Escape had left
  the menu bar active. The year shows `2401*` while there are unsaved
  orders.
- Battle Plans (F6) dialog at (362, 325). Mnemonics: `alt+p` Plan list,
  `alt+c` Copy (opens "Rename Battle Plan" with "NAME (2)"; type and
  Return), `alt+r` Rename, `alt+d` Delete, `alt+e` Secondary Target,
  `alt+t` Tactic, `alt+w` Attack Who. Primary Target's mnemonic collides
  with Rename: use `alt+e shift+Tab`. With a list focused and closed,
  Home and Down change the selection directly. Close has no working
  mnemonic: click (621, 513). Return in the dialog presses the focused
  button, which closed the dialog during a refused copy. Dump Cargo is
  the box at (686, 478).
- Deleting a plan that fleets use shows an alert (OK = Return). Delete is
  disabled for plan 0. At 15 plans Copy stays enabled but does nothing;
  `client-orders` detects the missing Rename dialog by the pixel at
  (600, 405).
- Fleets: Goto (232, 169) in "Fleets in Orbit" selects the first fleet
  there (`Armed Probe #1` = fleet 0). The fleet panel's Next (144, 132)
  went `#1` → `#4` → `#3` → `#2` → `#1` with four fleets.
- The fleet panel's Battle Plan list (combo at 380, 309) ignored keys;
  use the mouse. Its first item is "Battle Plans..." (opens the dialog),
  then the plans. Six rows of 14 px from y 320. A scroll bar (arrows at
  (380, 327) and (380, 397)) only appears with more than six items, and
  the open list starts scrolled to the current plan.

- **Manual cargo transfer** (XF-1, 2026-10-07). In the fleet view, Xfer
  (161, 213) in the "Orbiting X" panel opens Cargo Transfer with the
  orbited planet, foreign and unowned ones included. Rows (y): fuel 340,
  ironium 380, boranium 400, germanium 420, colonists 440. The arrow at
  x 585 moves cargo from the fleet to the planet, and the arrow at x 567
  moves it back. A click moves 1 kT, shift-click 10, ctrl-click 100,
  each capped. OK is at (627, 555). A foreign or unknown planet shows
  0 kT on its side. The client let colonists go down on a foreign
  homeworld and on an unowned planet. Each fleet's transfers are one
  order record (`combatlab dump`: `order cargo fleet= other= ir= …`;
  positive means loaded into the fleet). The host applied them all: the
  minerals were added to both planets; the colonists were lost, with
  message 0x058 at the foreign homeworld (it has a starbase) and 0x002
  at the unowned planet.
  `client-orders` commands: `fleet xfer`, `xfer ITEM N`, `xfer ok`.

- **Production queue** (PQ-1, 2026-10-07). With a planet shown, Change
  (231, 332) on the Production tile opens "Production Queue for X". The
  left list holds the buildable items, with this race's ship designs
  first, then Factory, Mine, Defenses, Mineral Alchemy and the Auto Build
  items. Its rows are 16 px apart from y 181, at x 300. The queue on the
  right starts with a "Top of the Queue" row at y 181 (x 790), with items
  every 16 px below it. Add (575, 244) inserts the selected left item
  after the selected queue row: a click adds 1, shift-click 10 and
  ctrl-click 100. Remove (575, 294) takes the same amounts off the
  selected row. The client has no count field: a count is set with
  Add and Remove. Item Up (575, 344), Item Down (575, 394), Clear
  (575, 444), the "Contribute only leftover resources to research" box
  (213, 700) and OK (824, 700). The order is one record per planet
  holding its whole new queue. `combatlab dump` prints it as
  `order queue planet= items=ID:COUNT:PCT:KIND`. The host replaced the
  queue with it and built from it the same year (factory ×10 → 3 built).
  Commands: `queue open`, `queue select R`, `queue add I N`,
  `queue remove N`, `queue up`, `queue down`, `queue clear`,
  `queue leftover`, `queue ok`.
- **Research** (PQ-1). F5 opens Research. The field radio buttons are at
  (313, 345 + 21k), k = 0 energy … 5 biotechnology. The budget spinner
  has up (841, 474) and down (841, 485), 1 percent per click. The "Next
  field to research" list (835, 379) has rows every 13 px from y 395:
  <Same field>, the six fields, then <Lowest field>. Done is at
  (742, 580). The order is a 2-byte record: the percent, then the field
  (low nibble) and the next field (high nibble: 4 for electronics, 7 for
  lowest). The host applied both and spent the year's research on the
  new field. Commands: `research open`, `research field K`,
  `research budget D`, `research next I`, `research done`.
- **Waypoint tasks** (WP-1). In the fleet view, the Waypoint Task list
  (181, 441) has rows every 14 px from y 459: none, Transport,
  Colonize, Remote Mining, Merge with Fleet, Scrap Fleet, Lay Mine
  Field, Patrol, Route, Transfer Fleet. Fleet waypoint rows start at
  (60, 262). Transport adds an item list (160, 467: fuel, ironium,
  boranium, germanium, colonists, rows every 16 px from y 486) and an
  action list (123, 490: none, load all, unload all, load exactly,
  unload exactly, fill up to %, wait for %, load dunnage, set amount
  to, set waypoint to; rows every 14 px from y 508). Each item keeps its
  own action, and the amount box is at (152, 490). Each fleet's
  waypoint is one change record (type 5, printed raw). The host ran the
  waypoint-0 tasks the same year:
  - unload exactly 25 kT ironium and load exactly 30 kT germanium at
    the own homeworld were exact;
  - Colonize with no colony module failed with message 0x054;
  - Scrap at a foreign homeworld removed the fleet, gave its cargo and
    scrap minerals to that planet, and sent message 0x05a.
  Commands: `wp select K`, `wp task T`, `wp transport ITEM ACTION [N]`.

### Scanning experiments (observed 2026-10-07, SC-001..SC-023)

```sh
experiments/sc/gen.py CB.XY OUTDIR            # specs + case tables (docs/PARITY.md "Scanning")
experiments/sc/check.py RUN CB.XY OUT/after.dump
```

- CombatLab keys added for this corpus: `planet N scanner none` (removes
  the planetary scanner: scanner id 31), `prt P N` (primary trait, 0 HE …
  9 JOAT) and `hab P C,C,C,L,L,L,H,H,H`. `combatlab dump` now prints, for
  `.M` files, one `seen planet N owner=… level=L starbase=…` line per
  planet report, and each full player block's habitability.
- A player's `.M` holds one section per year since its last submission
  (2400 and 2401 here); read the section whose `file turn=` matches the
  generated year.
- **Designs are checked against tech.** SC-021 gave player 0 electronics
  10 and a Scout with an Elephant Scanner (electronics 16). In the
  generated 2401 files the part was gone (`Scout, 1 Quick Jump 5, empty,
  empty`, mass 18 → 12), and the turn's scanning matched the stripped
  design. Keep every part within its owner's tech. (FM-004's LRT-gated
  engines were kept; whether that check differs was not tested.)
- Race edits and the point budget: JOAT → Claim Adjuster and JOAT + NAS
  generated without message 0x117. JOAT → War Monger did not (SC-015:
  0x117, colonists-per-resource stat raised from 10 to 23); adding No Ram
  Scoop, Cheap Engines, Only Basic Remote Mining, Low Starting Population
  and Bleeding Edge Tech (`lrt 0 0x1b80`) made it legal (SC-015L).
- Visibility did not depend on the random stream: SC-001 generated with
  cycles 20000 and 30000 gave different bytes and identical views.
- Round 4 (SC-024..SC-033, `experiments/sc/round2.py specs|list|check`):
  - `combatlab dump` prints another player's fleet with `dx dy warp wbits
    mass`. Each heading byte holds the component + 127; the dump subtracts
    127, so a fleet that did not move (bytes 0/0) prints `dx=-127
    dy=-127 warp=0`. Planet reports print `env popest defest surface`;
    `popest` is in units of 400 colonists, `defest` 0..15.
  - Design lines in a `.M` dump do not carry the design's owner: a
    partial design prints `owner=?`, and a full foreign design (War
    Monger, after a battle) prints the file's own player. Designs come in
    player order, as many per player as that player's `shipdesigns=`
    count; `round2.py` assigns owners that way.
  - Fleets placed outside the universe are moved to its edge: SC-028 put
    a fleet at y 920 in the tiny Combat Lab universe (1000..1400) and the
    generated year had it at y 1000. Keep every position in range.
  - The homeworld starbases carry Lasers; an enemy fleet in orbit starts a
    battle. Round 4 replaces `sbdesign P 0` with an empty Space Station.

### Takeover experiments (observed 2026-10-07, TK-001..TK-007)

```sh
python3 experiments/tk/gen.py                 # writes experiments/tk/tkNNN.spec
tools/fleetlab/combatlab build CB.HST experiments/tk/tk001.spec start.HST
tools/fleetlab/pinned-turn start.HST BASEDIR OUT [CYCLES]
grep 'after/CB.HST pdetail' OUT/after.dump    # per-planet result
```

- CombatLab keys added for this corpus:
  - `fleet … task TASK` sets the task of waypoint 0, and
    `to X Y [planet N] warp W [task TASK]` adds a waypoint with its own
    task. TASK is `colonize`, `scrap`, `mine`, `unload` (all colonists) or
    `transport A:V,A:V,A:V,A:V,A:V` (Ir, Bo, Ge, colonists, fuel; action
    nibble and value; `-` for none).
  - `planetset N mines= factories= defenses= excess= fe= bo= ge=
    scanner=ID conc=I,B,G env=G,T,R orig=G,T,R sbdmg=U` sets planet fields
    after any `planet` line (`orig` marks the planet terraformed; `sbdmg`
    sets the starbase's damage to U/500 of its armor and needs a
    starbase).
  - `combatlab dump` prints each fleet's waypoints (`wp … task= orders=`)
    and a `pdetail` line per planet: concentrations, environment,
    original environment, surface minerals, population, growth carry,
    installations and scanner id.
- `hst-edit edit … env=G,T,R orig=G,T,R` does the same environment edit
  on a PG001-style file; `dump` prints `orig=` for terraformed planets.
- The game used all of these as given: waypoint-0 tasks ran before
  movement, waypoint-1 tasks on arrival, and edited carry bytes,
  installations, scanner ids and environments took effect.
- A planet made with `planet N owner P` has no production queue. With no
  queue its resources all went to research even at research 0%: player 1
  rose from energy 3 to 5 in one TK-001 year, which changed its
  defenses' coverage. Keep the number of such planets small, or expect
  tech gains.
- Design parts above the owner's tech were removed in the generated year
  (as in SC-021): player 0 at tech 3 lost its Cherry, Smart, Peerless,
  LBU-17 and LBU-32 bombs. Put the attacker at tech 26.
- Populations above 0 with no mines, factories, defenses or carry are
  written without an installations section; `pdetail` then shows no
  `excess=` field.
- Counting random streams: with no battle in the year, the host files
  differed byte-wise between every pair of cycle settings, even settings
  whose random outcomes were all identical. Count streams by the vector of
  random outcomes (TK-007 puts 18 independent draws in one year): 14
  settings gave 7 streams.
- The `.M` event block (type 12) carries one record per message; ids 0x135
  (drop refused by a starbase) and 0x55 (unload at an unowned planet)
  appeared with the fleet and planet numbers next to them. The full record
  layout is in `MESSAGES.md` ("How messages work"), and
  `tools/fleetlab/events.py DUMP...` decodes the block (every block in the
  2026-10-07 corpora decoded cleanly).

### Takeover round 2 (observed 2026-10-07, TK-101..TK-117)

```sh
python3 experiments/tk/gen2.py                # writes tk1NN.spec
python3 experiments/tk/gen2.py --table        # prediction table
python3 experiments/tk/check2.py RUNDIR       # RUNDIR/tk1NN/run*/after.dump vs predictions
```

- New CombatLab keys: `defqueue P ID:COUNT,...` (the player's default
  production queue for new colonies: count byte at PlayerBlock data offset
  0x4f in StarsAPI's `fullDataBytes`, then words `id | count << 6`),
  `defleftover P 0|1` (bit 0 of 0x4e) and `field P FIELD` (research
  field). The dump prints `defqueue=` and `defleftover=` on player lines
  and a `queue planet=N items=id:count:pct:kind,...` line after a planet
  that has a production queue. Combat Lab's players have no default queue.
  The game kept and used the edited queue.
- Legal race edits (no message 0x117): JOAT → WM, AR or CA with
  `lrt P 0x1b80`; JOAT → IS alone; JOAT + Ultimate Recycling with
  `lrt P 0x1ba0`. UR alone (`0x20`) gave 0x117, and the generated year
  showed the race's first stat byte (as `hst-edit` prints it) raised from
  10 to 24; the trait stayed. BET in 0x1b80
  changes miniaturization, so ship costs differ from JOAT's.
- Check `points=` in `combatlab dump` before running: it must be 0 or
  more. Legal starts used in KB: JOAT + UR + NAS + LSP + BET (`lrt P 7200`,
  123 points); AR with `lrt P 7296` (198). An immune axis needs centre, low
  and high all at −1: `hab P 255,50,50,255,45,45,255,55,55` is gravity
  immune (700 points with `lrt P 7552`). Only the centre at 255 is
  repaired by the host before production: message 0x117, and the centre
  is forced to the midpoint of low and high (KB-2C's void first run).
- Queue `N empty` (CombatLab) writes a production queue block holding
  zero items. The game keeps it, and the planet sends nothing to research.
- A second year: run `pinned-turn` again with the first run's
  `raw/after/CB.HST` as START and `raw/after` as BASEDIR (TK-111).
- Three players: `tools/fleetlab/new-game` with three `pg000.r1` lines in
  the definition made TK3, three human players (no AI turns); CombatLab
  built on it unchanged (`pinned-turn … TK3`).
- Scrap in deep space wrote one object: type packet, destination 1023,
  the minerals as its cargo.
- AR colonists in a moving fleet shrink during movement (PARITY.md); give
  AR transports and colony ships enough margin, or start them in orbit.
- Claim Adjuster owners terraform their planets to the best their tech
  allows at the end of the year, so a CA new owner hides the capture-time
  revert of the environment.

### Fleet operations experiments (observed 2026-10-07, FO-01..FO-07)

```sh
python3 experiments/fo/gen.py OUTDIR
tools/fleetlab/combatlab build CB.HST OUTDIR/fo01.spec start.HST
tools/fleetlab/pinned-turn start.HST BASEDIR OUT 20000
python3 experiments/fo/check.py RUNDIR    # RUNDIR/fo01/after.dump ...
```

- New spec syntax: `target fleet OWNER ID` points waypoint 0 at a fleet
  (id `number | owner << 9`, target type 0x12); `to X Y fleet OWNER ID warp
  W` adds a fleet-targeted waypoint; `task merge` (task 4) and `task
  transfer K` (task 9, one word: the K-th player other than the owner).
  All three were accepted by the host as written.
- After the task ran (or was refused), the host had rewritten waypoint 0
  to deep space or the planet. The stars-decomp reading keeps a
  fleet-targeted waypoint 0 at turn start only for transport and merge.
- `combatlab dump` prints an empty `ships=` for a fleet record that has no
  ships (seen after a merge above 32767 ships).
- Relations are per direction: `relation 1 0 2` is player 1's view of
  player 0. Cross-player cargo and fleet transfers depend on the
  receiver's view.

### Movement round 2 (observed 2026-10-07, FM-101..FM-105)

```sh
python3 experiments/fm2/gen.py OUTDIR
tools/fleetlab/combatlab build CB.HST OUTDIR/fm101.spec start.HST
tools/fleetlab/pinned-turn start.HST BASEDIR OUT/fm101/run 20000
python3 experiments/fm2/check.py OUT
```

- `combatlab build` replaces all of a player's starbase designs with the
  spec's. A homeworld whose starbase design is not restated keeps
  pointing at a missing design, so restate design 0 (`sbdesign P 0 Space
  Station = ...`) whenever a spec adds starbase designs.
- JOAT with IFE plus NRSE, CE, OBRM, LSP and BET (`lrt 0x1b81`) is legal
  (no message 0x117).
- A part restricted to another PRT (the Anti-matter Generator, IT only)
  stayed in a JOAT design and worked.

### Universe objects experiments (observed 2026-10-07, OB-001..OB-017)

```sh
python3 experiments/ob/gen.py experiments/ob     # writes obNNN.spec; --list prints the case tables
tools/fleetlab/combatlab build CB.HST experiments/ob/ob001.spec start.HST
tools/fleetlab/pinned-turn start.HST BASEDIR OUT 20000
python3 experiments/ob/check.py OB-001 OUT/after.dump
```

- **Objects as records.** Minefields, packets, wormholes and the Mystery
  Trader are stored in the host file as object blocks (type 43): one count
  block (a 2-byte count), then one 18-byte record per object sorted by id
  `type<<13 | owner<<9 | number`. They come after the starbase designs and
  before the battle plans. The count block is left out when there are no
  objects. CombatLab `thing` lines write these records (header of
  `CombatLab.java`):

  ```text
  thing minefield OWNER NUM X Y COUNT [kind std|heavy|bump] [det] [known MASK] [seen MASK]
  thing packet OWNER NUM X Y DEST WARP IR BO GE [class K] [moved] [bit15]
  thing wormhole NUM X Y PARTNER CLASS [years N] [seen MASK] [seen2 MASK]
  thing trader NUM X Y DX DY WARP [met MASK] [item I]
  thing raw HEX
  ```

  The game loaded, updated and rewrote all four kinds. `combatlab dump`
  prints `things count=` and a `thing id=… type=…` line per record with its
  decoded fields and raw bytes.
- In written host files, wormhole records carry bit 13 of word 6 (0x2000)
  and packet records carry bit 15 of word 6. The game sets packet bit 14
  after a packet moves. Neither bit 15 nor bit 14 changed what the next
  year did (OB-003-J/K, OB-017-E).
- **New waypoint forms.** `task lay [YEARS]` (task 6) writes the lay-mines
  years word. The game writes the task back with 10 more bytes. With years
  0 it laid once and cleared the task. `to X Y thing ID warp W` targets an
  object (waypoint type 0x18), which is how a fleet enters a wormhole.
- **A lay-mines task on waypoint 0 holds the fleet.** A non-SD layer with
  lay on waypoint 0 and a waypoint 1 25 ly away laid in place and did not
  move. Its waypoints were kept (OB-014-D, OB-019).
- **Several years in a row.** `pinned-turn OUT1/raw/after/CB.HST
  OUT1/raw/after OUT2` generates the next year from a run's output
  (OB-019, 2400 → 2403). `check.py` takes `OB_YEAR=N` to check the cases of
  year N only.
- In `combatlab dump`, a fleet's `wp` lines follow its `fleet` line and
  end at the next `fleet` line. Read them per fleet: the first OB-014-D
  report counted waypoint 1 as removed because the dump was read wrongly.
- **Minefield cases must count planets.** Decay depends on the number of
  planets inside the field (`docs/PARITY.md` "Universe objects"). `gen.py`
  asserts the planet set inside every field. OB-001-J forgot this. A fleet
  that ends its move inside an enemy field sweeps it (OB-010-S).
- **Packet damage needs growth control.** Population grows after packet
  impacts in the same year. Set the target's environment to 50,50,50 and
  carry 0 (`planetset N env=50,50,50 …`); then an undamaged planet with
  population P (units of 100) is ⌊1.15·P⌋ after the year (OB-009 A/B).
  Packets 49 ly from a warp-7 target arrive the next year: allow a whole
  year's travel.
- **Round 5 notes (OB-021..OB-027).**
  - Gate jumps: `to X Y planet N warp 11`. Waypoint warp 11 means "use the
    stargate".
  - `combatlab dump` prints `mt=` per player: bytes 0x4a and 0x4b of the
    player block, high byte first. The game's part word is little-endian,
    so item bit 0 shows as `mt=0100`.
  - Do not send Long Hump 6 fleets at warp 10 into minefield cases. Each
    ship has a 1-in-10 chance to be lost before moving (message 0xe1 for a
    whole fleet), which hides the field result. Use warp 9, or a
    warp-10-rated engine.
  - Consecutive `pinned-turn` years start from the same random stream.
    Repeated draws in a multi-year run are not independent (the OB-025
    jiggles repeated their offsets).
  - A thing-target waypoint survives an object's move only if the owner
    knew the object at the start of the year. Set `seen` on the wormhole
    when a case needs the target kept.
- **JOAT built-in scanner.** JOAT Scout, Frigate and Destroyer hulls scan
  20·electronics / 10·electronics on top of their parts (S-10). Player 1
  at electronics 3 with a Rhino: R = ⌊⁴√(50⁴ + 60⁴)⌋ = 66, P = 30.
  OB-011's first checker forgot this.
- **PRT edits.** JOAT → SD (`prt P 5`) was legal. JOAT → PP (6) and IT (7)
  gave message 0x117 (the `.M` event block holds the bytes `17 01`) unless
  `lrt P 0x1b80` was also set, which made them legal.
- **New games from a definition file.** `stars.exe -a FILE.DEF` builds a
  new game with no window input and exits. `tools/fleetlab/new-game DEF OUT
  [CYCLES] [RACE_FILE…]` runs it from the registered snapshot and copies
  the new files out. The definition is plain text:

  ```text
  NAME                      game name
  0 1 1 11                  size (0 tiny … 4 huge), density, player positions, seed
  0 0 0 1 0 0 0             seven option flags; the 4th is "no random events"
  2                         number of players
  pg000.r1                  race file of player 1
  # 1 0                     an AI player (race, level)
  1 60                      eight victory-condition lines
  0 26 4
  0 5000
  0 100
  0 100
  0 100
  0 100
  1 50
  o6t11n.xy                 output file name (DOS 8.3)
  ```

  The race file must be copied into the games directory with the
  definition; `new-game` copies its extra arguments there. Copy it to a
  path outside the games directory first, because the reset deletes it.
- More than one race file can follow the definition (`new-game DEF OUT
  CYCLES a.r1 b.r1 …`); the definition names them by file name, one per
  human player (UG16..UG21, up to six race files with ten computer
  players).
- A run can fail silently, with no new files: once, right after the
  oracle reset, while the fleetlab tools were being rebuilt. Rerunning the
  same definition worked. Check that `OUT/raw` has the `.HST` before
  trusting a run.
- **Race design corpus (RD, observed 2026-10-07).** A race file with a bad
  checksum stops game creation with "The game file X.r1 appears to be
  corrupt, unable to load file" and an OK box; `new-game` then times out
  with `fail.png`. `racelab dump` prints `checksum=BAD` for such a file, and
  `racelab edit IN OUT` with no keys rewrites the checksum. Definition files
  may have CRLF line ends: strip `\r` before reading race file names from
  them in shell.
- In a running game (RD-P), `hst-edit` race edits to PRT, colonists per
  resource or race stat 15 are clamped silently by the next generation,
  while negative points or a malformed habitat are punished (message
  0x117). Check the event list before treating a race edit as unpunished.
- **Race files** (`tools/fleetlab/racelab`, observed 2026-10-07, UG):
  `racelab dump FILE.R1…` prints name, PRT, LRTs, growth, habitability,
  the economy stats, the leftover-points spend, whether the checksum is
  right, and the advantage points left. `racelab edit IN OUT prt=N
  lrt=0xNNNN spend=N growth=N name=S plural=S` writes a new race file with a
  recomputed checksum. PRT numbers run 0 HE, 1 SS, 2 WM, 3 CA, 4 IS, 5 SD,
  6 PP, 7 IT, 8 AR, 9 JOAT; spend 0 surface minerals, 1 concentrations,
  2 mines, 3 factories, 4 defenses.
- The points come from StarsAPI's race calculator, compiled into the
  fleetlab build. It agreed with every in-game legality result so far:
  PG000.R1 changed to WM scores −12, and the game penalized that race
  (message 0x117); PP (−37) and IT (−57) score below 0 as well and were
  not used. Keep crafted races at 0 or above; with more than 50 points
  left the homeworld gets the full 50-point spend.

### Wormholes and Mystery Trader over several years (observed 2026-10-07, WT-000)

```sh
python3 experiments/wt/smoke.py OUT                    # or a batch generator built on experiments/wt/wt.py
tools/fleetlab/combatlab build BASE/CB.HST OUT/wt000.spec OUT/start.HST
tools/fleetlab/years OUT/start.HST BASE OUT/run N [CYCLES|C1,C2,...] [STEP]
python3 experiments/wt/trace.py OUT/run                # per-year wormholes, Traders, fleets, tech
```

- `years` chains `pinned-turn`: year k starts from year k−1's
  `raw/after`. It runs with CYCLES + (k−1)·STEP (STEP defaults to 1000),
  or with the k-th entry of a comma list.
- **Each pinned year reseeds.** Every year starts a fresh DOSBox. With the
  same cycles every year, the same draws repeat. In WT-000 at 20000 three
  years running, every wormhole end moved by the same vector each year.
  Cycles values also fall into few streams: 21 values from 20000 to 45000
  gave 3 on the WT-000 start. This matches the KX-004 cycles-to-tick map
  (stars-elegy #44), so a sweep for random outcomes such as jump odds has
  to reach low cycles values. `trace.py` flags a year whose wormhole moves repeat the year
  before as `SAME STREAM?`. Year-1 stream classes for the WT-000 start are
  in `experiments/wt/README.md`.
- Wormhole and Trader `thing` lines take raw-word tokens: `w14 HEX` and
  `w16 HEX` for wormholes, `w10 HEX` and `w16 HEX` for Traders. A Trader's
  `w10` replaces the whole word, warp included.
- **Trader raw words after a move.** The game sets bit 4 of a Trader's
  `w10` (0x0008 → 0x0018) on its first move. Its `w16` read 0, 1, 2 in the
  files after years 1–3.
- **Staging a meeting.** OB-004 showed that a stationary fleet at the
  Trader does not trade. `wt.py meet` places the fleet `back` ly west of
  the Trader's expected end point and flies it there. The end point comes
  from `axis_move` (warp² ly along an axis, OB-004), so stage meetings on
  axis-aligned headings only.

### Component displays (observed 2026-10-07, CS-001)

- `hst-edit edit` also takes `tech=E,W,P,C,EL,B` (current levels) and
  `mt=HEX` (Mystery Trader items owned). Edit `PG001.HST` and `PG001.M1`
  the same way; opening the `.M1` shows the edited race, with no turn
  needed. Race checks (message 0x117) happen only when a turn is
  generated, so display-only setups may be outside the point budget.
- Technology Browser: Help → Technology Browser (`alt+h b`); Space steps
  to the next item through every category, wrapping at the end. The item
  pane is at (395, 257), 362×350.
- Ship & Starbase Designer: F4. "Available Hull Types" radio at (303, 307),
  "Starbases" at (303, 240). Click the hull combo (730, 212) twice to give
  it focus with the list closed; Down then steps through the hulls (Return
  or Escape would close the dialog). The panel shows the slot layout and
  the cost of one hull for this race.
- The planet status panel (left, "Defense Type", "Def Coverage") gives the
  homeworld's 10 defenses' coverage for the best defense the tech allows.
- CS-002: designs using engines the race may not build (HE-only, IFE,
  NRSE) were kept at tech 26; parts above the owner's tech are not.
- CS-003: a Combat Lab player's designs are read in the designer after
  one generation: copy the run's `raw/after/CB.*` into the games
  directory, open `cb.m1`, dismiss "Note: 2 years of data read" with
  Return, then F4. The designer opens on "Existing Designs"; click the
  combo (730, 212) twice and step with Down as for hulls. The panel shows
  mass, max fuel, armor, shields, cloak/jam, initiative/moves and, when
  the design has any scanning part, "Scanner Range" normal / penetrating.
- Battle records (`combatlab dump` hit lines): torpedo and missile hits
  carry flag 0x04, missile hits also 0x08. Records with 0x80 added left
  the target unchanged; against the unshielded targets of CS-003-C2 there
  was one for each shot that missed. The CS-003 checker skips them.

### Turn messages and minefield runs (observed 2026-10-07, MF)

- `combatlab dump` decodes each `.M` file's message block (block type
  12), after the `events raw=` line: `msg id=0xNN name=... obj=0xOOOO
  p=P1,P2,...`. A record is a word `w` (message id `w & 0x1ff`, size flags
  `w >> 9`), a word `obj`, then the message's parameters: parameter k is 2
  bytes if flag bit k is set, else 1 byte. How many parameters each id
  takes is read at run time from the local original game (`STARS_EXE`,
  default the oracle run copy; checked by hash); without it only the raw
  line prints. All 728 message blocks in the apparatus evidence parse
  exactly. Names are given for the minefield ids (0xbe..0xcc, 0xf4,
  0x15f..0x164, 0x17e); others print `name=-`.
- Minefield message parameters seen: hit messages (0xc5..0xc8, victim)
  are fleet, field owner, field kind (0 standard, 1 heavy, 2 speed bump),
  x, y of the stop and damage (before shields); the field owner's
  versions (0xc9..0xcc) drop the owner. Detonation messages are 0x160..0x164.
  Sweep messages give the swept count and the field's kind and centre.
  Fleet parameters are object ids, `0x8000 | owner << 9 | number`.
- Follow orders (`to X Y fleet OWNER ID warp W`) store the target's object
  id, `owner << 9 | number`. A bare number aims at player 0's fleet: FleetLab's
  `wpf` (FM corpus, player 0 only) is fine, but a player-1 follower aimed
  that way flies to the waypoint coordinates (first MF-02 run). The MF
  specs in the apparatus were built with an interim `fleet N` (same owner)
  form that wrote the same ids.
- Pinned streams for the MF starts: cycles 20000 and 25000 gave the same
  stream, as did 30000, 35000 and 40000; 15000 was a third. Runs at the
  same cycles reuse the same draws even with different fleets, so
  MF-01, MF-05b, MF-02's leaders and MF-09h's first fleets stopped at the
  same offsets. Pool rate samples across distinct streams only.
- Minefield counts are 32-bit in the object record; fields of 2,100,000
  load and decay normally.

### Client estimates (observed 2026-10-07, ES-001)

```sh
python3 experiments/es001/gen.py OUTDIR
tools/fleetlab/combatlab build CB.HST OUTDIR/es001.spec start.HST
tools/fleetlab/pinned-turn start.HST BASEDIR OUT 20000
tools/fleetlab/combatlab dump OUT/raw/after/CB.HST > after.dump
python3 experiments/es001/predict.py after.dump > predictions.tsv   # commit before opening the client
python3 experiments/es001/check.py predictions.tsv results.tsv
```

- `combatlab dump` prints each player's economy settings for the model:
  `race=` (growth %, colonists per resource / 100, factory output, cost,
  operated, mine output, cost, operated), `rcost=` (research cost
  setting per field, 0 expensive, 1 normal, 2 cheap), `resLast=` (last
  year's research spending), and per planet `frac=` (mineral depletion
  fractions) and `homeworld`.
- A first waypoint at the fleet's own position keeps the fleet where it
  is for the year and leaves its other waypoints as orders, so the
  generated file still has multi-leg routes to read estimates from.
- Open `cb.m1` from `OUT/raw/after` (title screen: alt+o, `cb.m1`,
  Return; "2 years of data read", Return).
- Report → Planets (F3) and Report → Fleets: the maximize button at
  (862,244) shows every column. Double-clicking a row selects that planet
  or fleet; Escape returns to the main window with it selected.
- Fleet view: the Fleet Waypoints list rows are at y = 262 + 14·k
  (x ≈ 60); clicking a row updates Distance, Travel Time and Est Fuel
  Usage. "Est. Range" is in the Fleet Composition tile. The fleet Next
  button (145,132) steps through the fleets in fleet-report order.
- Planet view: the Production list rows are at y = 219 + 14·k (x ≈ 260);
  "Completion:" is under the list. The planet Next button is also at
  (145,132).
- The population popup appears only while the mouse button is held on the
  Status tile's "Population" row (≈ 40,299): press, screenshot, release.
  `scripts/oracle/click` releases at once, so press with `xdotool
  mousedown 1` after moving the pointer the way `click` does.
- F5 opens the Research dialog.
- ES-002 (`experiments/es002`, same commands with `es002.spec`;
  `predict.py` takes `after.dump` with the `.XY` dump appended, and
  optionally the `.M1` dump for the planets player 0 has reports of).
  To read another player's view, exit the game and use File → Open: the
  dialog starts in `c:\stars`, so type the full path (`d:\cb.m2`). With
  the fleet view up, alt+r p did not open the planet report; F3 did.

### Files written during a generation (observed 2026-10-07)

- `PINNED_CAPTURE=DIR tools/fleetlab/pinned-turn …` starts
  `tools/fleetlab/capture-writes`, an inotify watcher on the games directory
  that copies every file as it is closed to `DIR/NNN-name` (write order) and
  logs create/write/delete events to `DIR/events.log`. It starts after the
  reset, which deletes the directory.
- With computer players, a `-g` generation writes one `.Xn`/`.Hn` pair per
  computer player (in player order) before the `.HST`, then the `.M` files
  and the `.HST` again; the computer players' `.Xn` files are gone when
  Stars! exits, so only the capture keeps them. They are registered-copy
  output (private apparatus only); the decoder is private.
- A rerun from the same start at the same cycles captured the same
  computer orders; a different stream changed only random choices such as
  names and pictures (one 7-player game, one year).

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
