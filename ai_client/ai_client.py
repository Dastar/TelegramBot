import asyncio
import time
import aiohttp
import openai

from logger import LogLevel
from message.channel import ChannelMessage
from setup import logger


def format_content(content: str, tag, text):
    return content.replace(tag, text)


class AIClient:
    def __init__(self, client: openai.OpenAI):
        self.client = client

    async def run(self, message: ChannelMessage):
        logger.log(LogLevel.Debug, 'Running AI model')
        content = await self.run_model(message.get_text(), message.channel)
        message.output_text = content
        if message.generate_image:
            await self.generate_image(message)

    async def run_model(self, text: str, channel):
        logger.log(LogLevel.Debug, f"running text model {channel.model}")

        retry_count = 0
        max_retries = 5
        backoff_factor = 2

        message = channel.get_message(text)
        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(model=channel.model, messages=message)
                content = response.choices[0].message.content.strip()
                logger.log(LogLevel.Debug, "Got answer from OpenAi, returning")
                return content
            except openai.RateLimitError as e:
                retry_count += 1
                wait_time = backoff_factor ** retry_count
                logger.log(LogLevel.Warning, f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            except openai.OpenAIError as e:
                logger.log(LogLevel.Error, f"An OpenAI error occurred: {e}")
                break
            except Exception as e:
                logger.log(LogLevel.Error, f"An unexpected error occurred: {e}")
                break

        raise Exception("Max retries exceeded for OpenAI API request")

    async def generate_image(self, message: ChannelMessage):
        channel = message.channel

        logger.log(LogLevel.Debug, f"running generating image model {channel.image_model}")
        try:
            text = channel.get_image_generate_message(message.get_text())
            response = openai.images.generate(prompt=text[1]['content'], n=1, size=channel.image_size, model=channel.image_model)
            image_url = response.data[0].url
            logger.log(LogLevel.Debug, f'Image url: {image_url}')
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as img_response:
                    if img_response.status == 200:
                        image_path = f'download/aiimage{time.time()}.png'
                        with open(image_path, 'wb') as file:
                            file.write(await img_response.read())
                        message.media.append(image_path)
                    else:
                        logger.log(LogLevel.Error, f"Failed to download image, status code: {img_response.status}")
                        return
        except Exception as e:
            logger.log(LogLevel.Error, f"An error occurred while generating the image: {e}")
            return
