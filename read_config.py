import configparser


class Configs:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.file = config_file
        self.title = "DEFAULT"

    def open(self):
        self.config.read(self.file)

    def read(self, property_name):
        try:
            output = self.config[self.title][property_name]
        except Exception:
            raise Exception(f"No property with name {property_name} in configuration file")

        if output.find(';') != -1:
            output = output.split(';')
            output = [line for line in output if line.strip()]
        return output


configs = Configs('config.ini')
configs.open()
