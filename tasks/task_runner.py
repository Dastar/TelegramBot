import asyncio
from logger import logger, LogLevel


class TaskRunner:
    def __init__(self):
        self.tasks = []
        self.stop_event = asyncio.Event()
        self.tg_client = None
        self.running_tasks = []

    def add_task(self, coro, interval):
        logger.log(LogLevel.Debug, "Adding a task")
        task = (coro.run, interval)
        self.tasks.append(task)

    async def _timed_task(self, task, interval):
        logger.log(LogLevel.Debug, "Running a task")
        check_interval = 1  # Check every second
        while not self.stop_event.is_set():
            await task(self.tg_client)
            for _ in range(int(interval / check_interval)):
                if self.stop_event.is_set():
                    break
                await asyncio.sleep(check_interval)

    async def run(self):
        self.running_tasks = [asyncio.create_task(self._timed_task(coro, interval)) for coro, interval in self.tasks]
        await asyncio.gather(*self.running_tasks)

    async def stop(self):
        self.stop_event.set()
        for task in self.running_tasks:
            task.cancel()
        await asyncio.gather(*self.running_tasks, return_exceptions=True)
