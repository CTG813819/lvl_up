class BasePlugin:
    """Base interface for all plugins/extensions."""
    def describe(self) -> str:
        """Return a description of the plugin."""
        raise NotImplementedError

    def run(self, data: dict) -> dict:
        """Run the plugin on input data and return results."""
        raise NotImplementedError

    def test(self) -> bool:
        """Run a self-test to verify plugin functionality."""
        raise NotImplementedError 