import asyncio
from os import path

from wabridge.wabridge import WABridge
from logger import LogLevel
from setup import CONFIGS, logger


async def main():
    logger.log(LogLevel.Debug, "Initializing WhatsApp Bridge")
    server_url = "http://localhost:3000"
    client = WABridge(server_url)
    shutdown_event = asyncio.Event()
    config = CONFIGS.safe_read_configuration()
    logger.log(LogLevel.Debug, "Starting the Client")
    try:
        await client.start(config['clientId'], config['exe'])
        await client.check_state()
    except Exception as e:
        print(e)
        client.terminate()
        exit(1)

    # List groups
    logger.log(LogLevel.Debug, "Caching groups")
    await client.cache_groups()

    logger.log(LogLevel.Debug, "Test #1: Sending Message")
    group_id = "TG2WA"
    message = '''Test message from Python'''
    result = await client.send_message(group_id, message)
    logger.log(LogLevel.Debug, f"Results: {result}")

    logger.log(LogLevel.Debug, "Test #2: Sending Media")
    media = [path.join('downloads', "document_2024-12-31_14-23-11.mp4")]
    result = await client.send_media(group_id, media, message)
    logger.log(LogLevel.Debug, f"Results: {result}")

    # Wait until shutdown signal is received
    try:
        logger.log(LogLevel.Debug, f"Waiting for events to end. "
                                   f"After receiving all messages you can terminate this process.")
        await shutdown_event.wait()
    except asyncio.CancelledError:
        logger.log(LogLevel.Debug, f"[Server] Received shutdown signal.")
    finally:
        logger.log(LogLevel.Debug, f"[Server] Shutting down server...")
        client.terminate()
        logger.log(LogLevel.Debug, f"For the final test check if port 3000 is free.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Server] KeyboardInterrupt detected.")
