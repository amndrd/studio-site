#!/bin/zsh
# Objects on the desk (step 8), retained 15/11: prototype B "en cours" without the cans and without the cup on the plans
# (the user's Sketchfab picks: the Pente cup under the lamp, two pencils, the eraser, the pen, the small plant on the
# riser, the rhyzome on the plans table). Studio views of the complete desk, then the desk shot in the lab.
# ./rendus-objets.sh sculpture renders the sculpture (kept for the lab decor step) on a museum plinth.
# Before: ../papiers-contenus/capture-emballages.sh, ../textures_objets.py.
# Raw renders in outils/blender/_bruts/objets, finished into bureau/rendus/8-objets by ../finition.py.
# usage: ./rendus-objets.sh [test [views] | sculpture | verif]
cd "$(dirname "$0")"
{ echo "# Objects on the desk (studio). Built by rendus-objets.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' bureau-complet.py; sed '$d' objets-papiers.py; cat objets-poses.py; } > _objets.py
{ echo "# The lab with the desk objects. Built by rendus-objets.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo-objets.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/objets"; mkdir -p "$OUT/labo"; t0=$(date +%s)
case "$1" in
  test)
    $B -b --factory-startup -P _objets.py -- vues=${2:-dessus} res=960 samples=24 out="$OUT/test" > "$OUT/log-test.txt" 2>&1
    echo "$(( $(date +%s) - t0 )) s"; exit ;;
  verif)
    $B -b --factory-startup -P _objets.py -- vues=dessus res=64 samples=1 verif=1 out="$OUT/test" > "$OUT/log-test.txt" 2>&1
    grep "CROISE\|VERIF" "$OUT/log-test.txt"; exit ;;
  sculpture)
    $B -b --factory-startup -P _objets.py -- mode=sculpture vues=sculpture,sculpture-face,sculpture-cote res=1920 samples=160 out="$OUT" > "$OUT/log-sculpture.txt" 2>&1
    $PY -I ../finition.py "$HERO" objets; exit ;;
esac
$B -b --factory-startup -P _objets.py -- vues=ensemble,dessus,lampe,mac,retour,plante res=1920 samples=128 out="$OUT" > "$OUT/log.txt" 2>&1
echo "studio : $(( $(date +%s) - t0 )) s"
$B -b --factory-startup -P _labo-objets.py -- shots=bureau res=1920 samples=96 tag=-B out="$OUT/labo" > "$OUT/log-labo.txt" 2>&1
echo "labo : $(( $(date +%s) - t0 )) s"
$PY -I ../finition.py "$HERO" objets
