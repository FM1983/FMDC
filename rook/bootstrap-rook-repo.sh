#!/usr/bin/env bash
# Seed the FM1983/rook build repo from the FMDC checkout.
# Needs: gh (authenticated) + git. Safe to re-run.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"

gh repo create FM1983/rook --private \
  --description "Rook — the Citadel command app. Native iPhone board console: option cards, dispatch, voice, push. Build per SPEC.md." \
  2>/dev/null && echo "created FM1983/rook" || echo "FM1983/rook already exists — seeding"

TMP="$(mktemp -d)"
git clone "https://github.com/FM1983/rook.git" "$TMP/rook"
cd "$TMP/rook"

cp "$SRC/SPEC.md" SPEC.md
cp "$SRC/CURSOR.md" CURSOR.md
mkdir -p .cursor/rules
cp "$SRC/rook.mdc" .cursor/rules/rook.mdc

cat > README.md <<'MD'
# Rook

The Citadel command app — the GODS-EYE board as an operable queue, native on the
iPhone: categorised checkbox option cards, context on tap with click-through to
every referenced file, dispatch staging with human-tap release, voice, and push.

- **SPEC.md** — the operative contract (v2.1, requirements P1–P20 with provenance)
- **CURSOR.md** — the working brief: kickoff prompt + phase-by-phase gates
- **.cursor/rules/rook.mdc** — non-negotiable rules every Cursor session is bound to

Start: open this repo in Cursor and paste the kickoff prompt from CURSOR.md §1.
Phase 0 gate requires the Apple Developer account for capital.citadel (APNs + TestFlight).

Confidential — internal.
MD

cat > .gitignore <<'GI'
node_modules/
.expo/
dist/
build/
*.log
.env
.env.*
*.p8
*.db
*.sqlite
.DS_Store
GI

git add -A
if git diff --cached --quiet; then echo "nothing new to commit"; else
  git commit -m "Seed Rook build repo: SPEC v2.1, Cursor brief and rules"
fi
git branch -M main
git push -u origin main
echo "Done: https://github.com/FM1983/rook"
