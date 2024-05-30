import sys
from telethon import TelegramClient, events, types
from openai import OpenAI
import openai
import os
# import logging
import asyncio
from telethon.extensions import html
from read_config import configs
from enums import ConfigProperty
from logger import logger, LogLevel as level


client = OpenAI(api_key=configs.read(ConfigProperty.ApiKey))

api_id = configs.read(ConfigProperty.ApiId)
api_hash = configs.read(ConfigProperty.ApiHash)

# Replace with your channel usernames or IDs
monitored_channels = configs.read(ConfigProperty.MonitoredChannels)
target_channel = configs.read(ConfigProperty.TargetChannel)

# Initialize OpenAI API
openai_api_key = configs.read(ConfigProperty.ApiKey)


async def handle_new_message(event, client):
    logger.log(level.Debug, "handle_new_message running")

    message = event.message
    logger.log(level.Debug, f'Got message, text is: {message.message}')

    def extract_code_blocks(text):
        import re
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        code_blocks = code_block_pattern.findall(text)
        for i, block in enumerate(code_blocks):
            text = text.replace(block, f"[CODE_BLOCK_{i}]")
        return text, code_blocks

    def insert_code_blocks(text, code_blocks):
        for i, block in enumerate(code_blocks):
            text = text.replace(f"[CODE_BLOCK_{i}]", block)
        return text

    # Extracting entities and formatted text
    message_text = html.unparse(message.message, message.entities)

    # Extracting code blocks
    message_text, code_blocks = extract_code_blocks(message_text)

    # Translate and rewrite text
    translated_text = await translate_and_rewrite_text(message_text)

    # Insert code blocks back into the translated text
    translated_text = insert_code_blocks(translated_text, code_blocks)

    # Adding right-to-left alignment characters
    translated_text = f"\u202B{translated_text}\u202C"

    if message.forward:
        original_sender = message.forward.sender
        original_sender_name = original_sender.username if original_sender else "Unknown"
        translated_text = f"Forwarded from {original_sender_name}: {translated_text}"
        logger.log(level.Debug, f"Translated text: {translated_text}")

    if message.media:
        try:
            file_path = await message.download_media()
            extension = "jpg" if isinstance(message.media, types.MessageMediaPhoto) else ""
            new_file_path = f"{file_path}.{extension}" if extension else file_path
            logger.log(level.Debug, f"Got media file: {new_file_path}")
            os.rename(file_path, new_file_path)
            await client.send_file(target_channel, new_file_path, caption=translated_text)
            os.remove(new_file_path)
        except Exception as e:
            logger.log(level.Error, f"Error downloading or sending media: {e}")
    else:
        await client.send_message(target_channel, translated_text, parse_mode='html')


async def translate_and_rewrite_text(text):
    logger.log(level.Debug, "translate_and_rewrite_text running")
    retry_count = 0
    max_retries = 5
    backoff_factor = 2

    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator and rewriter."},
                {"role": "user", "content": f"This GPT is a tech writer and Hebrew language professional, tasked with translating every message received into Hebrew and rewriting it to fit the best manner for a tech blog format on Telegram. The GPT translate and rewrite and will return only a final version of the text of the actual message:\n\n{text}"}
            ])
            return response.choices[0].message.content.strip()
        except openai.RateLimitError as e:
            retry_count += 1
            wait_time = backoff_factor ** retry_count
            logger.log(level.Warning, f"Rate limit exceeded. Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
        except openai.OpenAIError as e:
            logger.log(level.Error, f"An OpenAI error occurred: {e}")
            break
        except Exception as e:
            logger.log(level.Error, f"An unexpected error occurred: {e}")
            break

    raise Exception("Max retries exceeded for OpenAI API request")


async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        logger.log(level.Info, "Connected to Telegram Client")

        @client.on(events.NewMessage(chats=monitored_channels))
        async def handle_message(event):
            logger.log(level.Debug, "Got new message, processing")
            await handle_new_message(event, client)

        try:
            # Start the client
            await client.start()
            logger.log(level.Info, 'Client started successfully')

            # Run until disconnected
            await client.run_until_disconnected()
        except Exception as e:
            logger.log(level.Error, f'An error occurred: {e}')
        finally:
            if client.is_connected():
                await client.disconnect()
                logger.log(level.Info, 'Client disconnected successfully')
            else:
                logger.log(level.Info, 'Client was not connected')

if __name__ == '__main__':
    asyncio.run(main())
