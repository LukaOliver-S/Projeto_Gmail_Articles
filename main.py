from scripts.run_digest import run_digest
import os
import json


class Main:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path

    def run_basic(self):
        run_digest(self.config_path)


if __name__ == "__main__":
    main = Main()
    main.run_basic()