"""
Logging configuration and utilities for the batch replacement tool.
Provides colored console output and file logging.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class LogColors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    SUCCESS = '\033[92m'


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to log messages based on level.
    """
    
    # Color mappings for different log levels
    COLORS = {
        logging.DEBUG: LogColors.BLUE,
        logging.INFO: LogColors.GREEN,
        logging.WARNING: LogColors.WARNING,
        logging.ERROR: LogColors.ERROR,
        logging.CRITICAL: LogColors.ERROR + LogColors.BOLD
    }
    
    def format(self, record):
        # Save original levelname
        original_levelname = record.levelname
        
        # Add color to levelname
        if record.levelno in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelno]}{record.levelname}{LogColors.END}"
        
        # Format the message
        result = super().format(record)
        
        # Restore original levelname
        record.levelname = original_levelname
        
        return result


def setup_logging(
    verbose: bool = False,
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        verbose: Enable verbose (DEBUG) logging
        log_file: Path to log file (if None, no file logging)
        console_output: Enable console output
        
    Returns:
        Configured logger instance
    """
    # Set log level
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    console_format = '%(asctime)s - %(levelname)s - %(message)s'
    file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler with colors
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Use colored formatter for console
        console_formatter = ColoredFormatter(console_format, date_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler (always add if log_file is specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
            
            file_formatter = logging.Formatter(file_format, date_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr)
    
    # Return a named logger for the application
    return logging.getLogger('batch_replace')