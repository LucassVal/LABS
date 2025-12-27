"""
Centralized Logging for Windows NVMe Optimizer
All modules should use this instead of print()
"""
import logging
import sys
from datetime import datetime

# Create main logger
logger = logging.getLogger("optimizer")
logger.setLevel(logging.DEBUG)

# Console Handler (colored output)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

class ColorFormatter(logging.Formatter):
    """Custom formatter with colors"""
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[91m',  # Bright Red
        'RESET': '\033[0m'
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Format: [HH:MM:SS] [LEVEL] Message
        formatted = f"{color}[{timestamp}] [{record.levelname}]{reset} {record.getMessage()}"
        return formatted

console_handler.setFormatter(ColorFormatter())
logger.addHandler(console_handler)

# File Handler (for debugging)
try:
    file_handler = logging.FileHandler("optimizer.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
except:
    pass  # Log file creation may fail, that's ok

# Convenience functions
def info(msg): logger.info(msg)
def debug(msg): logger.debug(msg)
def warning(msg): logger.warning(msg)
def error(msg): logger.error(msg)
def success(msg): logger.info(f"✓ {msg}")
