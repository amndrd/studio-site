#!/bin/zsh
# Builds the document pages (documents.py) and screenshots them at print resolution into captures/.
# Needs Playwright from ~/Desktop/Portfolio/tools (capture.mjs). usage: ./capture.sh [python]
cd "$(dirname "$0")"
PY=${1:-python3}
$PY -I documents.py || exit 1
python3 -m http.server 8771 --bind 127.0.0.1 > /dev/null 2>&1 &
SRV=$!
sleep 1
cap() { node capture.mjs "http://127.0.0.1:8771/pages/$1.html" "captures/$1.png" $2 $3 $4 0 | tail -1; }
cap plan-rdc 1684 1191 2
cap coupe-aa 1191 842 2.5
cap halde-sitemap 1191 842 2.2
cap halde-materiaux 1191 842 2.2
cap devis 595 842 2.5
cap ombelle-accueil 842 1191 2.2
cap ombelle-mobile 842 595 2.5
cap ombelle-charte 595 842 2.5
cap code 595 842 2.5
kill $SRV
