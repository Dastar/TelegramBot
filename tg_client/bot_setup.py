# from telethon import TelegramClient, events
# import asyncio
# from openai import OpenAI
#
# from configuration_readers.data_reader import DataReader
# from configuration_readers.role_reader import RoleReader
# from ai_client.ai_client import AIClient
# from tg_client.channel_registry import ChannelRegistry
# from configuration_readers.channel_reader import ChannelReader
# from logger import LogLevel
# from setup import logger
# from events.event_handler import EventHandler
# from setup import setup_signal_handling
#
#
# def initialize_clients(config):
#     """Initialize OpenAI and AI clients."""
#     logger.log(LogLevel.Debug, "Initializing OpenAI client")
#     openai_client = OpenAI(api_key=config['api_key'])
#     aiclient = AIClient(openai_client)
#     return aiclient
#
#
# def setup_channels(config):
#     """Set up channel registry and readers."""
#     logger.log(LogLevel.Debug, "Setting up channels")
#     reader = DataReader(config['bot_config'])
#     role_reader = RoleReader(reader)
#     channel_reader = ChannelReader(role_reader, reader)
#     channels = ChannelRegistry()
#     for channel, sources in channel_reader.get_channels():
#         channels.add_channels(channel, sources)
#     return channels
#
#
# async def run_client(config, aiclient, channels):
#     """Run the Telegram client and handle messages."""
#     logger.log(LogLevel.Info, "Connecting to Telegram Client")
#     stop_event = asyncio.Event()
#     restart_event = asyncio.Event()
#
#     async with TelegramClient(config['session_name'], config['api_id'], config['api_hash']) as client:
#         message_handler = EventHandler(client, aiclient, channels, config)
#
#         @client.on(events.NewMessage(chats=channels.get_monitored()))
#         async def handle_message(event):
#             await message_handler.handle_new_message(event)
#
#         @client.on(events.CallbackQuery)
#         async def handler(event):
#             answer = await message_handler.hadle_buttons(event)
#             if answer == 'restart':
#                 restart_event.set()
#                 stop_event.set()
#
#         @client.on(events.MessageEdited)
#         async def handle_edited_messages(event):
#             logger.log(LogLevel.Debug, f'Editing message with id {event.message.id} from {event.chat.username}')
#             await message_handler.handle_edited_messages(event)
#
#         loop = asyncio.get_running_loop()
#         setup_signal_handling(loop, stop_event)
#
#         try:
#             await client.start()
#             logger.log(LogLevel.Info, 'Client started successfully')
#             await stop_event.wait()
#             logger.log(LogLevel.Info, 'Stop event received, shutting down...')
#         except Exception as e:
#             logger.log(LogLevel.Error, f'An error occurred: {e}')
#             return 'fail'
#         finally:
#             if client.is_connected():
#                 await client.disconnect()
#                 logger.log(LogLevel.Info, 'Client disconnected successfully')
#             else:
#                 logger.log(LogLevel.Info, 'Client is not connected')
#     return 'restart' if restart_event.is_set() else 'success'
