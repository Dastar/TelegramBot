import asyncio

from events.channel_message import ChannelMessage


class MessagesDict:
    def __init__(self):
        self._dict = {}
        self._lock = asyncio.Lock()

    async def set(self, key, value: ChannelMessage):
        async with self._lock:
            self._dict[key] = value

    async def get(self, key, default=None) -> ChannelMessage:
        async with self._lock:
            return self._dict.get(key, default)

    async def delete(self, key):
        async with self._lock:
            if key in self._dict:
                del self._dict[key]

    async def contains(self, key):
        async with self._lock:
            return key in self._dict

    async def keys(self):
        async with self._lock:
            return list(self._dict.keys())

    async def values(self):
        async with self._lock:
            return list(self._dict.values())

    async def items(self):
        async with self._lock:
            return list(self._dict.items())

    async def clear(self):
        async with self._lock:
            self._dict.clear()
