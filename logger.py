import logging
from enums import LogLevel


class Logger:
    def __init__(self, name, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.level = level

        # Create a formatter and set it for both handlers
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.writers = {
            LogLevel.Debug: self.logger.debug,
            LogLevel.Info: self.logger.info,
            LogLevel.Warning: self.logger.warning,
            LogLevel.Error: self.logger.error,
            LogLevel.Critical: self.logger.critical
        }

    def get_logger(self):
        return self.logger

    def _set_handler(self, handler):
        handler.setLevel(self.level)
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def set_file_handler(self, filename):
        handler = logging.FileHandler(filename)
        self._set_handler(handler)

    def set_console_handler(self):
        handler = logging.StreamHandler()
        self._set_handler(handler)

    def log(self, level, msg):
        self.writers[level](msg)


logger = Logger('TBLog', logging.DEBUG)
logger.set_file_handler('logger.log')
logger.set_console_handler()
