"""
Rolling Password Service
Provides encrypted password management with hourly updates
"""

import secrets
import hashlib
import hmac
import base64
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import structlog

logger = structlog.get_logger()

class RollingPasswordService:
    """
    Rolling Password Service for secure password management
    Provides hourly password updates with encryption
    """
    
    def __init__(self):
        self._master_key = Fernet.generate_key()
        self._cipher_suite = Fernet(self._master_key)
        self._password_tokens = {}
        self._password_history = {}
        self._encryption_salt = secrets.token_bytes(32)
        
    def _generate_secure_password(self, length: int = 16) -> str:
        """Generate a cryptographically secure password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def _hash_password(self, password: str, salt: bytes = None) -> Dict[str, Any]:
        """Hash password with salt using PBKDF2"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return {
            'hash': key,
            'salt': salt,
            'iterations': 100000
        }
    
    def _verify_password(self, password: str, stored_hash: bytes, salt: bytes) -> bool:
        """Verify password against stored hash"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return hmac.compare_digest(key, stored_hash)
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data using Fernet"""
        return self._cipher_suite.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet"""
        return self._cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def initialize_rolling_password(self, initial_password: str) -> Dict[str, Any]:
        """Initialize rolling password system with initial password"""
        try:
            # Generate token for this session
            token = secrets.token_urlsafe(32)
            
            # Hash the initial password
            hash_data = self._hash_password(initial_password)
            
            # Store password data
            self._password_tokens[token] = {
                'current_hash': hash_data['hash'],
                'salt': hash_data['salt'],
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(hours=1),
                'password_count': 1
            }
            
            # Encrypt sensitive data
            encrypted_hash = self._encrypt_data(hash_data['hash'].decode())
            
            logger.info(f"Rolling password initialized for token: {token[:8]}...")
            
            return {
                'status': 'success',
                'token': token,
                'expires_at': self._password_tokens[token]['expires_at'].isoformat(),
                'message': 'Rolling password system initialized'
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize rolling password: {e}")
            return {
                'status': 'error',
                'message': f'Failed to initialize rolling password: {str(e)}'
            }
    
    def validate_and_generate_new_password(self, current_password: str, token: str) -> Dict[str, Any]:
        """Validate current password and generate new one"""
        try:
            if token not in self._password_tokens:
                return {
                    'status': 'error',
                    'message': 'Invalid or expired token'
                }
            
            token_data = self._password_tokens[token]
            
            # Check if token is expired
            if datetime.now() > token_data['expires_at']:
                del self._password_tokens[token]
                return {
                    'status': 'error',
                    'message': 'Token expired'
                }
            
            # Verify current password
            if not self._verify_password(current_password, token_data['current_hash'], token_data['salt']):
                return {
                    'status': 'error',
                    'message': 'Invalid current password'
                }
            
            # Generate new password
            new_password = self._generate_secure_password(16)
            new_hash_data = self._hash_password(new_password)
            
            # Store password in history
            password_id = f"pwd_{token_data['password_count']}"
            self._password_history[password_id] = {
                'hash': token_data['current_hash'],
                'salt': token_data['salt'],
                'created_at': token_data['created_at'],
                'expires_at': token_data['expires_at']
            }
            
            # Update token data with new password
            token_data['current_hash'] = new_hash_data['hash']
            token_data['salt'] = new_hash_data['salt']
            token_data['created_at'] = datetime.now()
            token_data['expires_at'] = datetime.now() + timedelta(hours=1)
            token_data['password_count'] += 1
            
            logger.info(f"New password generated for token: {token[:8]}...")
            
            return {
                'status': 'success',
                'new_password': new_password,
                'expires_at': token_data['expires_at'].isoformat(),
                'password_count': token_data['password_count'],
                'message': 'Password validated and new password generated'
            }
            
        except Exception as e:
            logger.error(f"Failed to validate and generate new password: {e}")
            return {
                'status': 'error',
                'message': f'Failed to validate and generate new password: {str(e)}'
            }
    
    def get_password_status(self, token: str) -> Dict[str, Any]:
        """Get current password status"""
        try:
            if token not in self._password_tokens:
                return {
                    'status': 'error',
                    'message': 'Invalid token'
                }
            
            token_data = self._password_tokens[token]
            is_expired = datetime.now() > token_data['expires_at']
            
            return {
                'status': 'success',
                'is_expired': is_expired,
                'expires_at': token_data['expires_at'].isoformat(),
                'password_count': token_data['password_count'],
                'time_remaining': (token_data['expires_at'] - datetime.now()).total_seconds() if not is_expired else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get password status: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get password status: {str(e)}'
            }
    
    def reset_password_system(self, token: str) -> Dict[str, Any]:
        """Reset password system for a token"""
        try:
            if token in self._password_tokens:
                del self._password_tokens[token]
            
            # Clean up expired tokens
            current_time = datetime.now()
            expired_tokens = [
                token for token, data in self._password_tokens.items()
                if current_time > data['expires_at']
            ]
            
            for expired_token in expired_tokens:
                del self._password_tokens[expired_token]
            
            logger.info(f"Password system reset for token: {token[:8]}...")
            
            return {
                'status': 'success',
                'message': 'Password system reset successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to reset password system: {e}")
            return {
                'status': 'error',
                'message': f'Failed to reset password system: {str(e)}'
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get rolling password system statistics"""
        try:
            current_time = datetime.now()
            active_tokens = len([
                token for token, data in self._password_tokens.items()
                if current_time <= data['expires_at']
            ])
            
            total_passwords = sum(
                data['password_count'] for data in self._password_tokens.values()
            )
            
            return {
                'status': 'success',
                'active_tokens': active_tokens,
                'total_passwords_generated': total_passwords,
                'password_history_count': len(self._password_history),
                'system_uptime': 'active'
            }
            
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {
                'status': 'error',
                'message': f'Failed to get system stats: {str(e)}'
            }

# Global instance
rolling_password_service = RollingPasswordService() 