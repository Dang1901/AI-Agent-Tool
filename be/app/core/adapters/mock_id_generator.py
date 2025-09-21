"""
Mock implementation of IdGenerator for testing
"""
import uuid
from typing import Set

from ..ports.id_generator import IdGenerator


class MockIdGenerator(IdGenerator):
    """Mock implementation of IdGenerator for testing"""
    
    def __init__(self):
        self.generated_ids: Set[str] = set()
        self.id_counter = 0
    
    def generate(self) -> str:
        """Generate a new unique ID"""
        self.id_counter += 1
        id_str = f"mock-id-{self.id_counter}"
        self.generated_ids.add(id_str)
        return id_str
    
    def generate_uuid(self) -> str:
        """Generate a UUID v4"""
        id_str = str(uuid.uuid4())
        self.generated_ids.add(id_str)
        return id_str
    
    def generate_uuid_v7(self) -> str:
        """Generate a UUID v7 (time-based)"""
        # UUID v7 implementation using time-based approach
        import time
        import random
        
        # Get current timestamp in milliseconds
        timestamp_ms = int(time.time() * 1000)
        
        # Generate random data for the remaining bits
        random_data = random.getrandbits(48)
        
        # Create UUID v7 format: timestamp (48 bits) + random (48 bits)
        # This is a simplified implementation - in production use a proper UUID v7 library
        id_str = f"{timestamp_ms:012x}{random_data:012x}"
        
        # Ensure we have enough characters for UUID format
        if len(id_str) < 32:
            id_str = id_str.ljust(32, '0')
        
        # Format as UUID string (8-4-4-4-12)
        formatted_uuid = f"{id_str[:8]}-{id_str[8:12]}-7{id_str[13:16]}-{id_str[16:20]}-{id_str[20:32]}"
        
        self.generated_ids.add(formatted_uuid)
        return formatted_uuid
    
    def generate_short_id(self) -> str:
        """Generate a short ID"""
        self.id_counter += 1
        id_str = f"short-{self.id_counter}"
        self.generated_ids.add(id_str)
        return id_str
    
    def get_generated_ids(self) -> Set[str]:
        """Get all generated IDs (for testing)"""
        return self.generated_ids.copy()
    
    def reset(self):
        """Reset generator (for testing)"""
        self.generated_ids.clear()
        self.id_counter = 0
