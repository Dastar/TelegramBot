import asyncio
import time
import aiohttp
import openai
from openai import OpenAI

from logger import LogLevel
from events.channel_message import ChannelMessage
from setup import logger


def format_content(content: str, tag, text):
    return content.replace(tag, text)


class AIClient:
    def __init__(self, api_key, max_retries, base_url, is_on: True):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.is_on = is_on
        self.max_retries = max_retries if max_retries < 6 else 5

    async def turn_off(self, event):
        logger.log(LogLevel.Debug, "Model is off")
        self.is_on = False

    async def turn_on(self, event):
        logger.log(LogLevel.Debug, "Model is on")
        self.is_on = True

    async def run(self, message: ChannelMessage):
        logger.log(LogLevel.Debug, 'Running AI model')
        if not self.is_on:
            message.output_text = f"Model is Off. Original message:\n\n{message.get_text()}"
            return

        content, result = await self.run_model(message.get_text(), message.channel)
        message.output_text = content
        if not result:
            message.to_sender()
            return

    async def run_model(self, text: str, channel):
        logger.log(LogLevel.Debug, f"running text model {channel.model}")

        retry_count = 0
        backoff_factor = 2

        message = channel.get_message(text)
        while retry_count < self.max_retries:
            try:
                response = self.client.chat.completions.create(model=channel.model, messages=message)
                content = response.choices[0].message.content.strip()
                logger.log(LogLevel.Debug, "Got answer from OpenAi, returning")
                return content, True
            except openai.RateLimitError as e:
                retry_count += 1
                wait_time = backoff_factor ** retry_count
                logger.log(LogLevel.Warning, f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                logger.log(LogLevel.Debug, f"The error is: {e}")
                await asyncio.sleep(wait_time)
            except openai.OpenAIError as e:
                logger.log(LogLevel.Error, f"An OpenAI error occurred: {e}")
                break
            except Exception as e:
                logger.log(LogLevel.Error, f"An unexpected error occurred: {e}")
                break

        return "Error: Max retries exceeded for OpenAI API request", False

    async def generate_image(self, message: ChannelMessage):
        if not self.is_on:
            raise Exception("Model is off.")
        channel = message.channel

        logger.log(LogLevel.Debug, f"Starting image generation using model {channel.image_model}")

        try:
            # Prepare the prompt for image generation
            text = channel.get_image_generate_message(message.get_text())
            prompt = text[1]['content']  # Extract prompt content

            # Request image generation from OpenAI
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size=channel.image_size,
                model=channel.image_model
            )

            # Process the response
            image_url = response.data[0].url
            logger.log(LogLevel.Info, f"Generated image URL: {image_url}")

            # Download and save the image locally
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as img_response:
                    if img_response.status == 200:
                        image_path = f'download/generated_image_{time.time()}.png'
                        with open(image_path, 'wb') as file:
                            file.write(await img_response.read())

                        # Attach the image to the message
                        # message.media.clear()
                        # message.media.append(image_path)
                        logger.log(LogLevel.Info, f"Image saved at {image_path}")
                        return image_path
                    else:
                        logger.log(LogLevel.Error, f"Failed to download image. Status code: {img_response.status}")

        except openai.OpenAIError as e:
            logger.log(LogLevel.Error, f"OpenAI error during image generation: {e}")
        except Exception as e:
            logger.log(LogLevel.Error, f"Unexpected error in image generation: {e}")
