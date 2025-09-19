import os
import base64
import hashlib
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class EncryptionService:
    """
    Handles all encryption/decryption operations for sensitive tourist data
    Uses AES encryption via Fernet (authenticated encryption)
    """
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.fernet = Fernet(self.encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """
        Get or generate the encryption key
        In production, this should be securely managed (e.g., AWS KMS, Azure Key Vault)
        """
        key_b64 = os.environ.get("ENCRYPTION_KEY_BASE64")
        
        if key_b64:
            try:
                return base64.urlsafe_b64decode(key_b64)
            except Exception as e:
                logger.warning(f"Invalid encryption key in environment: {e}")
        
        # Generate a new key (for development only)
        key = Fernet.generate_key()
        logger.warning(f"Generated new encryption key: {base64.urlsafe_b64encode(key).decode()}")
        logger.warning("SECURITY WARNING: Store this key securely and add it to your .env file!")
        return key
    
    def encrypt_data(self, data: Dict[Any, Any]) -> str:
        """
        Encrypt a dictionary of data
        Returns base64 encoded encrypted string
        """
        try:
            # Convert data to JSON string
            json_data = json.dumps(data, default=str, sort_keys=True)
            
            # Encrypt the JSON string
            encrypted_bytes = self.fernet.encrypt(json_data.encode('utf-8'))
            
            # Return base64 encoded encrypted data
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise ValueError("Failed to encrypt data")
    
    def decrypt_data(self, encrypted_data: str) -> Dict[Any, Any]:
        """
        Decrypt base64 encoded encrypted string back to dictionary
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt to JSON string
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            json_data = decrypted_bytes.decode('utf-8')
            
            # Parse JSON back to dictionary
            return json.loads(json_data)
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise ValueError("Failed to decrypt data")
    
    def generate_hash(self, data: str) -> str:
        """
        Generate SHA-256 hash of data for integrity verification
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def verify_data_integrity(self, data: str, expected_hash: str) -> bool:
        """
        Verify data integrity by comparing hashes
        """
        actual_hash = self.generate_hash(data)
        return actual_hash == expected_hash

# Global encryption service instance
encryption_service = EncryptionService()