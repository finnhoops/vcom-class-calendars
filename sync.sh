#!/bin/bash
# ---------------------------------------------------------------------------
# Rebuild every classmate calendar from Anna's current build and publish.
#
# Run this AFTER Anna's calendar has been updated (its build/index.html is the
# source every classmate page is derived from). Normally you don't call this
# directly -- ../update-calendars.sh does it for you.
#
#   ./sync.sh                 rebuild all, commit, push
#   ./sync.sh "reason text"   use that as the commit message
# ---------------------------------------------------------------------------
set -uo pipefail
cd "$(dirname "$0")" || exit 1

MSG="${1:-Schedule update $(date +%Y-%m-%d)}"
SRC="../ANNA VCOM calendar/repo/build/index.html"

[ -f "$SRC" ] || { echo "STOP: can't find Anna's build at $SRC"; exit 1; }

echo "=== Pulling latest ==="
git pull -q --rebase || { echo "STOP: git pull failed — resolve that first."; exit 1; }

echo "=== Rebuilding every calendar ==="
python3 derive.py --all || { echo "STOP: derive.py failed (see message above)."; exit 1; }

git add -A
if git diff --cached --quiet; then
  echo "Nothing changed — the classmate calendars already match Anna's. Not pushing."
  exit 0
fi

git commit -q -m "$MSG" || { echo "STOP: commit failed."; exit 1; }
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if ! git push origin "$BRANCH"; then
  echo "Built and committed fine, but the push failed."
  echo "Nothing lost — fix the connection and run:  git push origin $BRANCH"
  exit 1
fi

echo
echo "Pushed. Vercel redeploys every classmate calendar in under a minute."
python3 - <<'PY'
import json, pathlib
reg = json.loads(pathlib.Path("registry.json").read_text())
site = reg.get("site", "vcom-class-calendars.vercel.app")
print(f"\n{len(reg['calendars'])} calendars live on https://{site} :")
for c in reg["calendars"]:
    name = c.get("label") or f"{c['name']}’s Calendar"
    path = c.get("path", f"/{c['slug']}")
    print(f"  {name:<22} https://{site}{'' if path == '/' else path}")
PY
