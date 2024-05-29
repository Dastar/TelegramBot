import configparser


class Configs:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.file = config_file
        self.title = "DEFAULT"

    def open(self):
        self.config.read(self.file)

    def read(self, property):
        try:
            output = self.config[self.title][property]
        except:
            raise Exception(f"No property with name {property} in configuration file")

        if output.find(';') != -1:
            output = output.split(';')
        return output


configs = Configs('config.ini')
configs.open()
