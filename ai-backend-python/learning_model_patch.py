
# Add to app/models/sql_models.py in the Learning class

@property
def success_rate(self) -> float:
    """Calculate success rate from learning data"""
    try:
        if not self.learning_data:
            return 0.0
        
        # Extract success information from learning_data
        if isinstance(self.learning_data, dict):
            success_count = self.learning_data.get('success_count', 0)
            total_count = self.learning_data.get('total_count', 1)
            return float(success_count) / float(total_count) if total_count > 0 else 0.0
        
        return 0.0
    except Exception:
        return 0.0

@property
def confidence(self) -> float:
    """Get confidence from learning data"""
    try:
        if not self.learning_data:
            return 0.5
        
        if isinstance(self.learning_data, dict):
            return float(self.learning_data.get('confidence', 0.5))
        
        return 0.5
    except Exception:
        return 0.5

@property
def improvement_score(self) -> float:
    """Calculate improvement score"""
    try:
        if not self.learning_data:
            return 0.0
        
        if isinstance(self.learning_data, dict):
            return float(self.learning_data.get('improvement_score', 0.0))
        
        return 0.0
    except Exception:
        return 0.0
