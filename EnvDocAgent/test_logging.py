"""
Test logging functionality
"""

from logger import Logger, get_logger
from pathlib import Path


def test_logging():
    """Test logging system"""
    
    # Initialize logging
    print("Initializing logging...")
    logger = Logger.setup(log_dir="logs_test", log_level="DEBUG")
    
    print(f"Log file: {Logger.get_log_file()}")
    print("\nWriting test log entries...\n")
    
    # Test log levels
    logger.debug("This is a DEBUG log entry")
    logger.info("This is an INFO log entry")
    logger.warning("This is a WARNING log entry")
    logger.error("This is an ERROR log entry")
    logger.critical("This is a CRITICAL log entry")
    
    # Submodule logger
    sub_logger = get_logger("test_module")
    sub_logger.info("Log message from test_module")
    
    # Exception logging
    try:
        raise ValueError("This is a test exception")
    except Exception as e:
        logger.exception(f"Caught exception: {e}")
    
    print(f"\nLogging done. See log file: {Logger.get_log_file()}\n")
    
    # Verify log file exists
    log_file = Logger.get_log_file()
    if log_file and log_file.exists():
        print("✓ Log file created")
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"✓ Log file size: {len(content)} bytes")
            print(f"✓ Log line count: {len(content.splitlines())} lines")
            
            print("\nLog file preview:")
            print("=" * 80)
            print(content)
            print("=" * 80)
    else:
        print("✗ Log file creation failed")


if __name__ == "__main__":
    test_logging()
