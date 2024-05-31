import asyncio
import openai
from logger import logger, LogLevel
from ai_message import AIMessage


def format_content(content: str, tag, text):
    return content.replace(tag, text)


class AIClient:
    def __init__(self, client: openai.OpenAI, language="English", model="gpt-3.5-turbo"):
        self.client = client
        self.messages = []
        self.outputLanguage = language
        self.model = model

    def add_role(self, role, content):
        message = AIMessage(role, content)
        message.format_content('%%LANGUAGE%%', self.outputLanguage)
        self.messages.append(message)

    def remove_role(self, role):
        self.messages = [message for message in self.messages if message.role != role]

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


