"""
Mock implementation of SecretCipher for testing
"""
import base64
from typing import Dict, Any

from ..ports.secret_cipher import SecretCipher


class MockSecretCipher(SecretCipher):
    """Mock implementation of SecretCipher for testing"""
    
    def __init__(self):
        self.key_info = {
            'key_id': 'mock-key-1',
            'algorithm': 'AES-256-GCM',
            'created_at': '2024-01-01T00:00:00Z'
        }
    
    async def encrypt(self, plaintext: str) -> str:
        """Mock encryption - just base64 encode for testing"""
        # In real implementation, this would use proper encryption
        encoded = base64.b64encode(plaintext.encode('utf-8')).decode('utf-8')
        return f"encrypted:{encoded}"
    
    async def decrypt(self, ciphertext: str) -> str:
        """Mock decryption - just base64 decode for testing"""
        # In real implementation, this would use proper decryption
        if not ciphertext.startswith("encrypted:"):
            raise ValueError("Invalid ciphertext format")
        
        encoded = ciphertext[10:]  # Remove "encrypted:" prefix
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            return decoded
        except Exception as e:
            raise ValueError(f"Failed to decrypt: {e}")
    
    async def rotate_key(self) -> bool:
        """Mock key rotation"""
        # In real implementation, this would rotate the encryption key
        self.key_info['key_id'] = f"mock-key-{int(self.key_info['key_id'].split('-')[-1]) + 1}"
        return True
    
    async def get_key_info(self) -> Dict[str, Any]:
        """Get information about current encryption key"""
        return self.key_info.copy()
