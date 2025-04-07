import logging
import sys
from pathlib import Path

def file_logger(name: str, filename: str = "run.log", level: int = logging.DEBUG) -> logging.Logger:
    """Set up and return a logger with both console and file output."""
    # Create logger
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent propagation to root logger
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set level
    logger.setLevel(level)
    
    # Create formatters
    formatter = logging.Formatter(
        '[%(name)s] %(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / filename, mode='a')  # Added mode='w' to overwrite
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def console_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Set up and return a logger with console output."""
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent propagation to root logger
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set level
    logger.setLevel(level)
    
    # Create formatters
    formatter = logging.Formatter(
        '[%(name)s] %(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger