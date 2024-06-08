from collections import defaultdict
from typing import Optional

from ai_client.role import Role


class Channel:
    def __init__(self, target, role: Optional[Role], tags, model):
        self.target = target
        self.role = role
        if self.role:
            self.role.init_tags(tags)
        self.model = model

    def init_role(self, role: Role, tags):
        self.role = role
        self.role.init_tags(tags)

    def get_message(self, text):
        return self.role.create_message(text)

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
        return list(self.channels.keys())
