@echo off
REM start.bat - crea/activa venv, instala deps y arranca servidor (cmd.exe)
IF NOT EXIST venv (
  python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python servidor.py
