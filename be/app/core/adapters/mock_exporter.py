"""
Mock implementation of Exporter for testing
"""
from typing import List, Dict, Any
import json
import yaml

from ..domain.env_var import EnvVar
from ..ports.exporter import Exporter


class MockExporter(Exporter):
    """Mock implementation of Exporter for testing"""
    
    async def export_to_k8s_secret(self, env_vars: List[EnvVar], secret_name: str) -> str:
        """Export environment variables to Kubernetes Secret YAML"""
        data = {}
        for env_var in env_vars:
            # In real implementation, you'd need to decrypt secrets
            data[env_var.key] = env_var.get_masked_value()
        
        secret = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': secret_name,
                'namespace': 'default'
            },
            'type': 'Opaque',
            'data': data
        }
        
        return yaml.dump(secret, default_flow_style=False)
    
    async def export_to_k8s_configmap(self, env_vars: List[EnvVar], configmap_name: str) -> str:
        """Export environment variables to Kubernetes ConfigMap YAML"""
        data = {}
        for env_var in env_vars:
            # Only non-secret variables go to ConfigMap
            if not env_var.is_secret:
                data[env_var.key] = env_var.value
        
        configmap = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': configmap_name,
                'namespace': 'default'
            },
            'data': data
        }
        
        return yaml.dump(configmap, default_flow_style=False)
    
    async def export_to_dotenv(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to .env format"""
        lines = []
        for env_var in env_vars:
            # In real implementation, you'd need to decrypt secrets
            value = env_var.get_masked_value()
            lines.append(f"{env_var.key}={value}")
        
        return "\n".join(lines)
    
    async def export_to_json(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to JSON format"""
        data = {}
        for env_var in env_vars:
            # In real implementation, you'd need to decrypt secrets
            data[env_var.key] = env_var.get_masked_value()
        
        return json.dumps(data, indent=2)
    
    async def export_to_yaml(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to YAML format"""
        data = {}
        for env_var in env_vars:
            # In real implementation, you'd need to decrypt secrets
            data[env_var.key] = env_var.get_masked_value()
        
        return yaml.dump(data, default_flow_style=False)
    
    async def parse_dotenv(self, content: str) -> Dict[str, str]:
        """Parse .env content and return key-value pairs"""
        result = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    result[key.strip()] = value.strip()
        return result
    
    async def parse_json(self, content: str) -> Dict[str, str]:
        """Parse JSON content and return key-value pairs"""
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
            else:
                raise ValueError("JSON content must be an object")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    async def parse_yaml(self, content: str) -> Dict[str, str]:
        """Parse YAML content and return key-value pairs"""
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
            else:
                raise ValueError("YAML content must be an object")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
