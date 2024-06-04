import yaml
from logger import logger, LogLevel


class Reader:
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
