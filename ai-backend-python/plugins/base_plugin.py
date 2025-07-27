class BasePlugin:
    """Base interface for all plugins/extensions."""
    
    def describe(self) -> str:
        """Return a description of the plugin."""
        return f"Plugin: {self.__class__.__name__}"
    
    def run(self, data: dict) -> dict:
        """Run the plugin on input data and return results."""
        # Default implementation - process data and return result
        return {
            "result": "processed",
            "data": data,
            "plugin": self.__class__.__name__,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def test(self) -> bool:
        """Run a self-test to verify plugin functionality."""
        try:
            # Test with sample data
            test_data = {"test": "data", "value": 123}
            result = self.run(test_data)
            return isinstance(result, dict) and "result" in result
        except Exception:
            return False
