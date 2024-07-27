import asyncio

from logger import LogLevel
from setup import CONFIGS, logger
from tg_client.telegram_bot import TelegramBot


async def main():
    """Main function to run the program."""
    config = CONFIGS.safe_read_configuration()
    bot = TelegramBot(config)

    return await bot.run_client()


if __name__ == '__main__':
    while True:
        try:
            result = asyncio.run(main())
            if result == 'restart': 
                logger.log(LogLevel.Info, 'Restarting the application...')
                continue
            break
        except Exception as e:
            logger.log(LogLevel.Error, f'Error: {e}')
            break
        finally:
            logger.log(LogLevel.Info, 'Event loop closed')
