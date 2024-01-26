import json
from pathlib import Path


class ReadMeta:
    def __init__(self, config_file):
        print(config_file)
        self.base = Path(config_file).resolve().parent

        with open(config_file, mode='r') as config:
            self.metadata = json.load(config)
        print(type(self.metadata))

    def project_name(self) -> str:
        return self.metadata['project_name']

    def version(self):
        return self.metadata['version']

    def logger(self, which):
        return Path(self.metadata['logger'][which])
