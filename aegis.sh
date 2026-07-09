#!/usr/bin/env bash
# Equivalent bash de aegis.ps1 : premiere execution, installe tout seul
# (venv + dependances) ; ensuite relaie simplement vers le vrai `aegis`.
#
# Usage : ./aegis.sh scan demo-legacy-app
#         ./aegis.sh rules list
#         ./aegis.sh doctor
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
venv_dir="$repo_root/.venv"

# Sous Windows (git-bash), les venv Python mettent leurs exe dans Scripts/
# et pas dans bin/.
if [ -f "$venv_dir/Scripts/python.exe" ]; then
    venv_python="$venv_dir/Scripts/python.exe"
    venv_aegis="$venv_dir/Scripts/aegis.exe"
else
    venv_python="$venv_dir/bin/python"
    venv_aegis="$venv_dir/bin/aegis"
fi

if [ ! -x "$venv_python" ] && [ ! -f "$venv_python" ]; then
    echo "Premiere utilisation : creation de l'environnement (ca prend une minute)..."
    python -m venv "$venv_dir"
    "$venv_python" -m pip install --quiet --upgrade pip
    "$venv_python" -m pip install --quiet -e "$repo_root/backend[dev,api]" -e "$repo_root/cli[dev]"
    echo "Environnement pret."
fi

exec "$venv_aegis" "$@"
