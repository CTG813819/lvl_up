#!/usr/bin/env python3

import sys
import os

# Add the project path
sys.path.append('/home/ubuntu/ai-backend-python')

def test_dependencies():
    """Test if required dependencies are available"""
    
    print("🔍 Testing Project Warmaster dependencies...")
    
    try:
        import cryptography
        print(f"✅ Cryptography library found: {cryptography.__version__}")
    except ImportError as e:
        print(f"❌ Cryptography library not found: {e}")
        return False
    
    try:
        from cryptography.fernet import Fernet
        print("✅ Fernet encryption available")
    except ImportError as e:
        print(f"❌ Fernet not available: {e}")
        return False
    
    try:
        from cryptography.hazmat.primitives import hashes
        print("✅ Cryptography hashes available")
    except ImportError as e:
        print(f"❌ Cryptography hashes not available: {e}")
        return False
    
    try:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        print("✅ PBKDF2HMAC available")
    except ImportError as e:
        print(f"❌ PBKDF2HMAC not available: {e}")
        return False
    
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        print("✅ RSA asymmetric encryption available")
    except ImportError as e:
        print(f"❌ RSA not available: {e}")
        return False
    
    print("✅ All cryptography dependencies are available!")
    return True

if __name__ == "__main__":
    test_dependencies() 