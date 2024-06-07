from data_reader import Reader
from ai_client.role import Role


class RoleReader(Reader):
    def __init__(self, file_path):
        super().__init__(file_path)

    def get_role(self, name):
        return self.get_attribute('roles', name, self.role_reader)

    @staticmethod
    def role_reader(data):
        role = Role(data['name'], data['system'], data['user'])
        return role


if __name__ == "__main__":
    r = RoleReader('roles/role.yaml')
    main = r.get_role('main')
    print(main)
