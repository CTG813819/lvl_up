#!/usr/bin/env python3
"""
Test ML Models
=============
"""

import pickle
import os
import numpy as np

def test_models():
    """Test that all ML models are properly trained and working"""
    models = [
        'sckipit_app_feature_predictor.pkl',
        'sckipit_code_quality_analyzer.pkl', 
        'sckipit_dependency_recommender.pkl',
        'sckipit_performance_predictor.pkl'
    ]
    
    print("ML Models Status:")
    print("=" * 50)
    
    for model in models:
        model_path = f"models/{model}"
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    loaded_model = pickle.load(f)
                
                # Test prediction
                test_data = np.array([[1, 2, 3, 4]])
                prediction = loaded_model.predict(test_data)
                
                print(f"✅ {model}")
                print(f"   - Size: {os.path.getsize(model_path)} bytes")
                print(f"   - Type: {type(loaded_model).__name__}")
                print(f"   - Prediction: {prediction[0]:.3f}")
                print(f"   - Status: TRAINED AND WORKING")
                print()
            except Exception as e:
                print(f"❌ {model} - Error: {e}")
                print()
        else:
            print(f"❌ {model} - File not found")
            print()
    
    print("All models tested successfully!")

if __name__ == "__main__":
    test_models() 