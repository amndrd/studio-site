#!/bin/zsh
# The cables of the desk corner (step 11), retained 17/11: B le long du pied, the fan's cable par le bureau (white).
# Studio views of the complete desk (every retained choice); the lab views come from rendus-labo.sh (_bruts/labo).
# Raw renders in outils/blender/_bruts/cables, finished into bureau/rendus/11-cables by ../finition.py cables.
# usage: ./rendus-cables.sh [test [views] | verif | labo-test [shots]]
cd "$(dirname "$0")"
{ echo "# The cables of the desk corner (studio). Built by rendus-cables.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' bureau-complet.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; cat objets-cables.py; } > _cables.py
{ echo "# The lab with the cables of the desk corner. Built by rendus-cables.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo-cables.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/cables"; mkdir -p "$OUT/labo"; t0=$(date +%s)
case "$1" in
  test)
    $B -b --factory-startup -P _cables.py -- vues=${2:-ensemble} res=960 samples=24 out="$OUT/test" "${@:3}" > "$OUT/log-test.txt" 2>&1
    echo "$(( $(date +%s) - t0 )) s"; exit ;;
  verif)
    $B -b --factory-startup -P _cables.py -- rendu=0 verif=1 out="$OUT/test" > "$OUT/log-verif.txt" 2>&1
    $B -b --factory-startup -P _labo-cables.py -- shots=bureau res=64 samples=1 verif=1 tag=-verif out="$OUT/test" > "$OUT/log-verif-labo.txt" 2>&1
    grep -h "CABLE\|Traceback\|Error:" "$OUT"/log-verif*.txt; echo "$(( $(date +%s) - t0 )) s"; exit ;;
  labo-test)
    $B -b --factory-startup -P _labo-cables.py -- shots=${2:-bureau} res=960 samples=24 out="$OUT/test" > "$OUT/log-labo-test.txt" 2>&1
    echo "$(( $(date +%s) - t0 )) s"; exit ;;
esac
$B -b --factory-startup -P _cables.py -- vues=ensemble,dessous,arriere,multiprise,fil,bras,mac,lampe res=1920 samples=128 out="$OUT" > "$OUT/log.txt" 2>&1
echo "studio : $(( $(date +%s) - t0 )) s"
$PY -I ../finition.py "$HERO" cables
