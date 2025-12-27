# Script PowerShell para criar atalho na Área de Trabalho
$SourcePath = "C:\Users\Lucas Valério\.gemini\antigravity\scratch\WindowsNVMeOptimizer\PythonVersion\RUN_OPTIMIZER.bat"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Windows Optimizer.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $SourcePath
$Shortcut.WorkingDirectory = Split-Path $SourcePath
$Shortcut.Description = "Windows NVMe RAM Optimizer"
$Shortcut.IconLocation = "powershell.exe,0"
$Shortcut.Save()

Write-Host "✓ Atalho criado na Área de Trabalho!" -ForegroundColor Green
