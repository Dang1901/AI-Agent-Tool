"""
Port interface for secret encryption/decryption
"""
from abc import ABC, abstractmethod
from typing import Optional


class SecretCipher(ABC):
    """Abstract interface for secret encryption/decryption"""
    
    @abstractmethod
    async def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext and return encrypted string"""
        pass
    
    @abstractmethod
    async def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext and return plaintext"""
        pass
    
    @abstractmethod
    async def rotate_key(self) -> bool:
        """Rotate encryption key"""
        pass
    
    @abstractmethod
    async def get_key_info(self) -> dict:
        """Get information about current encryption key"""
        pass
