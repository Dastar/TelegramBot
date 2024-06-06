import os
import signal
import ctypes

from read_config import configs
from enums import ConfigProperty
from logger import logger, LogLevel


def read_configuration():
    """Read and set up configuration values."""
    os.environ['OPENAI_API_KEY'] = configs.read(ConfigProperty.ApiKey)
    api_id = configs.read(ConfigProperty.ApiId)
    api_hash = configs.read(ConfigProperty.ApiHash)
    return {
        'api_key': configs.read(ConfigProperty.ApiKey),
        'api_id': api_id,
        'api_hash': api_hash,
        'role_file': configs.read(ConfigProperty.RoleFile),
        'channels_file': configs.read(ConfigProperty.ChannelsFile)
    }


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