import logging
from enum import Enum


class LogLevel(Enum):
    Debug = 0
    Info = 1
    Warning = 2
    Error = 4
    Critical = 5


class Logger:
    def __init__(self, name, log_file, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create a file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.writers = {
            LogLevel.Debug: self.logger.debug,
            LogLevel.Info: self.logger.info,
            LogLevel.Warning: self.logger.warning,
            LogLevel.Error: self.logger.error,
            LogLevel.Critical: self.logger.critical
        }

    def get_logger(self):
        return self.logger

    def log(self, level, msg):
        self.writers[level](msg)


logger = Logger('TBLog', 'logger.log', logging.DEBUG)
