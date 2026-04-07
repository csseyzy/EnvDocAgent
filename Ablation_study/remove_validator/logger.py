"""
Logging Configuration Module
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class Logger:
    """Logger Manager"""
    
    _instance: Optional[logging.Logger] = None
    _log_file: Optional[Path] = None
    
    @classmethod
    def setup(cls, log_dir: str = "logs", log_level: str = "INFO") -> logging.Logger:
        """
        Setup logging system
        
        Args:
            log_dir: Log file directory
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
        Returns:
            Configured logger instance
        """
        if cls._instance is not None:
            return cls._instance
        
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Generate log filename (with timestamp)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cls._log_file = log_path / f"readme_agent_{timestamp}.log"
        
        # Create logger
        logger = logging.getLogger("readme_agent")
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Avoid adding duplicate handlers
        if logger.handlers:
            logger.handlers.clear()
        
        # Define log format
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler - record all logs
        file_handler = logging.FileHandler(cls._log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Console handler - show INFO and above levels only
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        cls._instance = logger
        logger.info(f"Logging system initialized, log file: {cls._log_file}")
        
        return logger
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Get logger instance
        
        Returns:
            Logger instance, auto-initializes if not initialized
        """
        if cls._instance is None:
            return cls.setup()
        return cls._instance
    
    @classmethod
    def get_log_file(cls) -> Optional[Path]:
        """Get current log file path"""
        return cls._log_file


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get logger instance
    
    Args:
        name: Submodule name (optional)
    
    Returns:
        Logger instance
    """
    base_logger = Logger.get_logger()
    if name:
        return base_logger.getChild(name)
    return base_logger






