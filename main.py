import asyncio

from logger import logger, LogLevel
from setup import read_configuration
from bot_setup import initialize_clients, setup_channels, run_client


def main():
    """Main function to run the program."""
    config = read_configuration()
    aiclient = initialize_clients(config)
    channels = setup_channels(config)

    asyncio.run(run_client('sessions/session_name', config['api_id'], config['api_hash'], aiclient, channels))


if __name__ == '__main__':
    try:
        main()
    finally:
        logger.log(LogLevel.Info, 'Event loop closed')