import os
import time
import asyncio
import logging
import subprocess
import aiohttp
from threading import Thread

from enums import LogLevel
from setup import logger


class WABridge:
    def __init__(self, server_url):
        self.server_url = server_url
        self.server_process = None
        self.start_time = 0
        self.state = "Disconnected"

    async def start(self, client_id, executable):
        """Start the server and check the connection."""
        server_path = os.path.join(os.path.dirname(__file__), "http_server.js")
        server_dir = os.path.dirname(server_path)

        self.server_process = subprocess.Popen(
            ["node", server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,  # Output as text instead of bytes
            cwd=server_dir
        )

        if not self.server_process or self.server_process.poll() is not None:
            raise Exception("Failed to run the server")

        # Stream logs in a separate thread
        Thread(target=self._stream, daemon=True).start()

        # Allow server to start
        await asyncio.sleep(2)
        data = {
            "clientId": client_id,
            "executablePath": executable,
        }
        await self.post('start', data)
        await asyncio.sleep(2)

    async def check_state(self):
        connection = await self.run('get-state', self._status_check)

        if self.state == "QR event":
            logger.log(LogLevel.Info, "[WhatsApp] QR event was triggered. Still connecting...")
            await self.run('get-state', self._status_check)

        if connection is not None:
            logger.log(LogLevel.Info, "[WhatsApp] Successfully connected!")
        else:
            logger.log(LogLevel.Error, "[WhatsApp] Connection timeout exceeded.")

    def _status_check(self, request):
        message = request.get("state")
        if message == "qr":
            logger.log(LogLevel.Info, "Got QR event")
            self.start_time = time.time()
            self.state = "QR event"
            return False
        elif message == "Connected":
            self.state = message
            return True
        return False

    async def run(self, endpoint, func, timeout=60):
        self.start_time = time.time()
        while True:
            response = await self.post(endpoint)
            if func(response):
                return response

            if time.time() - self.start_time > timeout:
                return None

            await asyncio.sleep(2)

    async def post(self, endpoint, data=None, sleep=1):
        url = f"{self.server_url}/{endpoint}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data) as response:
                    await asyncio.sleep(sleep)
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"success": False, "error": await response.text()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _stream(self):
        while True:
            output = self.server_process.stdout.readline()
            if output == "" and self.server_process.poll() is not None:
                break
            if output:
                logger.log(LogLevel.Info, output.strip())

    async def cache_groups(self):
        func = lambda r: int(r.get("size")) > 0
        await self.run('cache', func)

    async def send_message(self, group_id, message):
        data = {
            "groupId": group_id,
            "message": message
        }
        return await self.post('send-message', data)

    async def list_groups(self):
        return await self.post("list-groups")

    async def send_media(self, group_id, media, caption):
        if isinstance(media, str):
            media = [media]
        data = {
            "groupId": group_id,
            "media": media,
            "caption": caption
        }
        return await self.post('send-media', data, sleep=2)

    def terminate(self):
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            self.server_process.wait()

    def __del__(self):
        self.terminate()
