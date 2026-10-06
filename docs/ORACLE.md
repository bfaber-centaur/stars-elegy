# Stars! J-RC3 Oracle

The oracle is the original Stars! J-RC3, run headlessly, so experiments can be
carried out against it and compared with Elegy:

```text
Xvfb → DOSBox → Windows 3.1 → Stars! J-RC3
        ↑ xdotool (keys, mouse)    ↓ screenshots, files on the Linux side
```

All control goes through `scripts/oracle/`. The proprietary apparatus stays
outside the repository, under `$ORACLE_HOME` (default `~/.stars-oracle`).

## Status

Verified with the real StarsBox + `stars_games` apparatus on 2026-10-06 unless
marked otherwise.

| Capability | State |
|---|---|
| Xvfb + DOSBox start/stop unattended | verified |
| Windows 3.1 boots; Stars! starts from autoexec | verified (about 3 s from `start` to the first Stars! dialog) |
| Full-window screenshots (1152x864 guest) | verified |
| Keyboard input reaches Windows / Stars! dialogs | verified |
| Mouse move, click, double-click land exactly in Windows | verified (Program Manager menu and icon) |
| Pristine → run copy → snapshot → reset | verified (`selftest`, and real reset between boots) |
| Header decode of real game files | verified (`files` on `stars_games`) |
| Stars! registered | verified: serial accepted, no prompt on relaunch; kept in a local `registered` snapshot |
| PG001 loaded from D: | verified (title "A Barefoot JayWalk", year 2407, Endeavor 48,600) |
| One turn generated, change observed from Linux | verified: `PG001.HST`/`.M1` turn 7 → 8 (2407 → 2408), game 92584875 |
| Normal (non-penalized) growth behavior | verified: 48,600 → 53,500 (penalty would give 51,100), in two independent runs |
| Turn reproducible from reset | verified at UI level (53,500 both runs); file bytes differ by design (per-write salt) |

The About dialog shows the version (2.60j) but neither a registrant nor an
"unregistered" marker, so it does not by itself establish registration; the
growth check does.

## Required apparatus (not in Git)

- `starsbox-macapp.tar.gz`: the macOS `StarsBox.app`. Only its DOS/Windows
  payload is used: `Contents/Resources/c_drive` (Windows 3.1 in `WINDOWS`,
  Stars! in `STARS`, Stars! Notebook in `NOTEBOOK`). The bundled macOS DOSBox
  binary and config are not used.
- `stars_games.tar.gz`: historical game files (`PG000.*`, `PG001.*`,
  `TESTSSG1.*`, `TEST_SS.R1`, `BACKUP/`).
- The Stars! serial number. It is entered into Stars!' first-run dialog, and
  must never be written into the repository, logs, docs, or PRs.

Never commit any of these, or screenshots that show registration details or
proprietary UI unless clearly safe. Raw game files produced by experiments
are evidence and may be committed as fixtures when needed.

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

## Configure and initialize

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
the original `cycles=auto`, and has worked fine so far.

The original `stars_dosbox_macos.conf` targets an SDL2 DOSBox build
(`output=texture`, an SDL2 mapper file), so it is a reference and is not
loaded.

### Deliberate deviation from pristine

At each `start`, if `ORACLE_MOUSE_NOACCEL=1` (the default), `MouseSpeed=0` is
added to the `[windows]` section of the **run copy's** `WINDOWS/WIN.INI`.
This turns off Windows pointer acceleration so that clicks land exactly. It
affects only how the Windows cursor moves, not anything Stars! computes.
`status` reports `WIN.INI` as modified for this reason. After any boot it
also reports `WINDOWS/WIN386.SWP` (the Windows swap file) as modified, and,
after Stars! first runs, `WINDOWS/STARS.INI` as added.

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
scripts/oracle/register SERIAL_FILE   # enter the serial into Stars!' first-run dialog
scripts/oracle/turn GAME.M1           # open a game, generate one turn, exit Stars!
scripts/oracle/stop
```

Screenshots capture the DOSBox window alone, at the guest resolution
(1152x864 with this Windows install). Screenshot pixel coordinates are guest
coordinates.

`start` pins the window at the screen origin (`SDL_VIDEO_WINDOW_POS=0,0`) on
a 1600x1200 Xvfb screen. Otherwise SDL centers the initial 640x400 window and
the window gets clipped when Windows switches to 1152x864.

### Waiting

- The Stars! title screen animates (twinkling stars), so `wait-stable` never
  succeeds while it's visible. Use `wait-for` with a reference crop of the
  expected dialog instead. Make the crop once from a screenshot, e.g.
  `convert shot.png -crop 290x16+440+344 +repage ~/.stars-oracle/refs/serial-dialog-title.png`
  is the title bar of the "Stars! Serial Number" dialog, and
  `convert shot.png -crop 130x20+367+802 +repage ~/.stars-oracle/refs/main-menu-open.png`
  is the "Open Game..." button of the title screen (registered Stars!).
- `wait-stable` suits static screens (Program Manager, Stars! map views).

### Keyboard

Keys go to the focused DOSBox window, and each script focuses it first.
Windows menus open with `alt+<letter>`, and dialogs respond to `Tab`,
`Return`, and `Escape`. Verified in Stars!:

| Keys | Effect |
|---|---|
| `Escape` on the serial dialog | cancels and exits Stars! |
| `alt+o` on the title screen | Open Game dialog, current directory `D:\` |
| type `pg001.m1`, `Return` | loads the game |
| `F9` | Turn → Generate |
| `alt+h` `a` | Help → About Stars! (`Return` there presses "Order Info...", not OK; close with `Escape`) |
| `alt+f` `x` | File → Exit, back to Windows |
| `alt+x` on the title screen | Exit Stars! |

### Mouse

Measured behavior of DOSBox 0.74-3 with this Windows 3.1 install:

- **Unlocked** (DOSBox default after start): host motion is rescaled to a
  640x200 range. Guest movement is about 0.556x horizontally (640/1152) and
  0.23x vertically (200/864), which makes exact positioning impractical.
- **Locked** (DOSBox hotkey `ctrl+F10`): one host pixel of relative motion
  moves the guest cursor exactly one pixel, provided Windows acceleration
  doesn't kick in. With acceleration on, motion arriving faster than the
  guest polls is doubled unpredictably. Turning acceleration off
  (`MouseSpeed=0`, see above) makes it exact at any tested pace.

`click` locks the mouse the first time it runs after `start`; the locked
state is tracked in `state/mouse-locked`. It parks the host pointer at the
bottom-right of the X screen, sweeps the guest cursor past the top-left
corner (Windows pins it at 0,0), then walks to (X,Y) in 8-pixel steps and
clicks. One click takes about 1 s. Accuracy was checked by locating the
cursor in screenshots: (47,31), (600,400), (777,123), and (1000,800) landed
exactly. A click on Program Manager's File menu opened it, and a
double-click on the Stars! icon launched Stars!.

Don't send `ctrl+F10` by hand. It would toggle the lock out of sync with
`state/mouse-locked`.

## Game files

Stars! writes game files to D:, i.e. `run/games/stars_games`, and they are
visible from Linux at once. DOSBox caches directory listings, so files changed
from the Linux side while DOSBox runs might not be seen by the guest. Make
such changes with the oracle stopped.

```sh
scripts/oracle/status   # added / modified / deleted relative to pristine
scripts/oracle/files    # every .HST/.Mn/.Xn/.Hn/.XY in run/, with decoded headers
go run ./cmd/stars-header FILE...                     # the same decode for arbitrary files
go run ./cmd/stars-record -watch DIR -out DIR         # archive every distinct .HST state
```

Only the plaintext file header (game ID, version, turn, year, player) is
decoded today. Later blocks are encrypted and not yet decoded by Elegy.

Pristine `stars_games` state, as decoded by `scripts/oracle/files`:

| Game | ID | Files (turn → year) |
|---|---|---|
| PG001 | 92584875 | `.HST` 7 → 2407, `.M1` 7 → 2407, `.H1` 6 → 2406, `.XY` 0; `BACKUP/` holds 2406 `.HST`/`.M1`/`.X1` |
| PG000 | 7144149 | `.HST`/`.M1` 36 → 2436, `.H1` 35, `.XY`, plus `.MAP`/`.PLA`/`.FLE`/`.R1` exports; `BACKUP/` holds 2435 |
| TESTSSG1 | 290058 | `.HST`/`.M1` 9 → 2409, `.H1` 8, `.XY`; `BACKUP/` holds 2408 |

No `PG001.X1` (orders) exists for 2407, so generating 2408 takes a Stars!
session that opens the player file and submits orders.

Observed when generating PG001 2407 → 2408:

- `PG001.HST` and `PG001.M1` move to turn 8; `PG001.H1` moves to turn 7.
- Stars! itself rewrites `BACKUP/`: it now holds the pre-turn 2407
  `.HST`/`.M1` and the submitted turn-7 `.X1`. `BACKUP/` is Stars!-managed,
  not a static archive.
- File bodies are encrypted with a salt from the file header that changes on
  every write, so two runs of the same turn produce different bytes of equal
  length. Compare runs by decoded content (or the UI), not by hash.
- Header flag bit `0x20` differed between two otherwise identical runs
  (`0xa0` vs `0x80`). Its meaning is unknown.

## Registration

The pristine StarsBox is **not registered**. On first run, Stars! shows a
"Stars! Serial Number" dialog, and Cancel exits Stars! entirely, so no game
can be opened. The bundle's `WINDOWS/SERIALNO.INI` is the Windows 3.1
install record, not Stars! registration.

Register once per pristine base, then keep a snapshot:

```sh
scripts/oracle/reset
scripts/oracle/start
scripts/oracle/wait-for ~/.stars-oracle/refs/serial-dialog-title.png 440 344 120
scripts/oracle/register /path/to/serial.txt
scripts/oracle/wait-for ~/.stars-oracle/refs/main-menu-open.png 367 802 30
scripts/oracle/key alt+x            # exit Stars! so it finishes writing
scripts/oracle/wait-stable 30 2
scripts/oracle/stop
scripts/oracle/snapshot registered  # later: scripts/oracle/reset registered
```

Stars! stores the registration in `C:\WINDOWS\STARS.INI`, encoded (the
serial does not appear there in plaintext), alongside window settings. Treat
that file, and every snapshot containing it, as registration-bearing: it
stays under `$ORACLE_HOME` and is git-ignored.

Before collecting parity data on a new base, re-run the behavioral check:
PG001 is at 2407 with 48,600 colonists and a growth carry of 80
(`docs/PARITY.md`). One turn under normal 10% growth gives
486×10 + 80 = 4,940 → +49 → **53,500** in 2408; the halved 5% penalty would
give 486×5 + 80 = 2,510 → +25 → 51,100. Read the population from the planet
Status panel; Elegy cannot decode it from the `.HST` yet. Observed
2026-10-06: 53,500 (twice).

## Smoke tests

Plumbing only, without apparatus (about 10 s, own temporary `ORACLE_HOME`,
display `:78`):

```sh
scripts/oracle/selftest      # ends with "selftest: PASS"
```

Real apparatus, boot to Stars!:

```sh
scripts/oracle/reset
scripts/oracle/start
scripts/oracle/wait-for ~/.stars-oracle/refs/serial-dialog-title.png 440 344 120
scripts/oracle/screenshot             # Stars! title screen + serial dialog
scripts/oracle/key Escape             # unregistered: Stars! exits to Program Manager
scripts/oracle/click 50 84 1 --double # relaunch Stars! from its icon
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
#   after:  game=92584875 version=2.83.0 turn=8 year=2408 ...
scripts/oracle/stop
scripts/oracle/status                 # PG001.HST/.M1/.H1 and BACKUP/PG001.* modified
scripts/oracle/reset registered       # PG001.HST back at turn 7
```

`turn` takes about 8 s. Run `stars-record` on `run/games/stars_games`
alongside it to keep every `.HST` state.

## Known fragility

- `stop` kills DOSBox outright. Stars! can be mid-write. Exit Stars! cleanly
  or wait for the screen to settle before stopping. Snapshot only while
  stopped.
- A `ctrl+F10` sent before DOSBox finishes starting is lost, so `click`
  locks lazily rather than at `start`.
- No window manager runs: `wmctrl` reports nothing, and `xdotool windowmove`
  doesn't work. Use `xdotool` and `SDL_VIDEO_WINDOW_POS`.
- Keystrokes go to the focused window. Don't run two input scripts at once.
- The xkbcomp warnings in `state/xvfb.log` and the ALSA warning in
  `state/dosbox.log` are harmless.
- One oracle per `ORACLE_DISPLAY`. Use different `ORACLE_HOME` and
  `ORACLE_DISPLAY` values to run several side by side.
