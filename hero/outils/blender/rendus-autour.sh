#!/bin/zsh
# The decor around the desk (step 10), retained 16/11: D sobre (two cartons, the white table fan on top) and the mesh
# bin. Studio views on the complete desk (every retained choice), then the desk shot, the wide axial shot and the bin at
# floor level in the lab. Raw renders in outils/blender/_bruts/autour, finished into bureau/rendus/10-autour.
# usage: ./rendus-autour.sh [test [views] | verif | labo-test [shots] | labo]
cd "$(dirname "$0")"
{ echo "# The decor around the desk (studio). Built by rendus-autour.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' bureau-complet.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; cat objets-autour.py; } > _autour.py
{ echo "# The lab with the decor around the desk. Built by rendus-autour.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo-autour.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/autour"; mkdir -p "$OUT/labo"; t0=$(date +%s)
case "$1" in
  test)
    $B -b --factory-startup -P _autour.py -- vues=${2:-large} res=960 samples=24 out="$OUT/test" "${@:3}" > "$OUT/log-test.txt" 2>&1
    echo "$(( $(date +%s) - t0 )) s"; exit ;;
  verif)
    $B -b --factory-startup -P _autour.py -- rendu=0 verif=1 out="$OUT/test" > "$OUT/log-verif.txt" 2>&1
    $B -b --factory-startup -P _labo-autour.py -- shots=bureau res=64 samples=1 verif=1 out="$OUT/test" > "$OUT/log-verif-labo.txt" 2>&1
    grep -h "CROISE\|Traceback" "$OUT"/log-verif*.txt; echo "$(( $(date +%s) - t0 )) s"; exit ;;
  labo-test)
    $B -b --factory-startup -P _labo-autour.py -- shots=${2:-bureau} res=960 samples=24 tag=-D out="$OUT/test" > "$OUT/log-labo-test.txt" 2>&1
    echo "$(( $(date +%s) - t0 )) s"; exit ;;
esac
if [[ "$1" != labo ]]; then
  $B -b --factory-startup -P _autour.py -- res=1920 samples=128 out="$OUT" > "$OUT/log.txt" 2>&1
  echo "studio : $(( $(date +%s) - t0 )) s"
fi
$B -b --factory-startup -P _labo-autour.py -- shots=bureau,axe,corbeille res=1920 samples=96 tag=-D out="$OUT/labo" > "$OUT/log-labo.txt" 2>&1
echo "labo : $(( $(date +%s) - t0 )) s"
$PY -I ../finition.py "$HERO" autour
