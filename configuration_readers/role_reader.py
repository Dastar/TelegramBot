from configuration_readers.data_reader import DataReader
from ai_client.role import Role


class RoleReader:
    def __init__(self, reader):
        self.reader = reader

    def get_role(self, name):
        return self.reader.get_attribute('roles', name, self.role_reader)

    @staticmethod
    def role_reader(data):
        role = Role(data['name'], data['system'], data['user'])
        return role
