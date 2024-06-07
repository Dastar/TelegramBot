import yaml
from logger import LogLevel
from setup import logger


class DataReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = self._load_yaml()

    def _load_yaml(self):
        try:
            with open(self.file_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file)
                return data
        except FileNotFoundError:
            logger.log(LogLevel.Error, f"File {self.file_path} not found.")
            return None
        except yaml.YAMLError as y:
            logger.log(LogLevel.Error, f"Error parsing YAML. {y}")
            return None
        except Exception as ex:
            logger.log(LogLevel.Error, f"Unexpected error: {ex}")
            return None

    def get_data(self, tag):
        return self.data.get(tag, []) if self.data else []

    def get_attribute(self, section, tag, func):
        data = self.get_data(section)
        for d in data:
            if d['name'] == tag:
                return func(d)
        return None

    def get_attributes(self, section, func):
        data = self.get_data(section)
        for d in data:
            yield func(d)
