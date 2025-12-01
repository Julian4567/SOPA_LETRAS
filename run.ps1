<# run.ps1
   Crea/activa un virtualenv, instala dependencias y arranca el servidor.
   Uso: .\run.ps1  (ejecutar en PowerShell)
         .\run.ps1 -RecreateVenv  (forzar recrear el venv)
#>
param(
  [switch]$RecreateVenv
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

if ($RecreateVenv -or -not (Test-Path .\venv)) {
  Write-Output "Creando entorno virtual .\venv..."
  python -m venv venv
}

Write-Output "Activando entorno virtual..."
.\venv\Scripts\Activate.ps1

Write-Output "Actualizando pip e instalando dependencias..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Output "Iniciando servidor..."
python servidor.py
