from configuration_readers.data_reader import DataReader
from channel_registry import Channel
from configuration_readers.role_reader import RoleReader


class ChannelReader:
    def __init__(self, role_reader: RoleReader, reader: DataReader):
        self.role_reader = role_reader
        self.reader = reader

    def get_channels(self):
        for channel in self.reader.get_attributes('channels', self.channel_reader):
            yield channel

    def channel_reader(self, data):
        role = self.role_reader.get_role(data['role'])
        channel = Channel(f'@{data['target']}', role, data['tags'], data['model'])
        sources = [f'@{m}' for m in data['monitored'].split(';') if m.strip()]
        return channel, sources
