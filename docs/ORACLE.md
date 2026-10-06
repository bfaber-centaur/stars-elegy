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

| Capability | State |
|---|---|
| Xvfb + DOSBox start/stop unattended | verified (`selftest`) |
| Screenshot of the DOSBox window | verified (`selftest`) |
| Keyboard injection reaches the guest | verified (`selftest`, DOS shell) |
| Guest file writes visible from Linux immediately | verified (`selftest`) |
| Pristine → run copy → snapshot → reset | verified (`selftest`) |
| Header decode of produced game files | verified (`selftest`, synthetic file) |
| Host pointer placement for `click` | verified at X11 level only |
| Mouse clicks land correctly in Windows 3.1 | **not yet verified** |
| Windows 3.1 / Stars! J-RC3 boot | **not yet verified** (no apparatus supplied so far) |
| Existing universe loaded, turn generated | **not yet verified** |
| Normal registration behavior | **not yet verified** |

Do not collect parity data until the last three rows are verified, and record
the commit and date when they are.

## Required apparatus (not in Git)

- A StarsBox-style bundle: Windows 3.1 installed on a DOSBox C: drive
  (a directory), with Stars! J-RC3 installed. It may come with its own
  DOSBox config.
- Optionally, a separate oracle drive containing existing test universes.
- Registration information for Stars!, if the bundle doesn't already contain it.

Never commit any of these, or screenshots and logs that show registration
details. Raw `.HST` and other game files produced by experiments are evidence
and may be committed as fixtures when needed.

Linux packages (installed by the environment setup script): `dosbox` (0.74-3
tested), `xvfb`, `xdotool`, `imagemagick`, `x11-utils`, `unzip`, `p7zip-full`,
plus Go for the inspection tools.

## Layout

```text
$ORACLE_HOME/
├── oracle.conf          local configuration (see oracle.conf.example)
├── sources.txt          SHA-256 of the supplied archives
├── pristine/            unpacked apparatus, read-only
├── pristine.sha256      manifest of pristine/
├── run/                 disposable copy that DOSBox actually uses
├── snapshots/NAME/      saved run copies, read-only
├── state/               pid files, logs, generated DOSBox config
└── shots/               screenshots
```

The read-only bits protect against accidents, not against root: the container
runs as root, which ignores them. Keep the supplied archives themselves
untouched; `setup --force` can always rebuild `pristine/` from them.

## Configure

```sh
mkdir -p ~/.stars-oracle
cp scripts/oracle/oracle.conf.example ~/.stars-oracle/oracle.conf
$EDITOR ~/.stars-oracle/oracle.conf
```

Choose one of two ways to boot:

- **Generated config:** `ORACLE_C_DIR` names the directory (relative to
  `run/`) to mount as C:, and `ORACLE_AUTOEXEC` lists the DOS commands that
  start Windows, e.g. `win`, or `win stars!` to launch Stars! directly.
- **Bundle config:** `ORACLE_BASE_CONF` names the bundle's own DOSBox config
  (relative to `run/`). DOSBox runs with `run/` as its working directory, so
  relative mount paths in that config still resolve. The headless overrides in
  `state/overrides.conf` are loaded after it. A config written for DOSBox-X or
  DOSBox Staging may need hand-editing for 0.74.

Each variable can also be set in the environment for a single command.

## Initialize and reset

```sh
scripts/oracle/setup --bundle /path/to/StarsBox.zip [--drive /path/to/oracle-drive.zip --drive-dest REL]
scripts/oracle/reset              # run/ := pristine/
scripts/oracle/snapshot NAME      # save run/ (oracle must be stopped)
scripts/oracle/reset NAME         # run/ := snapshots/NAME
```

`setup` accepts a directory, `.zip`, `.7z`, or tar archive, and only reads it.
`--drive-dest` (default `drive`) says where in `pristine/` the oracle drive
goes. If the bundle expects its universes inside its C: drive, point
`--drive-dest` at that directory.

`reset` stops a running oracle first. Reset before every experiment, and take
a snapshot at each state you will want to return to, such as "universe loaded,
turn 2400, orders not yet given".

## Start, observe, operate, stop

```sh
scripts/oracle/start                  # Xvfb + DOSBox, detached; waits for the window
scripts/oracle/status                 # processes, window title, changes vs pristine
scripts/oracle/screenshot [OUT.png]   # prints the PNG path
scripts/oracle/wait-stable [TIMEOUT] [QUIET]   # waits until the screen stops changing
scripts/oracle/key alt+f Down Return  # xdotool keysyms, sent in order
scripts/oracle/type 'win'             # literal text, no Return
scripts/oracle/click X Y [BUTTON] [--double]   # guest coordinates from a screenshot
scripts/oracle/stop
```

Screenshots are taken of the DOSBox window alone, so screenshot pixel
coordinates are guest screen coordinates (no scaler is applied).

Prefer the keyboard. Windows 3.1 menus open with `alt+<letter>`, dialogs
respond to `Tab`, `Return`, and `Escape`, and Stars! has many accelerator keys.

### Mouse

Under DOSBox the Windows mouse is relative. The host pointer position doesn't
map onto it. `click` therefore drives the guest cursor into the top-left
corner, where Windows pins it at (0,0), then moves to the target in steps of
3 pixels or fewer. Two things must hold for this to be exact:

1. Windows mouse acceleration is off (Control Panel → Mouse: slowest tracking
   speed, or `MouseSpeed=0` in `[windows]` of `WIN.INI`).
2. `ORACLE_MOUSE_SCALE` is the number of guest pixels moved per host pixel.
   Leave it at 1, then click a known control and check with a screenshot. If
   the cursor falls short or overshoots by a constant factor, set the scale to
   that factor.

Mouse capture (`autolock`) is disabled, so motion reaches the guest without
clicking into the window first.

### Wait before acting

DOSBox and Windows take a while to boot and repaint. Use `wait-stable` after
every action that changes the screen, and look at the screenshot it prints
before deciding on the next input.

## Game files

Stars! writes into `run/` and the files are visible from Linux at once.
DOSBox caches directory listings, though, so files changed from the Linux side
while DOSBox runs might not be seen by the guest. Make such changes with the
oracle stopped, or run `rescan` at a DOS prompt.

```sh
scripts/oracle/status   # added / modified / deleted relative to pristine
scripts/oracle/files    # every .HST/.Mn/.Xn/.Hn/.XY in run/, with decoded headers
go run ./cmd/stars-header FILE...      # the same decode for arbitrary files
go run ./cmd/stars-record -watch DIR -out DIR   # archive every distinct .HST state (docs/HST_RECORDER.md)
```

Only the plaintext file header (game ID, version, turn, year, player) is
decoded today. Later blocks are encrypted and not yet decoded by Elegy.

For an experiment that spans several turns, run `stars-record` against the
game directory inside `run/` while the oracle is running, so every
intermediate `.HST` state is preserved.

## Verifying registration

The oracle is only trustworthy when Stars! runs with normal registered
behavior. PARITY.md records that an unregistered or penalized run halved
effective population growth (10% → 5%). Before collecting data:

1. Check what Stars! reports about registration (the Help/About dialog) with
   a screenshot. Inspect it locally and do not commit it if it shows the
   name or serial.
2. Run a behavioral check: take a 10%-growth race at 100% habitability below
   25% capacity for one turn and confirm the growth matches PG-001 (25,000 →
   27,500 from a zero carry), not half of it.

If either check is ambiguous, stop and treat the oracle as untrusted.

## Smoke tests

Plumbing (no apparatus required, about 10 seconds). It runs on its own
temporary `ORACLE_HOME` and display `:78`:

```sh
scripts/oracle/selftest      # ends with "selftest: PASS"
```

Full oracle (requires apparatus and a configured `oracle.conf`):

```sh
scripts/oracle/setup --bundle /path/to/bundle [--drive /path/to/drive]
scripts/oracle/reset
scripts/oracle/start
scripts/oracle/wait-stable 120 5      # Windows / Stars! has booted; inspect the PNG
# Open a known universe and generate one turn, using key/type/click and
# checking each step with wait-stable.
scripts/oracle/wait-stable 120 5
scripts/oracle/stop
scripts/oracle/status                 # the universe's .HST should be "modified"
scripts/oracle/files                  # its year should be one more than before
scripts/oracle/reset                  # back to pristine
```

When this passes, write down the exact keystrokes it took next to the
universe's name here, so later workers can replay them.

## Known fragility

- Timing: Windows boot and turn generation take an unknown time under
  `cycles=max` on a shared VM. Always use `wait-stable`; never fixed sleeps.
- `stop` kills DOSBox outright. Stars! can be mid-write. Exit Stars! cleanly
  or wait for the screen to settle before stopping. Snapshot only while
  stopped.
- No window manager runs, so `wmctrl` has nothing to report. Use `xdotool`.
  `xdotool windowmove` has no effect on the DOSBox window either.
- Keystrokes go to the focused window. `key`, `type`, and `click` focus
  DOSBox first. Don't run two of them at once.
- The xkbcomp warnings in `state/xvfb.log` are harmless.
- One oracle per `ORACLE_DISPLAY`. Use different `ORACLE_HOME` and
  `ORACLE_DISPLAY` values to run several side by side.
