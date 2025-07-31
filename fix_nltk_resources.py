#!/usr/bin/env python3
"""
Fix NLTK Resources Script
Downloads missing NLTK resources to fix punkt_tab error
"""

import nltk
import os
import sys
import structlog

logger = structlog.get_logger()

def download_nltk_resources():
    """Download all required NLTK resources"""
    print("🔧 Downloading NLTK resources...")
    
    resources = [
        'punkt',
        'stopwords', 
        'punkt_tab',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words',
        'omw-1.4'  # Open Multilingual Wordnet
    ]
    
    for resource in resources:
        try:
            print(f"📦 Downloading {resource}...")
            nltk.download(resource, quiet=True)
            print(f"✅ Downloaded {resource}")
        except Exception as e:
            print(f"⚠️ Failed to download {resource}: {e}")
    
    # Test the tokenization
    try:
        from nltk.tokenize import word_tokenize
        test_text = "This is a test sentence for tokenization."
        tokens = word_tokenize(test_text)
        print(f"✅ Tokenization test successful: {tokens}")
    except Exception as e:
        print(f"❌ Tokenization test failed: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🚀 Fixing NLTK resources for AI Backend...")
    
    # Download resources
    success = download_nltk_resources()
    
    if success:
        print("🎉 NLTK resources fixed successfully!")
        print("🔄 Please restart the ai-backend-python service:")
        print("   sudo systemctl restart ai-backend-python")
    else:
        print("❌ Failed to fix NLTK resources")
        sys.exit(1)

if __name__ == "__main__":
    main() 