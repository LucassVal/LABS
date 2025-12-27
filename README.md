# 🚀 Windows NVMe RAM Optimizer V3.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)](https://www.microsoft.com/windows)

**Real-time Windows system optimizer with automated RAM cleaning, CPU throttling control, intelligent process prioritization, game mode detection, and live visual dashboard.**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [V3.0 New Features](#-v30-new-features)
- [Performance Gains](#-real-world-results)
- [Quick Start](#-quick-start)
- [Configuration](#️-configuration)
- [Project Structure](#-project-structure)
- [License](#-license)

---

## 🎯 Overview

Windows NVMe RAM Optimizer is a comprehensive system optimization tool designed for NVMe SSD-equipped systems. It automatically manages RAM, controls CPU frequency for sustained performance, prioritizes user applications, detects games for auto-boost, and provides real-time monitoring through a beautiful visual dashboard.

### Why This Tool?

- **Windows wastes RAM** on unnecessary standby cache
- **Thermal throttling** reduces sustained CPU performance by up to 50%
- **Background processes** steal resources from your important apps
- **No visibility** into what's happening with your system
- **Games need manual optimization** every time you play

This optimizer **solves all of these** automatically!

---

## ✨ Key Features

### ⚡ Smart I/O Priority Control (Kernel-Level)
- Uses **undocumented Windows Kernel APIs** (`NtSetInformationProcess`)
- **Active Apps (Games)**: Forces **High I/O Priority**. Your game skips the SSD queue!
- **Background Apps**: Forces **Very Low I/O Priority**. Chrome/Steam updates won't stutter your game.
- **Result**: Eliminates micro-stuttering caused by background disk usage.

### 💾 NVMe/SSD Enhancements
- **No Sleep**: Prevents SSD from entering deep sleep states (APST) to avoid "wake-up lag".
- **Disable LastAccess**: Stops Windows from writing to disk every time it reads a file (IOPS Saver).
- **Smart TRIM**: Runs a re-trim operation on startup to ensure peak write speeds.

### 🔥 Adaptive CPU Thermal Governor
- Replaces static limits with a dynamic algorithm monitoring temperature in real-time.
- **< 70°C**: Unlocks **100% CPU** (Turbo Boost) for max responsiveness.
- **70°C - 80°C**: Adjusts to **90%** to maintain performance.
- **> 90°C**: Throttles to **85%** to prevent overheating.
- **Benefit**: "Snappy" system for short bursts, safe for long gaming sessions.

### 🧹 Surgical RAM Cleaning (V2)
- New logic: **Only cleans when necessary.**
- Checks if **Standby Cache > 1GB**. If cache is empty, it does NOTHING.
- **Prevention**: Prevents "over-cleaning" which could cause stuttering.
- **Zero-Stutter**: Removed aggressive `EmptyWorkingSets` call.

### 🎮 Intelligent Process Scheduler
- **Auto-Detection:** Automatically identifies which app you are actively using.
- **Prioritization:** Assigns **High CPU Priority** to your active window.
- **Deprioritization:** Assigns **Low CPU Priority** to web browsers, Discord, Spotify automatically.

---

## 🆕 V3.0 New Features

### 🎮 Game Mode Detector
Automatically detects when you launch a game and applies optimizations!
- **40+ Games Supported**: Valorant, CS2, Fortnite, Apex, LoL, Dota 2, GTA V, and more
- **Auto-Boost**: Triggers CPU boost and RAM cleanup when game starts
- **Auto-Restore**: Returns to normal mode when game closes
- **Dashboard Integration**: Shows current game in the UI

### 📡 Network QoS (Ping Booster)
Optimizes network settings for lower gaming latency:
- **Nagle Algorithm Disabled**: Reduces micro-lag in online games
- **TCP Buffer Optimization**: Better packet handling
- **No Configuration Needed**: Applied automatically at startup

### ⚡ Profile System
Switch between optimization modes based on your activity:
| Profile | CPU Max | RAM Threshold | Best For |
|---------|---------|---------------|----------|
| 🎮 Gaming | 100% | 2GB (aggressive) | Maximum FPS |
| 💼 Productivity | 95% | 4GB | Work apps |
| 🔋 Battery Saver | 70% | 8GB | Laptop on battery |
| ⚖️ Balanced | 85% | 4GB | Default |

### 📊 History Logger (CSV)
Tracks all optimization events for analysis:
- **Location**: `~/.nvme_optimizer/logs/cleanup_history.csv`
- **Data**: Timestamp, freed MB, trigger, RAM before/after
- **Events Log**: Tracks game starts, profile changes, etc.

### 🖥️ System Tray Icon
Run the optimizer in the background:
- **Right-Click Menu**: Switch profiles, force RAM cleanup
- **Status Indicator**: Green = active
- **Requires**: `pip install pystray pillow`

---

## 📈 Real-World Results

Tested on **Intel Core i5-11300H + RTX 3050 Laptop**:

| Metric | Stock Windows | With Optimizer | Improvement |
|--------|---------------|----------------|-------------|
| **Avg Gaming Temp** | 92-95°C | 78-82°C | **-12°C** ❄️ |
| **Clock Stability** | Throttling | Stable (3.8GHz+) | **Smoothness** 🚀 |
| **Micro-Stuttering** | Frequent | Eliminated | **Consistent FPS** ✅ |
| **Free RAM** | < 500MB | 4GB+ | **Responsiveness** 💾 |
| **Input Lag** | Variable | Minimized | **Low Latency** ⚡ |

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/LucassVal/LABS.git
cd LABS/WindowsNVMeOptimizer/PythonVersion
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Optimizer
```bash
# Right-click → Run as Administrator
RUN_OPTIMIZER.bat
```

The Console Dashboard will start automatically with V3.0 features active.

---

## ⚙️ Configuration

Edit `config.yaml` to customize settings:

```yaml
# RAM Cleaning
standby_cleaner:
  enabled: true
  threshold_mb: 4096          # Clean when free RAM < 4GB

# CPU Control (85% = optimal for laptops)
cpu_control:
  max_frequency_percent: 85
  min_frequency_percent: 5

# V3.0: Network QoS
network_qos:
  enabled: true

# V3.0: Game Detection
game_detector:
  enabled: true

# V3.0: Add custom games
game_detector:
  extra_game_exes:
    - "mygame.exe"
```

---

## 📂 Project Structure

```
PythonVersion/
├── win_optimizer.py          # Main script (V3.0)
├── config.yaml               # Configuration
├── requirements.txt          # Dependencies
├── RUN_OPTIMIZER.bat         # Launcher
├── BUILD_EXE.bat             # Create standalone .exe
├── modules/
│   ├── standby_cleaner.py    # RAM cleaner
│   ├── cpu_power.py          # CPU control + Thermal Governor
│   ├── smart_process_manager.py # Auto I/O priority
│   ├── nvme_manager.py       # SSD optimizations
│   ├── dashboard.py          # Visual dashboard
│   ├── network_qos.py        # 🆕 Network optimization
│   ├── game_detector.py      # 🆕 Game detection
│   ├── profiles.py           # 🆕 Profile system
│   ├── history_logger.py     # 🆕 CSV logging
│   ├── tray_icon.py          # 🆕 System tray
│   ├── temperature_service.py # Centralized temp monitoring
│   └── logger.py             # Logging infrastructure
```

---

## 🔄 Auto-Start on Boot

Run as Administrator:
```powershell
.\install_service.ps1
```

Creates a Task Scheduler task that runs automatically on login.

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Inspired by [ISLC](https://www.wagnardsoft.com/forums/viewtopic.php?t=1256)
- Dashboard built with [Rich](https://github.com/Textualize/rich)
- GPU monitoring via [pynvml](https://github.com/gpuopenanalytics/pynvml)

---

**Made with ❤️ for the PC optimization community**

*Tested and validated on production systems*
