#!/bin/zsh
# The floor of the desk corner, retained 16/11: no floor covering, the desk stands on the lab's wet concrete; the
# perforated bin of objets-sol.py replaces the grey placeholder. Renders the wide axial shot and the desk shot of the lab
# (with every retained choice, same build as rendus-labo.sh) and the bin in the studio (bureau-complet, view corbeille),
# then finishes them into bureau/rendus/9-sol (and the two lab views into labo/rendus) with ../finition.py.
# usage: ./rendus-sol.sh [test]
cd "$(dirname "$0")"
{ echo "# The lab (retained choices). Built by rendus-sol.sh."; cat labo2-base.py; sed '$d' labo2-v2.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat labo3-v3.py; } > _labo.py
{ echo "# The whole desk corner (studio). Built by rendus-sol.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; cat bureau-complet.py; } > _bureau-complet.py
B=/Applications/Blender.app/Contents/MacOS/Blender
PY=${PY:-python3}
HERO="$PWD/../.."; mkdir -p _bruts/labo _bruts/complet _bruts/sol; t0=$(date +%s)
if [[ "$1" == test ]]; then
  $B -b --factory-startup -P _labo.py -- shots=bureau res=900 samples=24 out="$PWD/_bruts/sol/test" > _bruts/sol/log-test.txt 2>&1
  $B -b --factory-startup -P _bureau-complet.py -- vues=corbeille res=900 samples=24 out="$PWD/_bruts/sol/test" >> _bruts/sol/log-test.txt 2>&1
  echo "$(( $(date +%s) - t0 )) s"; exit
fi
$B -b --factory-startup -P _labo.py -- shots=axe,bureau,corbeille res=1920 samples=96 out="$PWD/_bruts/labo" > _bruts/sol/log-labo.txt 2>&1
echo "labo : $(( $(date +%s) - t0 )) s"
$B -b --factory-startup -P _bureau-complet.py -- vues=corbeille res=1920 samples=160 out="$PWD/_bruts/complet" > _bruts/sol/log-studio.txt 2>&1
echo "studio : $(( $(date +%s) - t0 )) s"
$PY -I ../finition.py "$HERO" labo
$PY -I ../finition.py "$HERO" sol
