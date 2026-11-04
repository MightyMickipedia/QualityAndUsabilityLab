#!/usr/bin/env bash
# Build and check one week's slides.
# Usage: ./build.sh week-01
# Writes presentations/week-01/week-01.pptx; a PDF and preview images go to build/preview/ (not committed).
# Needs: npm install (once), LibreOffice, poppler (pdftoppm).
set -euo pipefail
cd "$(dirname "$0")"
WEEK=${1:?usage: ./build.sh week-NN}
export NODE_PATH="$PWD/node_modules"
PY="${PY:-python3}"
SK=$(ls -d ~/.claude/skills/synced/*/pptx 2>/dev/null | head -1 || true)
[ -f assets/bg-scales.png ] || node backgrounds.js >/dev/null
f=$(node deck.js "$WEEK")
[ -n "$SK" ] && "$PY" "$SK/scripts/office/validate.py" "$f" | tail -1
p="$PWD/preview/$WEEK"; mkdir -p "$p"; rm -f "$p"/*
soffice --headless --convert-to pdf --outdir "$p" "$f" >/dev/null 2>&1
pdftoppm -jpeg -r 80 "$p/$WEEK.pdf" "$p/s"
echo "$f"
