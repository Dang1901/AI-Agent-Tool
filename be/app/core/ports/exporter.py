"""
Port interface for exporting environment variables
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..domain.env_var import EnvVar


class Exporter(ABC):
    """Abstract interface for exporting environment variables"""
    
    @abstractmethod
    async def export_to_k8s_secret(self, env_vars: List[EnvVar], secret_name: str) -> str:
        """Export environment variables to Kubernetes Secret YAML"""
        pass
    
    @abstractmethod
    async def export_to_k8s_configmap(self, env_vars: List[EnvVar], configmap_name: str) -> str:
        """Export environment variables to Kubernetes ConfigMap YAML"""
        pass
    
    @abstractmethod
    async def export_to_dotenv(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to .env format"""
        pass
    
    @abstractmethod
    async def export_to_json(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to JSON format"""
        pass
    
    @abstractmethod
    async def export_to_yaml(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to YAML format"""
        pass
    
    @abstractmethod
    async def parse_dotenv(self, content: str) -> Dict[str, str]:
        """Parse .env content and return key-value pairs"""
        pass
    
    @abstractmethod
    async def parse_json(self, content: str) -> Dict[str, str]:
        """Parse JSON content and return key-value pairs"""
        pass
    
    @abstractmethod
    async def parse_yaml(self, content: str) -> Dict[str, str]:
        """Parse YAML content and return key-value pairs"""
        pass
