#!/bin/zsh
# Builds the packaging pages (emballages.py: cans Ampère, Nord, Minuit; the Pente stamp of the cup sleeve) and
# screenshots them with a transparent background into captures/. Then ../textures_objets.py makes the textures.
# usage: ./capture-emballages.sh [python]
cd "$(dirname "$0")"
PY=${1:-python3}
$PY -I emballages.py || exit 1
python3 -m http.server 8772 --bind 127.0.0.1 > /dev/null 2>&1 &
SRV=$!
sleep 1
cap() { node capture-emballages.mjs "http://127.0.0.1:8772/pages/$1.html" "captures/$1.png" $2 $3 $4 | tail -1; }
cap emb-ampere 1806 1165 1.5
cap emb-minuit 1806 1165 1.5
cap emb-nord 2045 956 1.4
cap emb-pente 2730 420 1.2
kill $SRV
