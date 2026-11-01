#!/usr/bin/env bash
set -euo pipefail

CONFIG="$HOME/.config/polybar/config.ini"

killall -q polybar || true

while pgrep -x polybar >/dev/null; do
  sleep 0.1
done

monitors=()
if command -v xrandr >/dev/null 2>&1; then
  while IFS= read -r monitor; do
    monitors+=("$monitor")
  done < <(xrandr --query | awk '/ connected/ { print $1 }')
fi

if [ "${#monitors[@]}" -eq 0 ]; then
  polybar --reload --config="$CONFIG" top &
else
  for monitor in "${monitors[@]}"; do
    MONITOR="$monitor" polybar --reload --config="$CONFIG" top &
  done
fi
