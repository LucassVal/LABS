@echo off
REM Windows NVMe RAM Optimizer V3.0 - Launcher
REM Este script executa o otimizador como administrador

cd /d "%~dp0"

REM Verifica e instala dependencias novas (apenas na primeira vez)
if not exist ".deps_installed" (
    echo [INFO] Instalando dependencias V3.0...
    pip install pystray pillow -q
    echo. > .deps_installed
)

powershell -Command "Start-Process python -ArgumentList 'win_optimizer.py' -Verb RunAs"
