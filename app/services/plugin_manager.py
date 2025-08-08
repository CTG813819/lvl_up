import os
import importlib.util
import sys
from typing import Dict, List, Any

PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'plugins')
PLUGIN_DIR = os.path.abspath(PLUGIN_DIR)

class PluginManager:
    def __init__(self):
        self.plugins = {}  # name -> plugin instance
        self.reload_plugins()

    def reload_plugins(self):
        self.plugins = {}
        for fname in os.listdir(PLUGIN_DIR):
            if fname.endswith('.py') and fname != 'base_plugin.py':
                plugin_name = fname[:-3]
                plugin_path = os.path.join(PLUGIN_DIR, fname)
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[plugin_name] = module
                    try:
                        spec.loader.exec_module(module)
                        for attr in dir(module):
                            obj = getattr(module, attr)
                            if hasattr(obj, '__bases__') and 'BasePlugin' in [b.__name__ for b in obj.__bases__]:
                                self.plugins[plugin_name] = obj()
                    except Exception as e:
                        print(f"Failed to load plugin {plugin_name}: {e}")

    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())

    def describe_plugin(self, name: str) -> str:
        plugin = self.plugins.get(name)
        return plugin.describe() if plugin else "Plugin not found"

    def run_plugin(self, name: str, data: Dict[str, Any]) -> Any:
        plugin = self.plugins.get(name)
        if not plugin:
            return {"error": "Plugin not found"}
        return plugin.run(data)

    def test_plugin(self, name: str) -> bool:
        plugin = self.plugins.get(name)
        if not plugin:
            return False
        return plugin.test() 