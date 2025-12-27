@echo off
echo ========================================
echo   Windows NVMe Optimizer - BUILD EXE
echo ========================================
echo.

REM Check PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Instalando PyInstaller...
    pip install pyinstaller
)

REM Install all dependencies first
echo [INFO] Instalando dependencias...
pip install -r requirements.txt
pip install pystray pillow

echo.
echo [INFO] Compilando executavel...
echo.

REM Build with PyInstaller
REM --onefile: Single .exe file
REM --windowed: No console (use --console if you want terminal)
REM --icon: Custom icon (optional)
REM --add-data: Include config.yaml
REM --hidden-import: Modules that PyInstaller might miss

pyinstaller ^
    --onefile ^
    --console ^
    --name "WindowsOptimizer_V3" ^
    --add-data "config.yaml;." ^
    --add-data "modules;modules" ^
    --hidden-import pynvml ^
    --hidden-import wmi ^
    --hidden-import pystray ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageDraw ^
    --hidden-import psutil ^
    --hidden-import yaml ^
    --hidden-import colorama ^
    --hidden-import rich ^
    --hidden-import rich.console ^
    --hidden-import rich.layout ^
    --hidden-import rich.panel ^
    --hidden-import rich.table ^
    --hidden-import rich.live ^
    --uac-admin ^
    win_optimizer.py

echo.
if exist "dist\WindowsOptimizer_V3.exe" (
    echo ========================================
    echo [SUCCESS] Executavel criado com sucesso!
    echo ========================================
    echo.
    echo Arquivo: dist\WindowsOptimizer_V3.exe
    echo.
    echo Copie para a area de trabalho e execute como Administrador!
    
    REM Copy to desktop
    copy "dist\WindowsOptimizer_V3.exe" "%USERPROFILE%\Desktop\" >nul 2>&1
    if not errorlevel 1 (
        echo.
        echo [OK] Copiado para a Area de Trabalho automaticamente!
    )
) else (
    echo [ERROR] Falha na compilacao. Verifique os erros acima.
)

echo.
pause
