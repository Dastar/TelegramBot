import requests
import json
import subprocess
import time
import os
import threading

from logger import LogLevel
from setup import logger
from events.channel_message import ChannelMessage


class WhatsAppClient:
    def __init__(self, client_id, server_url, executable='/usr/bin/google-chrome-stable'):
        self.server_url = server_url
        self.server_process = None
        self.client_id = client_id
        self.executable = executable
        self.start_time = 0
        self.state = "Disconnected"

    def start(self):
        """Start the server and check the connection."""
        # Start the Node.js server
        server_path = os.path.join(os.path.dirname(__file__), "http_server.js")
        server_dir = os.path.dirname(server_path)

        self.server_process = subprocess.Popen(
            ["node", server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr with stdout
            text=True,  # Output as text instead of bytes
            cwd=server_dir
        )

        # Verify the server process started successfully
        if not self.server_process or self.server_process.poll() is not None:
            raise Exception("Failed to run the server")

        # Stream logs from the server in a separate thread
        threading.Thread(target=self._stream, daemon=True).start()

        # Wait briefly to allow server startup
        time.sleep(2)
        data = {
            "clientId": self.client_id,
            "executablePath": self.executable,
        }
        self.post('start', data)
        time.sleep(2)

        connection = self.run('get-state', lambda r: self._status_check(r))

        if self.state == "QR event":
            logger.log(LogLevel.Info, "[WhatsApp] QR event was triggered. Still connecting...")
            self.run('get-state', lambda r: self._status_check(r))

        if connection is not None:
            logger.log(LogLevel.Info, "[WhatsApp] Successfully connected!")
        else:
            logger.log(LogLevel.Error, "[WhatsApp] Connection timeout exceeded.")

    def send(self, message: ChannelMessage):
        target = message.get_wa_target()
        if self.state != 'Connected':
            logger.log(LogLevel.Error, "WhatsApp client is not connected")
            return
        if target.strip() == "":
            logger.log(LogLevel.Error, "No target to send WhatsApp")
            return
        if not message.approved:
            return

        logger.log(LogLevel.Info, f"Sending WhatsApp message to target: {target}")
        text = message.get_text()
        media = message.get_media()
        if media:
            self.send_media(target, media, text)
        elif text.strip():
            self.send_message(target, text)

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

    def run(self, endpoint, func, timeout=60):
        self.start_time = time.time()
        while True:
            response = self.post(endpoint)
            if func(response):
                return response
                # Exit if time exceeds 1 minute
            if time.time() - self.start_time > timeout:
                return None

            # Wait 2 seconds before retrying
            time.sleep(2)

    def cache_groups(self):
        groups = self.run('cache', lambda r: int(r.get('size')) > 0)
        if groups is not None:
            logger.log(LogLevel.Info, f'[WhatsApp] Found {groups.get('size')} groups')

    def post(self, endpoint, data=None, sleep=1):
        url = f"{self.server_url}/{endpoint}"
        try:
            response = requests.post(url, json=data)
            time.sleep(sleep)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _stream(self):
        while True:
            output = self.server_process.stdout.readline()
            if output == "" and self.server_process.poll() is not None:
                break
            if output:
                logger.log(LogLevel.Info, output.strip())

    def send_message(self, group_id, message):
        """
        Send a message to the specified group ID.
        :param group_id: ID of the target group
        :param message: Message to send
        """
        data = {
            "groupId": group_id,
            "message": message
        }
        return self.post('send-message', data)

    def list_groups(self):
        """
        Retrieve a list of cached groups.
        """
        return self.post("list-groups")

    def send_media(self, group_id, media, caption):
        if isinstance(media, str):
            media = [media]
        data = {
            "groupId": group_id,
            "media": media,
            "caption": caption
        }
        return self.post('send-media', data, sleep=2)

    def terminate(self):
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            self.server_process.wait()  # Ensure the process is fully terminated

    def __del__(self):
        self.terminate()


# Example Usage
if __name__ == "__main__":
    pass
