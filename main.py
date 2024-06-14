import asyncio

from logger import LogLevel
from setup import CONFIGS, logger
from tg_client.telegram_bot import TelegramBot


def main():
    """Main function to run the program."""
    config = CONFIGS.read_configuration()
    bot = TelegramBot(config)

    return asyncio.run(bot.run_client())


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
