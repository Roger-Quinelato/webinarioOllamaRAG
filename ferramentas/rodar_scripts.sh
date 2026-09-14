#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
python=".venv/Scripts/python.exe"
[ -x "$python" ] || python=".venv/bin/python"
falhas=0
for script in scripts/0*.py; do
  inicio=$(date +%s)
  "$python" -u "$script" > "docs/evidencias/E7/log_$(basename "$script" .py).txt" 2>&1
  codigo=$?
  echo "$(date +%H:%M:%S) $script → exit $codigo em $(( $(date +%s) - inicio ))s"
  [ "$codigo" -eq 0 ] || falhas=$((falhas + 1))
done
echo "scripts com falha: $falhas"
exit "$falhas"
