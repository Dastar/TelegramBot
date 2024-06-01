import asyncio
import time
from urllib import request
import aiohttp
import openai
from logger import logger, LogLevel
from ai_message import AIMessage


def format_content(content: str, tag, text):
    return content.replace(tag, text)


class AIClient:
    def __init__(self, client: openai.OpenAI, language, model="gpt-3.5-turbo"):
        self.client = client
        self.messages = []
        self.outputLanguage = language
        self.model = model

    def add_role(self, role, content):
        message = AIMessage(role, content)
        message.format_content('%%LANGUAGE%%', self.outputLanguage)
        self.messages.append(message)

    def remove_role(self, role):
        self.messages = [message for message in self.messages if message['role'] != role]

    async def run_model(self, text):
        logger.log(LogLevel.Debug, "run_model running")
        messages = []
        for message in self.messages:
            messages.append(message.create_message(text))

        retry_count = 0
        max_retries = 5
        backoff_factor = 2

        while retry_count < max_retries:
            try:
                response = self.client.chat.completions.create(model=self.model, messages=messages)
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

    async def generate_image2(self, text):
        logger.log(LogLevel.Debug, f"Generating Image")
        response = openai.images.generate(prompt=text, n=1, size="1024x1024", model="dall-e-3")
        image_url = response['data'][0]['url']
        img = request.get(image_url)
        if img.status_code == 200:
            with open(f'assets/download/aiimage{time.time()}.png') as file:
                file.write(img.content)
            return f'assets/download/aiimage{time.time()}.png'
        return ''

    async def generate_image(self, text):
        logger.log(LogLevel.Debug, "Generating Image")
        try:
            response = openai.images.generate(prompt=text, n=1, size="1024x1024", model="dall-e-3")
            image_url = response.data[0].url
            logger.log(LogLevel.Debug, f'Image url: {image_url}')
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as img_response:
                    if img_response.status == 200:
                        image_path = f'assets/download/aiimage{time.time()}.png'
                        with open(image_path, 'wb') as file:
                            file.write(await img_response.read())
                        return image_path
                    else:
                        logger.log(LogLevel.Error, f"Failed to download image, status code: {img_response.status}")
                        return ''
        except Exception as e:
            logger.log(LogLevel.Error, f"An error occurred while generating the image: {e}")
            return ''



