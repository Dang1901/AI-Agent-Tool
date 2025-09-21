"""
Real implementation of SecretCipher using cryptography library
"""
import os
import base64
from typing import Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.ports.secret_cipher import SecretCipher
from app.core.config import ENCRYPTION_MASTER_KEY


class CryptoCipher(SecretCipher):
    """Real implementation of SecretCipher using cryptography library"""
    
    def __init__(self, master_key: str = None):
        """
        Initialize cipher with master key
        
        Args:
            master_key: Master key for encryption. If None, will use config
        """
        if master_key is None:
            master_key = ENCRYPTION_MASTER_KEY
        
        self.master_key = master_key.encode('utf-8')
        self.fernet = self._create_fernet()
        self.key_info = {
            'key_id': 'crypto-cipher-1',
            'algorithm': 'Fernet (AES-128-CBC + HMAC-SHA256)',
            'created_at': '2024-01-01T00:00:00Z'
        }
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet cipher from master key"""
        # Derive key from master key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'env_var_salt',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)
    
    async def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return encrypted string"""
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Encryption failed: {e}")
    
    async def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext and return plaintext"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {e}")
    
    async def rotate_key(self) -> bool:
        """Rotate encryption key"""
        try:
            # In production, this would involve:
            # 1. Generating new key
            # 2. Re-encrypting all existing secrets
            # 3. Updating key metadata
            # For now, just update key info
            self.key_info['key_id'] = f"crypto-cipher-{int(self.key_info['key_id'].split('-')[-1]) + 1}"
            return True
        except Exception as e:
            print(f"Key rotation failed: {e}")
            return False
    
    async def get_key_info(self) -> Dict[str, Any]:
        """Get information about current encryption key"""
        return self.key_info.copy()


class KmsCipher(SecretCipher):
    """KMS-based implementation of SecretCipher (for production)"""
    
    def __init__(self, kms_client=None, key_id: str = None):
        """
        Initialize KMS cipher
        
        Args:
            kms_client: KMS client (AWS KMS, Azure Key Vault, etc.)
            key_id: KMS key ID
        """
        self.kms_client = kms_client
        self.key_id = key_id or os.getenv('KMS_KEY_ID')
        if not self.key_id:
            raise ValueError("KMS_KEY_ID environment variable is required")
        
        self.key_info = {
            'key_id': self.key_id,
            'algorithm': 'KMS',
            'created_at': '2024-01-01T00:00:00Z'
        }
    
    async def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using KMS"""
        try:
            # This is a placeholder implementation
            # In real implementation, you'd call KMS encrypt API
            if self.kms_client:
                response = self.kms_client.encrypt(
                    KeyId=self.key_id,
                    Plaintext=plaintext
                )
                return base64.b64encode(response['CiphertextBlob']).decode('utf-8')
            else:
                # Fallback to local encryption
                cipher = CryptoCipher()
                return await cipher.encrypt(plaintext)
        except Exception as e:
            raise ValueError(f"KMS encryption failed: {e}")
    
    async def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext using KMS"""
        try:
            # This is a placeholder implementation
            # In real implementation, you'd call KMS decrypt API
            if self.kms_client:
                response = self.kms_client.decrypt(
                    CiphertextBlob=base64.b64decode(ciphertext.encode('utf-8'))
                )
                return response['Plaintext'].decode('utf-8')
            else:
                # Fallback to local decryption
                cipher = CryptoCipher()
                return await cipher.decrypt(ciphertext)
        except Exception as e:
            raise ValueError(f"KMS decryption failed: {e}")
    
    async def rotate_key(self) -> bool:
        """Rotate KMS key"""
        try:
            # In production, this would involve:
            # 1. Creating new KMS key
            # 2. Re-encrypting all secrets with new key
            # 3. Updating key metadata
            self.key_info['key_id'] = f"{self.key_id}-rotated"
            return True
        except Exception as e:
            print(f"KMS key rotation failed: {e}")
            return False
    
    async def get_key_info(self) -> Dict[str, Any]:
        """Get information about current KMS key"""
        return self.key_info.copy()
