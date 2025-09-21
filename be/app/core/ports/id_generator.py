"""
Port interface for ID generation
"""
from abc import ABC, abstractmethod


class IdGenerator(ABC):
    """Abstract interface for ID generation"""
    
    @abstractmethod
    def generate(self) -> str:
        """Generate a new unique ID"""
        pass
    
    @abstractmethod
    def generate_uuid(self) -> str:
        """Generate a UUID"""
        pass
    
    @abstractmethod
    def generate_short_id(self) -> str:
        """Generate a short ID"""
        pass
