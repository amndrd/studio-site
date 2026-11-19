#!/bin/zsh
# Renders of the fictional projects printed on the desk papers (Ombelle speakers, Halde study model).
# Output: hero/outils/papiers-contenus/img/. usage: ./rendus-fictifs.sh [samples]
cd "$(dirname "$0")"
{ echo "# Fictional projects renders. Built by rendus-fictifs.sh."; cat labo2-base.py; sed '$d' objets-bureau.py; cat rendus-fictifs.py; } > _fictifs.py
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P _fictifs.py -- samples=${1:-128} out="$PWD/../papiers-contenus/img" > _bruts/log-fictifs.txt 2>&1
grep -E "RENDER|Error|Traceback" _bruts/log-fictifs.txt | grep -v "Not freed" | head
