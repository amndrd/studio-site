#!/bin/zsh
# The construction video of the desk (prototypes): the complete desk built by the same modules as
# rendus-bureau-complet.sh, then video/trace.py (which build call made each object), video/construction.py (stages,
# materials, wireframe twins, modelling, schedule) and video/main.py (tests, cameras, render).
# Frames in outils/blender/_bruts/video/<test>/<style>/, assembled into an MP4 by ffmpeg.
# usage: ./rendus-video.sh <test> [style] [res] [samples] [extra key=value ...]
cd "$(dirname "$0")"
{ echo "# The construction video. Built by rendus-video.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; sed '$d' objets-rangements.py; sed '$d' objets-chaise.py; sed '$d' objets-mandy.py; sed '$d' objets-ecrans.py; cat objets-poste.py; sed '$d' objets-lampe.py; sed '$d' objets-contenus.py; sed '$d' objets-papiers.py; sed '$d' objets-poses.py; sed '$d' objets-sol.py; sed '$d' objets-autour.py; sed '$d' objets-cables.py; sed '$d' bureau-complet.py; cat video/trace.py video/construction.py video/boucle.py video/main.py; } > _video.py
B=/Applications/Blender.app/Contents/MacOS/Blender
T=${1:-macstudio}; ST=${2:-coupe}; RES=${3:-1280}; SPL=${4:-24}; shift 4 2>/dev/null
OUT="$PWD/_bruts/video/$T/${NOM:-$ST}"; mkdir -p "$OUT"; t0=$(date +%s)
$B -b --factory-startup -P _video.py -- test=$T style=$ST res=$RES samples=$SPL out="$OUT" "$@" > "$OUT/log.txt" 2>&1
echo "$T $ST : $(( $(date +%s) - t0 )) s"
grep -E "Traceback|Error:" "$OUT/log.txt" | grep -v "could not find any file path" | head -5
FPS=24; for a in "$@"; do [[ "$a" == pas=* ]] && FPS=$(( 24 / ${a#pas=} )); done
ls "$OUT"/[0-9]*.png >/dev/null 2>&1 && ffmpeg -y -loglevel error -framerate $FPS -pattern_type glob -i "$OUT/[0-9]*.png" -c:v libx264 -pix_fmt yuv420p -crf 16 -movflags +faststart "$OUT/../${NOM:-$ST}.mp4" && echo "mp4 $OUT/../${NOM:-$ST}.mp4"
return 0 2>/dev/null || exit 0
