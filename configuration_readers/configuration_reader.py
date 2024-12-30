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

    def read_int(self, property_name):
        try:
            data = int(self.read(property_name))
            return data
        except Exception as e:
            return 0

    def read_bool(self, property_name):
        try:
            data = self.read(property_name) == 'True'
            return data
        except:
            return False

    def read_str(self, property_name):
        try:
            data = self.read(property_name)
            return data
        except:
            return False

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
            'max_retries': int(self.read('MaxGPTRetries')),
            'bot_token': self.read('BotToken'),
            'base_url': self.read('BaseUrl'),
            'clientId': self.read('ClientID'),
            'exe': self.read('Executable'),
        }

    def safe_read_configuration(self):
        """Read and set up configuration values."""
        os.environ['OPENAI_API_KEY'] = self.read(ConfigProperty.ApiKey)

        return {
            'api_key': self.read_str(ConfigProperty.ApiKey),
            'api_id': self.read_str(ConfigProperty.ApiId),
            'api_hash': self.read_str(ConfigProperty.ApiHash),
            'bot_config': self.read_str(ConfigProperty.BotConfig),
            'forward_message': self.read_str(ConfigProperty.ForwardMessage),
            'session_name': self.read_str(ConfigProperty.SessionName),
            'to_delay': self.read_bool('Delay'),
            'max_retries': self.read_int('MaxGPTRetries'),
            'bot_token': self.read('BotToken'),
            'base_url': self.read('BaseUrl'),
            'clientId': self.read('ClientID'),
            'exe': self.read('Executable'),
        }
