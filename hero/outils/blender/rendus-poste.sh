#!/bin/zsh
# The retained workstation (setup B2: two 27" screens on a dual arm, MacBook Pro, keyboard, mouse, AirPods,
# Mac Studio, power strip): studio views, then the desk shot and the wide shot in the lab.
# Raw renders in outils/blender/_bruts/poste, finished into bureau/rendus/4-poste by ../finition.py.
# usage: ./rendus-poste.sh [test [views]]
cd "$(dirname "$0")"
{ echo "# Workstation B2 (studio). Built by rendus-poste.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; echo "main_ecrans()"; } > _poste.py
{ echo "# The lab (retained choices). Built by rendus-poste.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/poste"; mkdir -p "$OUT"; t0=$(date +%s)
if [[ "$1" == test ]]; then
  $B -b --factory-startup -P _poste.py -- setups=B2 vues=${2:-face,mac,objets} res=900 samples=24 out="$OUT/test" > "$OUT/log-test.txt" 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
$B -b --factory-startup -P _poste.py -- setups=B2 vues=tq,face,det,mac,objets,clavier res=1920 samples=160 out="$OUT" > "$OUT/log.txt" 2>&1
echo "studio : $(( $(date +%s) - t0 )) s"
$B -b --factory-startup -P _labo.py -- shots=bureau,axe res=1920 samples=96 tag=-B2 out="$OUT/labo" > "$OUT/log-labo.txt" 2>&1
echo "labo : $(( $(date +%s) - t0 )) s"
$PY -I ../finition.py "$HERO" poste
