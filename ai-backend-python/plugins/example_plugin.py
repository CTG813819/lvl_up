import sys
import os
from datetime import datetime
# Add the plugins directory to the path so we can import base_plugin
sys.path.append(os.path.dirname(__file__))
from base_plugin import BasePlugin

class ExamplePlugin(BasePlugin):
    def describe(self) -> str:
        return "Example plugin that processes data and provides insights."
    
    def run(self, data: dict) -> dict:
        # Real implementation - analyze data and provide insights
        insights = []
        
        if isinstance(data, dict):
            # Analyze data structure
            insights.append(f"Data has {len(data)} keys")
            
            # Check for specific patterns
            if "error" in str(data).lower():
                insights.append("Data contains error-related content")
            
            if "test" in data:
                insights.append("Test data detected")
        
        return {
            "result": "analyzed",
            "data": data,
            "insights": insights,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "plugin": "ExamplePlugin"
        }
    
    def test(self) -> bool:
        return self.run({"test": "data"})["result"] == "analyzed"
