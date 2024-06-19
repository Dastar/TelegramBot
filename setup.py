import os
import signal
import ctypes

from enums import ConfigProperty
from configuration_readers.configuration_reader import Configurations
from logger import Logger, LogLevel

CONFIGS = Configurations('configurations/config.ini').open()
logger = Logger(CONFIGS.read(ConfigProperty.LogName),
                CONFIGS.read(ConfigProperty.LogLevel)
                )

logger.set_file_handler(CONFIGS.read(ConfigProperty.LogFile))
logger.set_console_handler()


def setup_signal_handling(loop, stop_event):
    """Set up signal handling for graceful termination."""
    def signal_handler(sig=None, frame=None):
        logger.log(LogLevel.Info, 'Received termination signal, exiting...')
        stop_event.set()

    if os.name == 'nt':
        def win_signal_handler(dwCtrlType):
            signal_handler()
            return True

        kernel = ctypes.WinDLL('kernel32')
        kernel.SetConsoleCtrlHandler(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(win_signal_handler), True)
    else:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
