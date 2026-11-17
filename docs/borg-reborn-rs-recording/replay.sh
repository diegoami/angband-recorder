#!/usr/bin/env bash
# Replay a recording and compare it:  replay.sh RECORDING_DIR OUT_DIR SEED RACE CLASS TURNS
# Assumes the recording used run-env.sh and harness/run.sh flags menu,terminal-save
# (the replay's arguments must match the recording's; see RECORDING_DIR/process.json "command").
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ $# -eq 6 ] || { echo "usage: replay.sh RECORDING_DIR OUT_DIR SEED RACE CLASS TURNS" >&2; exit 2; }
D="$(realpath "$1")"; R="$(realpath -m "$2")"; SEED=$3 RACE=$4 CLASS=$5 TURNS=$6
[ ! -e "$R" ] || { echo "replay.sh: $R exists" >&2; exit 2; }
source "$HERE/run-env.sh"
mkdir -p "$R"/{user,save,archive,panic,scores,checkpoints}
cp "$D/user/borg.txt" "$R/user/"
if [ -f "$D/user/errands_plan.txt" ]; then cp "$D/user/errands_plan.txt" "$R/user/"; fi
cd "$BRR_BUILD/build/rec/game"
# BORG_ERRANDS_PLAN stays unset: run.sh does not pass it to the game, which reads the plan from borg.txt.
flock /tmp/angband-validation.lock env -u BORG_RECORD_DIR -u BORG_TOOLKIT_NATIVE -u BORG_ERRANDS_PLAN \
  -u CHECKPOINT_EVERY -u ANGBAND_BIN \
  ANGBAND_REPLAY_DIR="$D/native" ANGBAND_RECORD_DIR="$R/native" BORG_TOOLKIT_HEADLESS=1 BORG_RUN_DIR="$R" \
  BORG_PROFILE="$BRR_BUILD/harness/profiles/reborn-default.txt" BORG_PROFILE_NAME=harness/profiles/reborn-default.txt \
  TZ=UTC LANG=C.UTF-8 LC_ALL=C.UTF-8 ./angband -mborgh -n -uBorg \
  -duser="$R/user" -dsave="$R/save" -darchive="$R/archive" -dpanic="$R/panic" -dscores="$R/scores" -- \
  -seed "$SEED" -race "$RACE" -class "$CLASS" -turns "$TURNS" -keylog "$R/keys.log" -msglog "$R/messages.log" \
  -statelog "$R/state.log" -summary "$R/summary.json" -screen -menu-letters -save-final-state "$R/final.save" \
  -checkpoint-every 50000 -checkpoint-dir "$R/checkpoints" > "$R/stderr.log" 2>&1 \
  || echo "replay.sh: game exited with rc=$?; see $R/stderr.log"
for f in keys.log state.log final.save; do cmp -s "$D/$f" "$R/$f" && echo "$f identical" || echo "$f DIFFERS"; done
