#!/bin/zsh
# Storage contents, retained mix M (2026-11-15): studio views of the four storage pieces, the desk and the riser,
# then the desk shot and a low shot of the storage in the lab (with the LED strips under the desk, option ledsous=1).
# The prototypes A|B|C|D are still options (contenus=A,B,C,D in the studio, contenu=A in the lab).
# Raw renders in outils/blender/_bruts/contenus, finished into bureau/rendus/6-contenu-rangements by ../finition.py.
# usage: ./rendus-contenus.sh [test [contenus] [views]]   |   ./rendus-contenus.sh labo-test [shots]
cd "$(dirname "$0")"
{ echo "# Storage contents (studio). Built by rendus-contenus.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; cat objets-contenus.py; } > _contenus.py
{ echo "# The lab with the storage contents. Built by rendus-contenus.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo-contenus.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; OUT="$PWD/_bruts/contenus"; mkdir -p "$OUT/labo"; t0=$(date +%s)
if [[ "$1" == test ]]; then
  $B -b --factory-startup -P _contenus.py -- contenus=${2:-M} vues=${3:-grp} res=960 samples=24 out="$OUT/test" > "$OUT/log-test.txt" 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
if [[ "$1" == labo-test ]]; then
  $B -b --factory-startup -P _labo-contenus.py -- shots=${2:-bureau} res=960 samples=24 tag=-M out="$OUT/test" "${@:3}" > "$OUT/log-labo-test.txt" 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
$B -b --factory-startup -P _contenus.py -- contenus=M vues=grp,ouvert,tiroirs,desserte,bur,rehausse res=1920 samples=128 out="$OUT" > "$OUT/log.txt" 2>&1
echo "studio : $(( $(date +%s) - t0 )) s"
$B -b --factory-startup -P _labo-contenus.py -- shots=bureau,rangements res=1920 samples=96 tag=-M out="$OUT/labo" > "$OUT/log-labo-M.txt" 2>&1
echo "labo : $(( $(date +%s) - t0 )) s"
$PY -I ../finition.py "$HERO" contenus
