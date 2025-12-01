#!/usr/bin/env bash
# run.sh - crea un virtualenv, instala deps y arranca el servidor
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d venv ]; then
  python3 -m venv venv
fi

. venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python servidor.py
