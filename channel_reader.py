from data_reader import Reader
from channel_registry import Channel
from ai_client.role_reader import RoleReader


class ChannelReader(Reader):
    def __init__(self, file_path, role_reader: RoleReader):
        super().__init__(file_path)
        self.role_reader = role_reader

    def reload_reader(self, role_file):
        self.role_reader = RoleReader(role_file)

    def get_channel(self, name):
        channels = self.get_data('channels')
        for channel in channels:
            if channel['name'] == name:
                out = Channel(f'@{channel['target']}', self.role_reader.get_role(channel['role']), channel['tags'])
                monitored = [f'@{m}' for m in channel['monitored'].split(';') if m.strip()]
                return out, monitored

        return None, []

    def get_channels(self):
        data = self.get_data('channels')
        for d in data:
            channel = Channel(f'@{d['target']}', self.role_reader.get_role(d['role']), d['tags'])
            monitored = [f'@{m}' for m in d['monitored'].split(';') if m.strip()]
            yield channel, monitored
