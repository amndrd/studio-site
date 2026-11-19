#!/bin/zsh
# Papers on the desk (option papiers=M, the B + C mix of 15/11): the complete desk corner in the studio
# (ensemble, top view, lamp zone, return, workstation, books under the lamp), then the desk shot in the lab.
# Before: ../papiers-contenus/capture.sh, ../textures_papiers.py, ../textures_livres.py, rendus-fictifs.sh.
# Raw renders in outils/blender/_bruts/papiers, finished into bureau/rendus/7-papiers by ../finition.py.
# usage: ./rendus-papiers.sh [test [pistes] [views]]   |   ./rendus-papiers.sh labo-test [piste]
cd "$(dirname "$0")"
{ echo "# Papers on the desk (studio). Built by rendus-papiers.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' bureau-complet.py; cat objets-papiers.py; } > _papiers.py
{ echo "# The lab with the papers. Built by rendus-papiers.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo-papiers.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/papiers"; mkdir -p "$OUT/labo"; t0=$(date +%s)
if [[ "$1" == test ]]; then
  $B -b --factory-startup -P _papiers.py -- pistes=${2:-M} vues=${3:-lampe} res=960 samples=24 out="$OUT/test" > "$OUT/log-test.txt" 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
if [[ "$1" == labo-test ]]; then
  $B -b --factory-startup -P _labo-papiers.py -- shots=bureau res=960 samples=24 papiers=${2:-M} tag=-${2:-M} out="$OUT/test" > "$OUT/log-labo-test.txt" 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
$B -b --factory-startup -P _papiers.py -- pistes=M vues=ensemble,dessus,lampe,retour,poste,livres res=1920 samples=128 out="$OUT" > "$OUT/log.txt" 2>&1
echo "studio : $(( $(date +%s) - t0 )) s"
for k in M; do
  $B -b --factory-startup -P _labo-papiers.py -- shots=bureau res=1920 samples=96 papiers=$k tag=-$k out="$OUT/labo" > "$OUT/log-labo-$k.txt" 2>&1
  echo "labo $k : $(( $(date +%s) - t0 )) s"
done
$PY -I ../finition.py "$HERO" papiers
