"""
Rolling Password Service
<<<<<<< HEAD
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
=======
Implements hourly rotating passwords for enhanced app security
"""

import asyncio
import hashlib
import secrets
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import text

from app.core.database import get_session
from app.core.config import settings

logger = structlog.get_logger()


class RollingPasswordService:
    """Service that manages hourly rotating passwords for app access"""
    
    def __init__(self):
        self.current_password_hash = None
        self.next_password_hash = None
        self.password_generation_time = None
        self.password_expiry_time = None
        self.user_sessions = {}  # Track user login sessions
        self.password_history = []  # Keep history for security analysis
        self.failed_attempts = {}  # Track failed login attempts
        
        # Password generation parameters
        self.password_length = 12
        self.password_complexity = {
            "uppercase": True,
            "lowercase": True,
            "digits": True,
            "special_chars": True
        }
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        self.password_rotation_interval = timedelta(hours=1)
        self.grace_period = timedelta(minutes=5)  # Grace period for password transition
        
        # Initialize the service lazily - will be called when first needed
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure the service is initialized before use"""
        if not self._initialized:
            await self._initialize_rolling_password_system()
            self._initialized = True
    
    async def _initialize_rolling_password_system(self):
        """Initialize the rolling password system"""
        try:
            logger.info("🔐 Initializing Rolling Password System")
            
            # Create database table if not exists
            await self._create_password_table()
            
            # Load existing password state or generate new
            await self._load_or_generate_initial_password()
            
            # Start password rotation scheduler
            await self._start_password_rotation_scheduler()
            
            logger.info("✅ Rolling Password System initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize rolling password system: {e}")
    
    async def _create_password_table(self):
        """Create database table for password management"""
        try:
            async with get_session() as session:
                # Create table for rolling passwords
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS rolling_passwords (
                        id SERIAL PRIMARY KEY,
                        password_hash VARCHAR(256) NOT NULL,
                        generation_time TIMESTAMP NOT NULL,
                        expiry_time TIMESTAMP NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Create table for user sessions
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(256) NOT NULL,
                        session_token VARCHAR(256) NOT NULL,
                        login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address VARCHAR(45),
                        password_used VARCHAR(256),
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """))
                
                # Create table for failed login attempts
                await session.execute(text("""
                    CREATE TABLE IF NOT EXISTS failed_login_attempts (
                        id SERIAL PRIMARY KEY,
                        user_identifier VARCHAR(256) NOT NULL,
                        attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address VARCHAR(45),
                        password_attempted VARCHAR(256)
                    )
                """))
                
                await session.commit()
                logger.info("✅ Rolling password database tables created")
        except Exception as e:
            logger.error(f"Failed to create password tables: {e}")
            raise
    
    async def _load_or_generate_initial_password(self):
        """Load existing password state or generate initial password"""
        try:
            async with get_session() as session:
                # Check for existing active password
                result = await session.execute(text("""
                    SELECT password_hash, generation_time, expiry_time 
                    FROM rolling_passwords 
                    WHERE is_active = TRUE 
                    ORDER BY generation_time DESC 
                    LIMIT 1
                """))
                existing_password = result.fetchone()
                
                if existing_password:
                    self.current_password_hash = existing_password[0]
                    self.password_generation_time = existing_password[1]
                    self.password_expiry_time = existing_password[2]
                    
                    # Check if password is still valid
                    if datetime.utcnow() > self.password_expiry_time:
                        logger.info("🔄 Existing password expired, generating new one")
                        await self._generate_new_password()
                    else:
                        logger.info("✅ Loaded existing active password")
                else:
                    # No existing password, generate initial one
                    await self._generate_new_password()
                    logger.info("🆕 Generated initial rolling password")
        except Exception as e:
            logger.error(f"Failed to load password state: {e}")
            await self._generate_new_password()
    
    async def _generate_new_password(self) -> str:
        """Generate a new secure password"""
        try:
            # Generate secure random password
            password = self._generate_secure_password()
            password_hash = self._hash_password(password)
            
            # Set timing
            generation_time = datetime.utcnow()
            expiry_time = generation_time + self.password_rotation_interval
            
            # Store in database
            async with get_session() as session:
                # Deactivate old passwords
                await session.execute(text("""
                    UPDATE rolling_passwords 
                    SET is_active = FALSE 
                    WHERE is_active = TRUE
                """))
                
                # Insert new password
                await session.execute(text("""
                    INSERT INTO rolling_passwords (password_hash, generation_time, expiry_time, is_active)
                    VALUES (:hash, :gen_time, :exp_time, TRUE)
                """), {
                    "hash": password_hash,
                    "gen_time": generation_time,
                    "exp_time": expiry_time
                })
                
                await session.commit()
            
            # Update instance variables
            self.current_password_hash = password_hash
            self.password_generation_time = generation_time
            self.password_expiry_time = expiry_time
            
            # Store plain text password for development/testing
            self._current_plain_password = password
            
            # Add to history
            self.password_history.append({
                "password_hash": password_hash,
                "generation_time": generation_time.isoformat(),
                "expiry_time": expiry_time.isoformat()
            })
            
            # Keep only last 24 hours of history
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.password_history = [
                p for p in self.password_history 
                if datetime.fromisoformat(p["generation_time"]) > cutoff_time
            ]
            
            logger.info(f"🔐 Generated new rolling password: {password}, expires at {expiry_time.isoformat()}")
            return password
        except Exception as e:
            logger.error(f"Failed to generate new password: {e}")
            raise

    def _generate_secure_password(self) -> str:
        """Generate a cryptographically secure password"""
        # Character sets
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        digits = "0123456789"
        special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Build character set based on complexity requirements
        chars = ""
        if self.password_complexity["uppercase"]:
            chars += uppercase
        if self.password_complexity["lowercase"]:
            chars += lowercase
        if self.password_complexity["digits"]:
            chars += digits
        if self.password_complexity["special_chars"]:
            chars += special
        
        # Ensure at least one character from each required set
        password = ""
        if self.password_complexity["uppercase"]:
            password += secrets.choice(uppercase)
        if self.password_complexity["lowercase"]:
            password += secrets.choice(lowercase)
        if self.password_complexity["digits"]:
            password += secrets.choice(digits)
        if self.password_complexity["special_chars"]:
            password += secrets.choice(special)
        
        # Fill remaining length with random characters
        remaining_length = self.password_length - len(password)
        password += ''.join(secrets.choice(chars) for _ in range(remaining_length))
        
        # Shuffle the password to avoid predictable patterns
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        password = ''.join(password_list)
        
        return password

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        return self._hash_password(password) == stored_hash
    
    async def _start_password_rotation_scheduler(self):
        """Start the password rotation scheduler"""
        async def rotation_loop():
            while True:
                try:
                    # Check if current password is about to expire
                    if self.password_expiry_time:
                        time_until_expiry = self.password_expiry_time - datetime.utcnow()
                        
                        if time_until_expiry <= timedelta(minutes=5):
                            # Generate new password 5 minutes before expiry
                            await self._generate_new_password()
                            
                            # Notify about password rotation
                            await self._notify_password_rotation()
                    
                    # Sleep for 1 minute before next check
                    await asyncio.sleep(60)
                except Exception as e:
                    logger.error(f"Password rotation scheduler error: {e}")
                    await asyncio.sleep(60)
        
        # Start the rotation loop
        asyncio.create_task(rotation_loop())
        logger.info("🔄 Password rotation scheduler started")
    
    async def _notify_password_rotation(self):
        """Notify system about password rotation"""
        try:
            logger.info("📢 Password rotation notification sent")
            # In production, this could send notifications to administrators
        except Exception as e:
            logger.error(f"Failed to send password rotation notification: {e}")
    
    async def authenticate_user(self, user_id: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """Authenticate user with current or previous password"""
        # Ensure service is initialized
        await self._ensure_initialized()
        
        try:
            logger.info(f"🔐 Authentication attempt for user: {user_id}")
            
            # Check for account lockout
            if await self._is_user_locked_out(user_id):
                return {
                    "success": False,
                    "error": "account_locked",
                    "message": "Account temporarily locked due to failed attempts",
                    "lockout_expires": await self._get_lockout_expiry(user_id)
                }
            
            # Verify password against current password
            password_valid = False
            password_used = None
            
            if self.current_password_hash and self._verify_password(password, self.current_password_hash):
                password_valid = True
                password_used = self.current_password_hash
            else:
                # Check previous passwords within grace period
                password_used = await self._check_previous_passwords(password)
                if password_used:
                    password_valid = True
                else:
                    # Check if this is a user's last known password (even if expired)
                    password_used = await self._check_user_last_password(user_id, password)
                    if password_used:
                        password_valid = True
                        logger.info(f"🔑 User {user_id} authenticated with last known password")
            
            if password_valid:
                # Successful authentication
                session_token = await self._create_user_session(user_id, password_used)
                
                # Clear failed attempts
                await self._clear_failed_attempts(user_id)
                
                # Get next password if user needs it
                next_password = await self._get_next_password_for_user(user_id)
                
                return {
                    "success": True,
                    "session_token": session_token,
                    "message": "Authentication successful",
                    "next_password": next_password,
                    "password_expires_at": self.password_expiry_time.isoformat() if self.password_expiry_time else None,
                    "time_until_expiry": str(self.password_expiry_time - datetime.utcnow()) if self.password_expiry_time else None
                }
            else:
                # Failed authentication
                await self._record_failed_attempt(user_id, password, ip_address)
                
                return {
                    "success": False,
                    "error": "invalid_password",
                    "message": "Invalid password",
                    "attempts_remaining": await self._get_attempts_remaining(user_id)
                }
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "success": False,
                "error": "system_error",
                "message": "Authentication system error"
            }
    
    async def _check_previous_passwords(self, password: str) -> Optional[str]:
        """Check password against recent passwords within grace period"""
        try:
            grace_cutoff = datetime.utcnow() - self.grace_period
            
            async with get_session() as session:
                result = await session.execute(text("""
                    SELECT password_hash FROM rolling_passwords 
                    WHERE generation_time > :cutoff 
                    ORDER BY generation_time DESC
                """), {"cutoff": grace_cutoff})
                
                for row in result:
                    if self._verify_password(password, row[0]):
                        return row[0]
                
                return None
        except Exception as e:
            logger.error(f"Failed to check previous passwords: {e}")
            return None
    
    async def _is_user_locked_out(self, user_id: str) -> bool:
        """Check if user is currently locked out"""
        try:
            lockout_cutoff = datetime.utcnow() - self.lockout_duration
            
            async with get_session() as session:
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM failed_login_attempts 
                    WHERE user_identifier = :user_id 
                    AND attempt_time > :cutoff
                """), {"user_id": user_id, "cutoff": lockout_cutoff})
                
                failed_count = result.scalar()
                return failed_count >= self.max_failed_attempts
        except Exception as e:
            logger.error(f"Failed to check lockout status: {e}")
            return False
    
    async def _get_lockout_expiry(self, user_id: str) -> Optional[str]:
        """Get lockout expiry time for user"""
        try:
            async with get_session() as session:
                result = await session.execute(text("""
                    SELECT MAX(attempt_time) FROM failed_login_attempts 
                    WHERE user_identifier = :user_id
                """), {"user_id": user_id})
                
                last_attempt = result.scalar()
                if last_attempt:
                    expiry = last_attempt + self.lockout_duration
                    return expiry.isoformat()
                return None
        except Exception as e:
            logger.error(f"Failed to get lockout expiry: {e}")
            return None
    
    async def _record_failed_attempt(self, user_id: str, password: str, ip_address: str = None):
        """Record failed login attempt"""
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()  # Store hash for analysis
            
            async with get_session() as session:
                await session.execute(text("""
                    INSERT INTO failed_login_attempts (user_identifier, attempt_time, ip_address, password_attempted)
                    VALUES (:user_id, :attempt_time, :ip_address, :password_hash)
                """), {
                    "user_id": user_id,
                    "attempt_time": datetime.utcnow(),
                    "ip_address": ip_address,
                    "password_hash": password_hash
                })
                await session.commit()
            
            logger.warning(f"🚨 Failed login attempt recorded for user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to record failed attempt: {e}")
    
    async def _clear_failed_attempts(self, user_id: str):
        """Clear failed attempts for user after successful login"""
        try:
            async with get_session() as session:
                await session.execute(text("""
                    DELETE FROM failed_login_attempts 
                    WHERE user_identifier = :user_id
                """), {"user_id": user_id})
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to clear failed attempts: {e}")
    
    async def _get_attempts_remaining(self, user_id: str) -> int:
        """Get remaining login attempts before lockout"""
        try:
            lockout_cutoff = datetime.utcnow() - self.lockout_duration
            
            async with get_session() as session:
                result = await session.execute(text("""
                    SELECT COUNT(*) FROM failed_login_attempts 
                    WHERE user_identifier = :user_id 
                    AND attempt_time > :cutoff
                """), {"user_id": user_id, "cutoff": lockout_cutoff})
                
                failed_count = result.scalar()
                return max(0, self.max_failed_attempts - failed_count)
        except Exception as e:
            logger.error(f"Failed to get attempts remaining: {e}")
            return 0
    
    async def _create_user_session(self, user_id: str, password_used: str) -> str:
        """Create new user session"""
        try:
            session_token = secrets.token_urlsafe(32)
            
            async with get_session() as session:
                await session.execute(text("""
                    INSERT INTO user_sessions (user_id, session_token, password_used, login_time, last_activity)
                    VALUES (:user_id, :session_token, :password_used, :login_time, :last_activity)
                """), {
                    "user_id": user_id,
                    "session_token": session_token,
                    "password_used": password_used,
                    "login_time": datetime.utcnow(),
                    "last_activity": datetime.utcnow()
                })
                await session.commit()
            
            # Store in memory for quick access
            self.user_sessions[session_token] = {
                "user_id": user_id,
                "login_time": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            logger.info(f"✅ Created session for user: {user_id}")
            return session_token
        except Exception as e:
            logger.error(f"Failed to create user session: {e}")
            raise
    
    async def _get_next_password_for_user(self, user_id: str) -> Optional[str]:
        """Get next password for authenticated user"""
        try:
            # Only generate next password after successful login
            # This ensures security - no automatic password generation
            next_password = self._generate_secure_password()
            logger.info(f"🔑 Generated next password for user: {user_id} after successful login")
            return next_password
        except Exception as e:
            logger.error(f"Failed to get next password: {e}")
            return None
    
    async def get_current_password_info(self) -> Dict[str, Any]:
        """Get information about current password (for admin use)"""
        # Ensure service is initialized
        await self._ensure_initialized()
        
        try:
            return {
                "has_active_password": self.current_password_hash is not None,
                "generation_time": self.password_generation_time.isoformat() if self.password_generation_time else None,
                "expiry_time": self.password_expiry_time.isoformat() if self.password_expiry_time else None,
                "time_until_expiry": str(self.password_expiry_time - datetime.utcnow()) if self.password_expiry_time else None,
                "password_history_count": len(self.password_history),
                "active_sessions": len(self.user_sessions),
                "rotation_interval_hours": self.password_rotation_interval.total_seconds() / 3600,
                "grace_period_minutes": self.grace_period.total_seconds() / 60
            }
        except Exception as e:
            logger.error(f"Failed to get password info: {e}")
            return {"error": str(e)}
    
    async def get_security_analytics(self) -> Dict[str, Any]:
        """Get security analytics for the rolling password system"""
        # Ensure service is initialized
        await self._ensure_initialized()
        
        try:
            async with get_session() as session:
                # Get failed attempt statistics
                failed_attempts_result = await session.execute(text("""
                    SELECT COUNT(*), COUNT(DISTINCT user_identifier) 
                    FROM failed_login_attempts 
                    WHERE attempt_time > :cutoff
                """), {"cutoff": datetime.utcnow() - timedelta(hours=24)})
                failed_stats = failed_attempts_result.fetchone()
                
                # Get successful login statistics
                successful_logins_result = await session.execute(text("""
                    SELECT COUNT(*), COUNT(DISTINCT user_id) 
                    FROM user_sessions 
                    WHERE login_time > :cutoff
                """), {"cutoff": datetime.utcnow() - timedelta(hours=24)})
                success_stats = successful_logins_result.fetchone()
                
                return {
                    "last_24_hours": {
                        "failed_attempts": failed_stats[0] if failed_stats else 0,
                        "unique_users_failed": failed_stats[1] if failed_stats else 0,
                        "successful_logins": success_stats[0] if success_stats else 0,
                        "unique_users_success": success_stats[1] if success_stats else 0
                    },
                    "password_rotations": len(self.password_history),
                    "current_active_sessions": len(self.user_sessions),
                    "security_status": "secure" if (failed_stats[0] if failed_stats else 0) < 10 else "elevated_risk",
                    "system_health": "operational"
                }
        except Exception as e:
            logger.error(f"Failed to get security analytics: {e}")
            return {"error": str(e)}
    
    async def force_password_rotation(self) -> Dict[str, Any]:
        """Force immediate password rotation (admin function)"""
        try:
            logger.info("🔄 Forcing immediate password rotation")
            new_password = await self._generate_new_password()
            
            # Invalidate all existing sessions
            await self._invalidate_all_sessions()
            
            return {
                "success": True,
                "message": "Password rotation completed",
                "new_password_generated": True,
                "all_sessions_invalidated": True,
                "new_expiry_time": self.password_expiry_time.isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to force password rotation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _invalidate_all_sessions(self):
        """Invalidate all active user sessions"""
        try:
            async with get_session() as session:
                await session.execute(text("""
                    UPDATE user_sessions 
                    SET is_active = FALSE 
                    WHERE is_active = TRUE
                """))
                await session.commit()
            
            # Clear memory sessions
            self.user_sessions.clear()
            
            logger.info("🚫 All user sessions invalidated")
        except Exception as e:
            logger.error(f"Failed to invalidate sessions: {e}")

    async def get_current_plain_password(self) -> Optional[str]:
        """Get current password in plain text (for development/testing only)"""
        # Ensure service is initialized
        await self._ensure_initialized()
        
        if hasattr(self, '_current_plain_password') and self._current_plain_password:
            return self._current_plain_password
        return None

    async def _check_user_last_password(self, user_id: str, password: str) -> Optional[str]:
        """Check if password matches user's last known password from session history"""
        try:
            async with get_session() as session:
                # Get user's last successful login password
                result = await session.execute(text("""
                    SELECT password_used FROM user_sessions 
                    WHERE user_id = :user_id 
                    ORDER BY login_time DESC 
                    LIMIT 1
                """), {"user_id": user_id})
                
                last_password_hash = result.scalar()
                if last_password_hash and self._verify_password(password, last_password_hash):
                    return last_password_hash
                
                return None
        except Exception as e:
            logger.error(f"Failed to check user last password: {e}")
            return None


# Global instance
rolling_password_service = RollingPasswordService()
>>>>>>> c98fd28782c60b4bf527a7cf8255f563dabe32e2
