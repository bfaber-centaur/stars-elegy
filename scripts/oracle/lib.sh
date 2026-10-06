# shellcheck shell=bash
# Shared configuration and helpers for the Stars! oracle scripts.
#
# Nothing here may name a proprietary file or credential. Apparatus paths come
# from the environment or from $ORACLE_HOME/oracle.conf, which lives outside
# the repository.

set -euo pipefail

ORACLE_HOME="${ORACLE_HOME:-$HOME/.stars-oracle}"
if [[ -f "$ORACLE_HOME/oracle.conf" ]]; then
	# shellcheck disable=SC1091
	source "$ORACLE_HOME/oracle.conf"
fi

ORACLE_DISPLAY="${ORACLE_DISPLAY:-:77}"
ORACLE_SCREEN="${ORACLE_SCREEN:-1600x1200x24}"
ORACLE_DOSBOX="${ORACLE_DOSBOX:-dosbox}"
# Directory (relative to the run copy) mounted as C: by the generated config.
ORACLE_C_DIR="${ORACLE_C_DIR:-}"
# Optional directory (relative to the run copy) mounted as D:, e.g. game files
# kept separate from the application drive.
ORACLE_D_DIR="${ORACLE_D_DIR:-}"
# Optional DOSBox config shipped with the bundle (relative to the run copy).
# When set it is loaded first and the headless overrides are layered on top.
ORACLE_BASE_CONF="${ORACLE_BASE_CONF:-}"
# Extra DOS commands appended to the generated [autoexec], one per line.
ORACLE_AUTOEXEC="${ORACLE_AUTOEXEC:-}"
ORACLE_CYCLES="${ORACLE_CYCLES:-max}"
ORACLE_MACHINE="${ORACLE_MACHINE:-svga_s3}"
ORACLE_MEMSIZE="${ORACLE_MEMSIZE:-16}"
# Turn Windows 3.1 mouse acceleration off in the run copy's WIN.INI
# (MouseSpeed=0) so click lands exactly. Set to 0 to leave WIN.INI untouched.
ORACLE_MOUSE_NOACCEL="${ORACLE_MOUSE_NOACCEL:-1}"
# Relative mouse motion pacing for click (see docs/ORACLE.md, Mouse).
ORACLE_MOUSE_STEP="${ORACLE_MOUSE_STEP:-8}"
ORACLE_MOUSE_PAUSE="${ORACLE_MOUSE_PAUSE:-0.005}"

PRISTINE="$ORACLE_HOME/pristine"
RUN="$ORACLE_HOME/run"
SNAPSHOTS="$ORACLE_HOME/snapshots"
STATE="$ORACLE_HOME/state"
SHOTS="$ORACLE_HOME/shots"

export DISPLAY="$ORACLE_DISPLAY"

die() {
	echo "oracle: $*" >&2
	exit 1
}

log() {
	echo "oracle: $*" >&2
}

pid_alive() {
	local f="$STATE/$1.pid"
	[[ -f "$f" ]] && kill -0 "$(cat "$f")" 2>/dev/null
}

dosbox_window() {
	xdotool search --class dosbox 2>/dev/null | head -n 1
}

require_window() {
	pid_alive dosbox || die "DOSBox is not running (scripts/oracle/start)"
	local w
	w="$(dosbox_window)"
	[[ -n "$w" ]] || die "DOSBox window not found on $DISPLAY"
	echo "$w"
}

focus_window() {
	local w
	w="$(require_window)"
	xdotool windowfocus --sync "$w" 2>/dev/null || xdotool windowfocus "$w"
	echo "$w"
}

# manifest DIR: one "sha256  relative/path" line per regular file, sorted.
manifest() {
	(cd "$1" && find . -type f -print0 | sort -z | xargs -0 -r sha256sum)
}
