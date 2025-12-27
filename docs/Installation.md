# Installation Guide

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (1809+) or Windows 11
- **RAM**: 8GB (16GB recommended for best results)
- **Storage**: NVMe SSD
- **Python**: 3.8 or higher
- **Privileges**: Administrator rights

### Recommended System
- **CPU**: Modern Intel/AMD (6th gen+ Intel or Ryzen 2000+)
- **RAM**: 16GB DDR4
- **Storage**: NVMe Gen3 or Gen4 SSD
- **GPU**: Any (NVIDIA GPUs get full monitoring)

---

## Step-by-Step Installation

### 1. Install Python

Download Python 3.8+ from [python.org](https://www.python.org/downloads/)

**Important**: Check "Add Python to PATH" during installation!

Verify installation:
```bash
python --version
# Should show: Python 3.8.x or higher
```

### 2. Clone or Download Repository

**Option A: Git Clone**
```bash
git clone https://github.com/LucassVal/LABS.git
cd LABS/WindowsNVMeOptimizer
```

**Option B: Download ZIP**
1. Download ZIP from GitHub
2. Extract to `C:\WindowsNVMeOptimizer\`
3. Open folder in terminal

### 3. Install Dependencies

Open **PowerShell as Administrator** in the `PythonVersion` folder:

```bash
cd PythonVersion
pip install -r requirements.txt
```

Dependencies installed:
- `psutil` - System monitoring
- `pyyaml` - Configuration files
- `colorama` - Colored console output
- `wmi` - Windows Management
- `pynvml` - NVIDIA GPU monitoring
- `rich` - Beautiful dashboard
- `pywin32` - Windows APIs

### 4. Configure Settings (Optional)

Edit `config.yaml` before first run:

```yaml
# Adjust these based on your needs:
standby_cleaner:
  threshold_mb: 4096  # 2GB = less aggressive, 4GB = more aggressive

cpu_control:
  max_frequency_percent: 85  # 85 = balanced, 90 = more performance
```

### 5. First Run

**Right-click** `RUN_OPTIMIZER.bat` → **Run as Administrator**

Choose dashboard mode:
- `[1]` Console Dashboard (recommended)
- `[2]` Floating Widget

You should see:
```
✓ Running as Administrator
[INFO] Loading configuration...
[INFO] StandbyMemoryCleaner started (threshold: 4096MB)
[CPU] Max frequency set to 85%
[SMART] Process manager started
[FAN] ✓ NBFC configured for 100%
✓ All services started
```

---

## Enable Auto-Start (Optional but Recommended)

Run as Administrator:
```powershell
.\install_service.ps1
```

This creates a Windows Task Scheduler task that:
- ✅ Starts automatically on login
- ✅ Runs with elevated privileges
- ✅ Restarts on failure
- ✅ No UAC prompt every boot

To verify:
1. Open Task Scheduler
2. Look for "WindowsNVMeOptimizer"
3. Task should be "Ready" or "Running"

---

## Verify Installation

### Test 1: Check Dashboard
Dashboard should show:
- ✅ CPU usage, temperature, frequency
- ✅ GPU detection (if NVIDIA)
- ✅ RAM usage and free space
- ✅ All optimizations showing as "Active"

### Test 2: RAM Cleaning
1. Open many Chrome tabs
2. Watch RAM usage go up
3. When it crosses threshold → Auto-cleanup!
4. "Cleanups" counter should increase

### Test 3: CPU Limit
1. Open Task Manager → Performance → CPU
2. Max speed should be around 85% of advertised max
3. Example: 3.74 GHz instead of 4.4 GHz

---

## Optional: Fan Control Setup

If NBFC auto-detection fails:

### Option 1: Install NBFC
1. Download: [NBFC on GitHub](https://github.com/hirschmann/nbfc)
2. Install and configure for your laptop model
3. Restart optimizer

### Option 2: Manual BIOS
1. Restart PC → Enter BIOS (F2/Del)
2. Find "Fan Control" or "Thermal"
3. Set to "Performance" or "Full Speed"

### Option 3: Manufacturer Software
- **ASUS**: Armoury Crate
- **MSI**: Dragon Center
- **Lenovo**: Vantage

---

## Troubleshooting Installation

### "Python not found"
**Solution**: Reinstall Python with "Add to PATH" checked

### "Permission denied" errors
**Solution**: Run PowerShell/CMD as Administrator

### "Module not found" errors
**Solution**: 
```bash
pip install --upgrade -r requirements.txt
```

### "NBFC not detected"
**Solution**: Install NBFC or use BIOS/manufacturer software

### "GPU not detected"
**Solutions**:
- Update NVIDIA drivers
- For AMD GPUs: Limited support (no pynvml)
- Intel iGPU: Shows status only

---

## Uninstallation

### Remove Auto-Start
```powershell
# Run as Admin
schtasks /delete /tn "WindowsNVMeOptimizer" /f
```

### Remove Program
1. Close optimizer (Ctrl+C)
2. Delete folder: `C:\WindowsNVMeOptimizer\`
3. (Optional) Uninstall Python if not used elsewhere

### Reset CPU Frequency
CPU frequency will automatically reset to 100% when optimizer stops.

Or manually:
```powershell
powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100
powercfg /setdcvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100
powercfg /setactive SCHEME_CURRENT
```

---

## Next Steps

- [Configuration Guide](Configuration.md) - Customize settings
- [CPU Analysis](CPU-Analysis.md) - Why 85% is better than 100%
- [RAM Cleaning](RAM-Cleaning.md) - How it works
- [Fan Control](Fan-Control.md) - Detailed fan setup

---

**Installation complete! Enjoy your optimized system!** 🚀
