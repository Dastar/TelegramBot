import asyncio
from logger import logger, LogLevel


class TaskRunner:
    def __init__(self):
        self.tasks = []
        self.stop_event = asyncio.Event()
        self.tg_client = None

    def add_task(self, coro, interval):
        task = asyncio.create_task(self._timed_task(coro.run, interval))
        self.tasks.append(task)

    async def _timed_task(self, task, interval):
        check_interval = 1  # Check every second
        while not self.stop_event.is_set():
            await task(self.tg_client)
            for _ in range(int(interval / check_interval)):
                if self.stop_event.is_set():
                    break
                await asyncio.sleep(check_interval)

    async def run(self):
        logger.log(LogLevel.Info, f"Running {len(self.tasks)} tasks.")
        await asyncio.gather(*self.tasks)

    async def stop(self):
        logger.log(LogLevel.Info, "Task Runner received termination signal, exiting...")
        self.stop_event.set()
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
