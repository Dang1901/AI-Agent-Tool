"""
Mock implementation of Clock for testing
"""
from datetime import datetime
from typing import Optional

from ..ports.clock import Clock


class MockClock(Clock):
    """Mock implementation of Clock for testing"""
    
    def __init__(self, fixed_time: Optional[datetime] = None):
        self.fixed_time = fixed_time
        self.time_offset = 0
    
    def now(self) -> datetime:
        """Get current datetime"""
        if self.fixed_time:
            return self.fixed_time
        return datetime.now()
    
    def utcnow(self) -> datetime:
        """Get current UTC datetime"""
        if self.fixed_time:
            return self.fixed_time
        return datetime.utcnow()
    
    def timestamp(self) -> float:
        """Get current timestamp"""
        if self.fixed_time:
            return self.fixed_time.timestamp()
        return datetime.now().timestamp()
    
    def set_fixed_time(self, fixed_time: datetime):
        """Set a fixed time for testing"""
        self.fixed_time = fixed_time
    
    def advance_time(self, seconds: int):
        """Advance time by specified seconds (for testing)"""
        if self.fixed_time:
            self.fixed_time = datetime.fromtimestamp(self.fixed_time.timestamp() + seconds)
        else:
            self.time_offset += seconds
    
    def reset(self):
        """Reset clock to current time"""
        self.fixed_time = None
        self.time_offset = 0
