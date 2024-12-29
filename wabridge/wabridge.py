import requests
import json
import subprocess
import time
import os
import threading

from logger import LogLevel
from setup import logger


class WhatsAppClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.server_process = None
        self.ready = False

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
        time.sleep(5)
        self.post('start', {"clientId": "dastar"})
        time.sleep(2)

        connection = self.run('is-connected', lambda r: 'true' in r.get('message'))
        if connection is not None:
            logger.log(LogLevel.Info, "[WhatsApp] Successfully connected!")
        else:
            logger.log(LogLevel.Error, "[WhatsApp] Connection timeout exceeded.")

    def run(self, endpoint, func, timeout=60):
        start_time = time.time()
        while True:
            response = self.post(endpoint)
            if func(response):
                return response
                # Exit if time exceeds 1 minute
            if time.time() - start_time > timeout:
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
                if output.strip() == '[WhatsApp] Client is ready!':
                    self.ready = True

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


# Example Usage
if __name__ == "__main__":
    # Start the server

    # Replace this URL with your server's address
    server_url = "http://localhost:3000"
    client = WhatsAppClient(server_url)
    client.start()
    # List groups

    groups = client.list_groups()
    # print("Groups:", json.dumps(groups, indent=4))

    # Send a test message
    group_id = "120363386281984067@g.us"  # Replace with a valid group ID
    message = "Hello from Python Client!"
    result = client.send_message(group_id, message)
    print("Send Message Result:", json.dumps(result, indent=4))

    # Keep the server running (Press Ctrl+C to stop)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[Server] Shutting down server...")
        client.server_process.terminate()
