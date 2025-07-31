#!/usr/bin/env python3
"""
Fix NLTK Missing
================
Install nltk and other immediate missing packages
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
    print("🔧 Fix NLTK Missing")
    print("=" * 30)
    
    # Install immediate missing packages
    print("\n📦 Installing missing packages...")
    packages = [
        "nltk",
        "spacy",
        "textblob",
        "wordcloud"
    ]
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if run_cmd(f"pip install {package}"):
            print(f"✅ {package} installed")
        else:
            print(f"❌ Failed to install {package}")
            return False
    
    # Download NLTK data
    print("\n📚 Downloading NLTK data...")
    nltk_data = ["punkt", "stopwords", "wordnet"]
    
    for data in nltk_data:
        print(f"📚 Downloading {data}...")
        download_cmd = f"python3 -c 'import nltk; nltk.download(\"{data}\", quiet=True)'"
        run_cmd(download_cmd)
    
    # Test nltk import
    print("\n🧪 Testing nltk import...")
    if run_cmd("python3 -c 'import nltk; print(\"nltk imported successfully\")'"):
        print("✅ nltk imported successfully")
    else:
        print("❌ nltk import failed")
        return False
    
    print("\n🎉 NLTK fix complete!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 