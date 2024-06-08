import asyncio

from logger import LogLevel
from setup import CONFIGS, logger
from bot_setup import initialize_clients, setup_channels, run_client


def main():
    """Main function to run the program."""
    config = CONFIGS.read_configuration()
    aiclient = initialize_clients(config)
    channels = setup_channels(config)

    asyncio.run(run_client(config, aiclient, channels))


if __name__ == '__main__':
    try:
        main()
    finally:
        logger.log(LogLevel.Info, 'Event loop closed')
