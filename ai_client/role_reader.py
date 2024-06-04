from data_reader import Reader
from ai_client.role import Role


class RoleReader(Reader):
    def __init__(self, file_path):
        super().__init__(file_path)

    def get_role(self, name: str) -> Role | None:
        roles = self.get_data('roles')
        for role in roles:
            if role['name'] == name:
                final_role = Role(name, role['system'], role['user'])
                return final_role
        return None


if __name__ == "__main__":
    r = RoleReader('roles/role.yaml')
    main = r.get_role('main')
    print(main)
