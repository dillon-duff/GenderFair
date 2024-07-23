import os
import time
import logging
from multiprocessing import Lock
from functools import wraps

class MultiprocessSafeLogger:
    def __init__(self, log_file, level=logging.INFO):
        self.log_file = log_file
        self.level = level
        self.lock = Lock()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log(self, message, level=logging.INFO):
        with self.lock:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            log_entry = f"{timestamp} - {logging.getLevelName(level)} - {message}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)

    def info(self, message):
        self.log(message, logging.INFO)

    def warning(self, message):
        self.log(message, logging.WARNING)

    def error(self, message):
        self.log(message, logging.ERROR)

    def critical(self, message):
        self.log(message, logging.CRITICAL)

def with_logging(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

# Usage
logger = MultiprocessSafeLogger('logs/npo_rankings_pipeline.log')

@with_logging(logger)
def some_function():
    # Your function code here
    pass