# Script PowerShell para instalação do auto-start (versão Python)
# Execute como Administrador

$scriptPath = Join-Path $PSScriptRoot "win_optimizer.py"
$pythonExe = "python"  # ou "python3" ou caminho completo

# Testa se Python está instalado
try {
    $pythonVersion = & $pythonExe --version
    Write-Host "✓ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale Python e tente novamente" -ForegroundColor Yellow
    pause
    exit 1
}

# Instala dependências
Write-Host "`nInstalando dependências..." -ForegroundColor Cyan
& $pythonExe -m pip install -r requirements.txt

# Cria Task Scheduler task
Write-Host "`nConfigurando auto-start..." -ForegroundColor Cyan

$taskName = "WinOptimizerPython"
$taskDescription = "Windows NVMe RAM Optimizer (Python)"

# Remove task existente
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Cria nova task
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`"" -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -Description $taskDescription `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Force

Write-Host "`n✓ Auto-start instalado com sucesso!" -ForegroundColor Green
Write-Host "`nO otimizador será iniciado automaticamente ao ligar o PC" -ForegroundColor Yellow
Write-Host "`nPara testar agora, execute:" -ForegroundColor Cyan
Write-Host "    python win_optimizer.py" -ForegroundColor White

pause
