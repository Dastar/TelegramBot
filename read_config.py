import configparser


class Configs:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.file = config_file
        self.title = "DEFAULT"

    def open(self):
        self.config.read(self.file)

    def read(self, property):
        if self.title not in self.config:
            raise Exception(f"No section with title {self.title} in configuration file")

        if property not in self.config[self.title]:
            raise Exception(f"No property with name {property} in configuration file")

        output = self.config[self.title][property]

        if ';' in output:
            output = output.split(';')
            output = [line for line in output if line.strip()]
        return output


configs = Configs('config.ini')
configs.open()

try:
    role_file = configs.read('RoleFile')
    print(role_file)
except Exception as e:
    print(e)
