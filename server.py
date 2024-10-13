import asyncio
from aiohttp import web
import uvloop

from setup import CONFIGS
from tg_client.telegram_bot import TelegramBot

# Assuming the TelegramBot class is already defined elsewhere and imported here
# from telegram_bot import TelegramBot

app = web.Application()

bot = None

async def start_bot(request):
    global bot
    if bot and bot.is_running:
        return web.json_response({"status": "Bot is already running"})

    config = CONFIGS.read_configuration()
    bot = TelegramBot(config)

    await asyncio.create_task(bot.run_client())
    return web.json_response({"status": "Bot started"})

async def get_status(request):
    global bot
    status = {
        "is_running": bot.is_running if bot else False,
        # "number_of_targets": bot.number_of_targets() if bot else 0,
        # "number_of_sources": bot.number_of_sources() if bot else 0
    }
    return web.json_response(status)

app.add_routes([web.get('/start_bot', start_bot)])
app.add_routes([web.get('/status', get_status)])

if __name__ == '__main__':
    uvloop.install()
    web.run_app(app, port=5000)
