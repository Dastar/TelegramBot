import asyncio

from events.channel_message import ChannelMessage


class MessageQueue:
    def __init__(self):
        self.messages = []
        self._lock = asyncio.Lock()

    async def put(self, message: ChannelMessage):
        async with self._lock:
            self.messages.append(message)

    async def get(self, id):
        async with self._lock:
            return next((message for message in self.messages if id in message.sent_id), None)

    async def pop(self, id):
        message = self.get(id)
        if message is None:
            return None

        async with self._lock:
            self.messages.remove(message)

    def __len__(self):
        return len(self.messages)
