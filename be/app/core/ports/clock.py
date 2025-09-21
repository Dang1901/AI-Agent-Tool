"""
Port interface for time operations
"""
from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Abstract interface for time operations"""
    
    @abstractmethod
    def now(self) -> datetime:
        """Get current datetime"""
        pass
    
    @abstractmethod
    def utcnow(self) -> datetime:
        """Get current UTC datetime"""
        pass
    
    @abstractmethod
    def timestamp(self) -> float:
        """Get current timestamp"""
        pass
