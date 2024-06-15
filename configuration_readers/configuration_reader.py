import configparser
import os

from enums import ConfigProperty


class Configurations:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.file = config_file
        self.title = "DEFAULT"

    def open(self):
        self.config.read(self.file)
        return self

    def read(self, property_name):
        if self.title not in self.config:
            raise Exception(f"No section with title {self.title} in configuration file")

        if property_name not in self.config[self.title]:
            raise Exception(f"No property with name {property_name} in configuration file")

        output = self.config[self.title][property_name]

        if ';' in output:
            output = output.split(';')
            output = [line for line in output if line.strip()]
        return output

    def read_configuration(self):
        """Read and set up configuration values."""
        os.environ['OPENAI_API_KEY'] = self.read(ConfigProperty.ApiKey)

        return {
            'api_key': self.read(ConfigProperty.ApiKey),
            'api_id': self.read(ConfigProperty.ApiId),
            'api_hash': self.read(ConfigProperty.ApiHash),
            'bot_config': self.read(ConfigProperty.BotConfig),
            'forward_message': self.read(ConfigProperty.ForwardMessage),
            'session_name': self.read(ConfigProperty.SessionName),
            'to_delay': self.read('Delay') == 'True',
        }
