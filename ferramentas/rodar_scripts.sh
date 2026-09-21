#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
python=".venv/Scripts/python.exe"
[ -x "$python" ] || python=".venv/bin/python"
falhas=0
logs="logs/rodar_scripts"
mkdir -p "$logs"
scripts=(
  scripts/02_indexar_hibrido.py
  scripts/calibrar_retrieval_hibrido.py
)
for script in "${scripts[@]}"; do
  inicio=$(date +%s)
  log="$logs/$(basename "$script" .py).txt"
  "$python" -u "$script" > "$log" 2>&1
  codigo=$?
  echo "$(date +%H:%M:%S) $script → exit $codigo em $(( $(date +%s) - inicio ))s; log: $log"
  [ "$codigo" -eq 0 ] || falhas=$((falhas + 1))
done
echo "scripts com falha: $falhas"
exit "$falhas"
