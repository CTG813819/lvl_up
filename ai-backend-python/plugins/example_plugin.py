import sys
import os
# Add the plugins directory to the path so we can import base_plugin
sys.path.append(os.path.dirname(__file__))
from base_plugin import BasePlugin

class ExamplePlugin(BasePlugin):
    def describe(self) -> str:
        return "Example plugin that echoes input data."

    def run(self, data: dict) -> dict:
        return {"echo": data}

    def test(self) -> bool:
        return self.run({"test": 123}) == {"echo": {"test": 123}} 