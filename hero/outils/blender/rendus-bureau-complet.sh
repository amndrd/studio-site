#!/bin/zsh
# The whole desk corner in the studio, without the lab: every retained choice of the desk detail pass
# (desk, storage and contents, LED strips, workstation B2, lamp on three books, chair Mandy).
# Raw renders in outils/blender/_bruts/complet, finished into bureau/rendus/bureau-complet by ../finition.py.
# usage: ./rendus-bureau-complet.sh [test [views]]
cd "$(dirname "$0")"
{ echo "# The whole desk corner (studio). Built by rendus-bureau-complet.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat bureau-complet.py; } > _bureau-complet.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/complet"; mkdir -p "$OUT"; t0=$(date +%s)
if [[ "$1" == test ]]; then
  $B -b --factory-startup -P _bureau-complet.py -- vues=${2:-ensemble} res=960 samples=24 out="$OUT/test" > "$OUT/log-test.txt" 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
$B -b --factory-startup -P _bureau-complet.py -- vues=ensemble,poste,face,droite res=1920 samples=160 out="$OUT" > "$OUT/log.txt" 2>&1
echo "studio : $(( $(date +%s) - t0 )) s"
$PY -I ../finition.py "$HERO" complet
