import asyncio

from logger import LogLevel
from setup import CONFIGS, logger
from bot_setup import initialize_clients, setup_channels, run_client


def main():
    """Main function to run the program."""
    config = CONFIGS.read_configuration()
    aiclient = initialize_clients(config)
    channels = setup_channels(config)

    return asyncio.run(run_client(config, aiclient, channels))


if __name__ == '__main__':
    while True:
        try:
            result = main()
            if result == 'restart':  # Adjust this condition based on the actual return value that indicates a restart
                logger.log(LogLevel.Info, 'Restarting the application...')
                continue
            break
        except Exception as e:
            logger.log(LogLevel.Error, f'Error: {e}')
            break
        finally:
            logger.log(LogLevel.Info, 'Event loop closed')
