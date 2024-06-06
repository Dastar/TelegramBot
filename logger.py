import logging
from enums import LogLevel, ConfigProperty
from read_config import configs


class Logger:
    def __init__(self, name, level, formatter):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        self.level = log_levels[level]

        # Create a formatter and set it for both handlers
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

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
        handler = logging.FileHandler(filename, encoding='utf-8')
        self._set_handler(handler)

    def set_console_handler(self):
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def log(self, level, msg):
        self.writers[level](msg)


logger = Logger(configs.read(ConfigProperty.LogName),
                configs.read(ConfigProperty.LogLevel),
                configs.read(ConfigProperty.LogFormat)
                )

logger.set_file_handler(ConfigProperty.LogFile)
logger.set_console_handler()
