from configuration_readers.data_reader import DataReader
from tg_client.channel_registry import Channel
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
        image_role = self.role_reader.get_role(data['image_role'])
        image_model = data['image_model']
        size = data['image_size']
        channel = Channel(f'@{data['target']}', role, data['tags'], data['model'], image_role, image_model, size)
        sources = [f'@{m}' for m in data['monitored'].split(';') if m.strip()]
        return channel, sources
