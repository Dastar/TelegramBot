import asyncio
import time
from logger import logger, LogLevel


class Task:
    def __init__(self, delay):
        self.delay = delay
        self.last_played = time.time()

    async def run(self, client):
        pass


