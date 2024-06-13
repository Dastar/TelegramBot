from collections import defaultdict
from typing import Optional

from ai_client.role import Role


class Channel:
    def __init__(self, target, role: Optional[Role], tags, model, image_role: Optional[Role], image_model, image_size):
        self.target = target
        self.role = role
        if self.role:
            self.role.init_tags(tags)
        self.model = model
        self.image_role = image_role
        self.image_model = image_model
        self.image_size = image_size

    def init_role(self, role: Role, tags):
        self.role = role
        self.role.init_tags(tags)

    def get_message(self, text):
        return self.role.create_message(text)

    def get_image_generate_message(self, text):
        return self.image_role.create_message(text)

    def __eq__(self, other):
        if not isinstance(other, Channel):
            return False
        return self.target == other.target and self.role.name == other.role.name


class ChannelRegistry:
    def __init__(self):
        self.channels = {}

    def add_channel(self, monitored, channel):
        self.channels[monitored] = channel

    def add_channels(self, channel: Channel, monitored: list):
        for m in monitored:
            self.add_channel(m, channel)

    def get_channel(self, monitored):
        if monitored in self.channels:
            return self.channels[monitored]
        elif f'@{monitored}' in self.channels:
            return self.channels[f'@{monitored}']
        else:
            return None

    def get_monitored(self):
        sources = list(self.channels.keys())
        return sources
