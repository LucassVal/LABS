@echo off
REM Windows NVMe RAM Optimizer - Launcher
REM Este script executa o otimizador como administrador

cd /d "%~dp0"
powershell -Command "Start-Process python -ArgumentList 'win_optimizer.py' -Verb RunAs"
