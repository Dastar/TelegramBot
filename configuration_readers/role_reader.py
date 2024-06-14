from configuration_readers.data_reader import DataReader
from ai_client.role import Role


class RoleReader:
    def __init__(self, reader: DataReader):
        self.reader = reader

    def get_role(self, name):
        return self.reader.get_attribute('roles', name, self.role_reader)

    def save(self, role: Role):
        def updater(data):
            data['system'] = role.system.original_content.strip()
            data['user'] = role.user.original_content.strip()
            return True

        self.reader.save('roles', role.name, updater)

    @staticmethod
    def role_reader(data):
        role = Role(data['name'], data['system'], data['user'])
        return role
