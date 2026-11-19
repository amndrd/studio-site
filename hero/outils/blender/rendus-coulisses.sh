#!/bin/zsh
# Behind the scenes (17/11): captures of the Blender scene of the complete desk (hero/bureau/scene/bureau-complet.blend) in a
# SECOND Blender with its interface (it opens a window and closes it itself; the user's Blender is not touched).
# ui  = screenshots of the interface (16:9 window 1484 x 850 pt, 4:5 window 668 x 850 pt, Retina x2);
# net = the same cameras without interface: wireframe, clay, material preview (render.opengl) and the Cycles render.
# Raw images in outils/blender/_bruts/coulisses; ../coulisses_mise_en_page.py files them into bureau/coulisses (A, C).
# usage: ./rendus-coulisses.sh [ui|net] [169|45] [vues=a,b]   (no argument: everything)
cd "$(dirname "$0")"
B=/Applications/Blender.app/Contents/MacOS/Blender
SCENE="$PWD/../../bureau/scene/bureau-complet.blend"
OUT="$PWD/_bruts/coulisses"; mkdir -p "$OUT"; t0=$(date +%s)
run() {   # job format [only=...]
  local geo="0 0 1484 850"; [[ "$2" == 45 ]] && geo="0 0 668 850"
  perl -e 'alarm 1800; exec @ARGV' $B --factory-startup "$SCENE" --window-geometry ${=geo} --python coulisses.py -- job=$1 format=$2 out="$OUT" "${@:3}" > "$OUT/stdout-$1-$2.txt" 2>&1
  echo "$1 $2 : $(( $(date +%s) - t0 )) s"
  if grep -qi "traceback" "$OUT/log-$1-$2.txt"; then tail -8 "$OUT/log-$1-$2.txt"; fi
  return 0
}
if [[ -n "$1" ]]; then run "$1" "${2:-169}" "${@:3}"; exit; fi
run ui 169
run ui 45
run net 169
run net 45
