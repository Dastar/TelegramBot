import asyncio
from logger import logger, LogLevel


class TaskRunner:
    def __init__(self):
        self.tasks = {}
        self.event_stopper = None

    def add_task(self, name, task):
        self.tasks[name] = task

    def remove_task(self, name):
        if name in self.tasks:
            return self.tasks.pop(name)

    async def run(self):
        while not self.event_stopper.is_set():
            for task in self.tasks.values():
                if self.event_stopper.is_set():
                    break
                await task.run()
