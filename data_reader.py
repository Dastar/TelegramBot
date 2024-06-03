import yaml


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
            print(f"File {self.file_path} not found.")
            return None
        except yaml.YAMLError:
            print("Error parsing YAML.")
            return None

