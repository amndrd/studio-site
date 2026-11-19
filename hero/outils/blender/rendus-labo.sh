#!/bin/zsh
# The lab with every retained choice (steel-frame hall, light mix D, desk D, storage N, chair Mandy,
# workstation B2, desk lamp on three classics, storage contents M, papers M): wide axial shot, zones, desk lamp, top view.
# Raw renders in outils/blender/_bruts/labo, finished into labo/rendus by ../finition.py.
# usage: ./rendus-labo.sh [test]
cd "$(dirname "$0")"
{ echo "# The lab (retained choices). Built by rendus-labo.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/labo"; mkdir -p "$OUT"; t0=$(date +%s)
if [[ "$1" == test ]]; then
  $B -b --factory-startup -P _labo.py -- shots=${2:-bureau} res=900 samples=24 out="$OUT/test" > "$OUT/log-test.txt" 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
run() { $B -b --factory-startup -P _labo.py -- "$@" out="$OUT" > "$OUT/log-${1#shots=}.txt" 2>&1; echo "$1 : $(( $(date +%s) - t0 )) s"; }
run shots=axe,bureau,lampe,corbeille res=1920 samples=96
run shots=projets,atelier res=1920 samples=96
run shots=serveurs,ventilo res=1920 samples=96
run shots=plan res=1600 samples=48
$PY -I ../finition.py "$HERO" labo
