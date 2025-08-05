#!/usr/bin/env python3
"""
Install All Missing Packages
===========================
Install all missing packages for the backend server
"""

import subprocess
import sys

def run_cmd(cmd):
    print(f"🔄 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Success: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ Error: {result.stderr.strip()}")
        return False

def main():
    print("🔧 Install All Missing Packages")
    print("=" * 40)
    
    # Install all required packages
    print("\n📦 Installing all required packages...")
    packages = [
        # Core ML/NLP packages
        "numpy",
        "pandas", 
        "scikit-learn",
        "nltk",
        "spacy",
        "textblob",
        "wordcloud",
        
        # Visualization
        "matplotlib",
        "seaborn",
        "plotly",
        "bokeh",
        
        # Web framework
        "fastapi",
        "uvicorn",
        "python-multipart",
        
        # Database
        "sqlalchemy",
        "asyncpg",
        "psycopg2-binary",
        "alembic",
        
        # Authentication & Security
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-dotenv",
        
        # HTTP & Networking
        "requests",
        "aiohttp",
        "httpx",
        
        # Logging & Monitoring
        "structlog",
        "psutil",
        
        # Additional utilities
        "python-dateutil",
        "pytz",
        "pydantic",
        "email-validator"
    ]
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if run_cmd(f"pip install {package}"):
            print(f"✅ {package} installed successfully")
        else:
            print(f"⚠️  Failed to install {package}, continuing...")
    
    # Download NLTK data
    print("\n📚 Downloading NLTK data...")
    nltk_data = [
        "punkt",
        "stopwords", 
        "wordnet",
        "averaged_perceptron_tagger",
        "maxent_ne_chunker",
        "words"
    ]
    
    for data in nltk_data:
        print(f"📚 Downloading NLTK {data}...")
        download_cmd = f"python3 -c 'import nltk; nltk.download(\"{data}\", quiet=True)'"
        run_cmd(download_cmd)
    
    # Test critical imports
    print("\n🧪 Testing critical imports...")
    test_imports = [
        "import numpy",
        "import pandas", 
        "import sklearn",
        "import nltk",
        "import fastapi",
        "import uvicorn"
    ]
    
    for imp in test_imports:
        test_cmd = f"python3 -c '{imp}; print(\"✅ {imp} works\")'"
        if run_cmd(test_cmd):
            print(f"✅ {imp} imported successfully")
        else:
            print(f"❌ {imp} failed")
    
    print("\n🎉 All package installation complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 