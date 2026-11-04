#!/usr/bin/env bash
# Build, validate and export one week's slides.
# Usage: ./build.sh week-01            (scales, the team's style)
#        ./build.sh week-01 all        (all four styles)
#        ./build.sh week-01 terminal   (one other style)
# Needs: npm install (once), LibreOffice, poppler (pdftoppm).
set -euo pipefail
cd "$(dirname "$0")"
WEEK=${1:?usage: ./build.sh week-NN [style ...]}; shift || true
export NODE_PATH="$PWD/node_modules"
PY="${PY:-python3}"
SK=$(ls -d ~/.claude/skills/synced/*/pptx 2>/dev/null | head -1 || true)
[ -f assets/bg-gavel.png ] || node backgrounds.js >/dev/null
for f in $(node deck.js "$WEEK" "$@"); do
  if [ -n "$SK" ]; then
    "$PY" "$SK/scripts/office/validate.py" "$f" | tail -1
    (cd "$(dirname "$f")" && "$PY" "$SK/scripts/office/soffice.py" --headless --convert-to pdf "$(basename "$f")" >/dev/null 2>&1)
  else
    (cd "$(dirname "$f")" && soffice --headless --convert-to pdf "$(basename "$f")" >/dev/null 2>&1)
  fi
  p=preview/$(basename "${f%.pptx}"); mkdir -p "$p"; rm -f "$p"/*.jpg
  pdftoppm -jpeg -r 80 "${f%.pptx}.pdf" "$p/s"
  echo "$f"
done
