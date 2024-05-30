import os
import asyncio

import openai
from telethon.extensions import html
from telethon import TelegramClient, events, types
from logger import logger, LogLevel as Level


class MessageHandler:
    def __init__(self, client, ai_client, target_channels):
        logger.log(Level.Debug, f"Creating Message Handler. Target channels: {target_channels}")
        self.client = client
        self.ai_client = ai_client
        self.target_channels = target_channels

    async def handle_new_message(self, event):
        logger.log(Level.Debug, "handle_new_message running")

        message = event.message
        logger.log(Level.Debug, f'Got message, text is: {message.message}')

        # Extracting entities and formatted text
        message_text = html.unparse(message.message, message.entities)

        # Extracting code blocks
        message_text, code_blocks = self.extract_code_blocks(message_text)

        # Translate and rewrite text
        translated_text = await self.translate_and_rewrite_text(message_text)

        # Insert code blocks back into the translated text
        translated_text = self.insert_code_blocks(translated_text, code_blocks)

        # Adding right-to-left alignment characters
        translated_text = f"\u202B{translated_text}\u202C"

        if message.forward:
            original_sender = message.forward.sender
            original_sender_name = original_sender.username if original_sender else "Unknown"
            translated_text = f"Forwarded from {original_sender_name}: {translated_text}"
            logger.log(Level.Debug, f"Translated text: {translated_text}")

        if message.media:
            try:
                file_path = await message.download_media()
                extension = "jpg" if isinstance(message.media, types.MessageMediaPhoto) else ""
                new_file_path = f"{file_path}.{extension}" if extension else file_path
                logger.log(Level.Debug, f"Got media file: {new_file_path}")
                os.rename(file_path, new_file_path)
                for target in self.target_channels:
                    sent = await self.client.send_file(target, new_file_path, caption=translated_text)
                    logger.log(Level.Info, f"Media {sent.id} is sent to {target}")
                os.remove(new_file_path)
            except Exception as e:
                logger.log(Level.Error, f"Error downloading or sending media: {e}")
        else:
            try:
                for target in self.target_channels:
                    sent = await self.client.send_message(target, translated_text, parse_mode='html')
                    logger.log(Level.Info, f"Message {sent.id} is sent to {target}")
            except Exception as e:
                logger.log(Level.Error, f"Error occured: {e}")
        logger.log(Level.Debug, "Exiting handle_new_message")

    def extract_code_blocks(self, text):
        import re
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        code_blocks = code_block_pattern.findall(text)
        for i, block in enumerate(code_blocks):
            text = text.replace(block, f"[CODE_BLOCK_{i}]")
        return text, code_blocks

    def insert_code_blocks(self, text, code_blocks):
        for i, block in enumerate(code_blocks):
            text = text.replace(f"[CODE_BLOCK_{i}]", block)
        return text

    async def translate_and_rewrite_text(self, text):
        logger.log(Level.Debug, "translate_and_rewrite_text running")
        retry_count = 0
        max_retries = 5
        backoff_factor = 2

        while retry_count < max_retries:
            messages = [
                {
                    "role": "system",
                    "content": "You are a translator and rewriter."
                },
                {
                    "role": "user",
                    "content": f"This GPT is a tech writer and Hebrew language professional, tasked with translating "
                               f"every message received into Hebrew and rewriting it to fit the best manner for a tech "
                               f"blog format on Telegram. The GPT translate and rewrite and will return only a final "
                               f"version of the text of the actual message:\n\n{text}"
                }
            ]

            try:
                response = self.ai_client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
                content = response.choices[0].message.content.strip()
                logger.log(Level.Debug, "Got translated message, proceeding")
                return content
            except openai.RateLimitError as e:
                retry_count += 1
                wait_time = backoff_factor ** retry_count
                logger.log(Level.Warning, f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except openai.OpenAIError as e:
                logger.log(Level.Error, f"An OpenAI error occurred: {e}")
                break
            except Exception as e:
                logger.log(Level.Error, f"An unexpected error occurred: {e}")
                break

        raise Exception("Max retries exceeded for OpenAI API request")
