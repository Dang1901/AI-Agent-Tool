"""
Real implementation of Exporter for Kubernetes YAML
"""
from typing import List, Dict, Any
import yaml
import json
import re

from app.core.domain.env_var import EnvVar
from app.core.ports.exporter import Exporter


class K8sYamlExporter(Exporter):
    """Real implementation of Exporter for Kubernetes YAML"""
    
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
    
    async def export_to_k8s_secret(self, env_vars: List[EnvVar], secret_name: str) -> str:
        """Export environment variables to Kubernetes Secret YAML"""
        # Filter only secret variables
        secret_vars = [var for var in env_vars if var.is_secret]
        
        if not secret_vars:
            return self._create_empty_secret_yaml(secret_name)
        
        # Create data section with base64 encoded values
        data = {}
        for env_var in secret_vars:
            # In real implementation, you'd need to decrypt the value
            # For now, we'll use the encrypted value as-is
            import base64
            encoded_value = base64.b64encode(env_var.value.encode('utf-8')).decode('utf-8')
            data[env_var.key] = encoded_value
        
        secret = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': secret_name,
                'namespace': self.namespace,
                'labels': {
                    'app.kubernetes.io/name': 'env-vars',
                    'app.kubernetes.io/component': 'secrets'
                }
            },
            'type': 'Opaque',
            'data': data
        }
        
        return yaml.dump(secret, default_flow_style=False, sort_keys=False)
    
    async def export_to_k8s_configmap(self, env_vars: List[EnvVar], configmap_name: str) -> str:
        """Export environment variables to Kubernetes ConfigMap YAML"""
        # Filter only non-secret variables
        config_vars = [var for var in env_vars if not var.is_secret]
        
        if not config_vars:
            return self._create_empty_configmap_yaml(configmap_name)
        
        # Create data section
        data = {}
        for env_var in config_vars:
            data[env_var.key] = env_var.value
        
        configmap = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': configmap_name,
                'namespace': self.namespace,
                'labels': {
                    'app.kubernetes.io/name': 'env-vars',
                    'app.kubernetes.io/component': 'configmap'
                }
            },
            'data': data
        }
        
        return yaml.dump(configmap, default_flow_style=False, sort_keys=False)
    
    async def export_to_dotenv(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to .env format"""
        lines = []
        
        # Add header comment
        lines.append("# Environment variables exported from EnvVar Manager")
        lines.append(f"# Generated at: {self._get_current_timestamp()}")
        lines.append("")
        
        # Group by scope
        scopes = {}
        for env_var in env_vars:
            scope_key = f"{env_var.scope.level.value}:{env_var.scope.ref_id}"
            if scope_key not in scopes:
                scopes[scope_key] = []
            scopes[scope_key].append(env_var)
        
        # Export each scope
        for scope_key, scope_vars in scopes.items():
            lines.append(f"# Scope: {scope_key}")
            for env_var in scope_vars:
                # Escape value if it contains special characters
                value = self._escape_env_value(env_var.value)
                lines.append(f"{env_var.key}={value}")
            lines.append("")
        
        return "\n".join(lines)
    
    async def export_to_json(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to JSON format"""
        data = {
            'metadata': {
                'exported_at': self._get_current_timestamp(),
                'count': len(env_vars),
                'scopes': list(set(f"{var.scope.level.value}:{var.scope.ref_id}" for var in env_vars))
            },
            'environment_variables': []
        }
        
        for env_var in env_vars:
            var_data = {
                'key': env_var.key,
                'value': env_var.get_masked_value(),  # Mask secrets
                'type': env_var.type.value,
                'scope': {
                    'level': env_var.scope.level.value,
                    'ref_id': env_var.scope.ref_id
                },
                'tags': env_var.tags,
                'description': env_var.description,
                'is_secret': env_var.is_secret,
                'status': env_var.status.value,
                'created_by': env_var.created_by,
                'created_at': env_var.created_at.isoformat(),
                'updated_by': env_var.updated_by,
                'updated_at': env_var.updated_at.isoformat()
            }
            data['environment_variables'].append(var_data)
        
        return json.dumps(data, indent=2, default=str)
    
    async def export_to_yaml(self, env_vars: List[EnvVar]) -> str:
        """Export environment variables to YAML format"""
        data = {
            'metadata': {
                'exported_at': self._get_current_timestamp(),
                'count': len(env_vars),
                'scopes': list(set(f"{var.scope.level.value}:{var.scope.ref_id}" for var in env_vars))
            },
            'environment_variables': []
        }
        
        for env_var in env_vars:
            var_data = {
                'key': env_var.key,
                'value': env_var.get_masked_value(),  # Mask secrets
                'type': env_var.type.value,
                'scope': {
                    'level': env_var.scope.level.value,
                    'ref_id': env_var.scope.ref_id
                },
                'tags': env_var.tags,
                'description': env_var.description,
                'is_secret': env_var.is_secret,
                'status': env_var.status.value,
                'created_by': env_var.created_by,
                'created_at': env_var.created_at.isoformat(),
                'updated_by': env_var.updated_by,
                'updated_at': env_var.updated_at.isoformat()
            }
            data['environment_variables'].append(var_data)
        
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    
    async def parse_dotenv(self, content: str) -> Dict[str, str]:
        """Parse .env content and return key-value pairs"""
        result = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse key=value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                result[key] = value
        
        return result
    
    async def parse_json(self, content: str) -> Dict[str, str]:
        """Parse JSON content and return key-value pairs"""
        try:
            data = json.loads(content)
            
            if isinstance(data, dict):
                # Handle nested structure
                if 'environment_variables' in data:
                    result = {}
                    for var in data['environment_variables']:
                        if 'key' in var and 'value' in var:
                            result[var['key']] = var['value']
                    return result
                else:
                    # Flat structure
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
                # Handle nested structure
                if 'environment_variables' in data:
                    result = {}
                    for var in data['environment_variables']:
                        if 'key' in var and 'value' in var:
                            result[var['key']] = var['value']
                    return result
                else:
                    # Flat structure
                    return {str(k): str(v) for k, v in data.items()}
            else:
                raise ValueError("YAML content must be an object")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")
    
    def _create_empty_secret_yaml(self, secret_name: str) -> str:
        """Create empty secret YAML"""
        secret = {
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': secret_name,
                'namespace': self.namespace,
                'labels': {
                    'app.kubernetes.io/name': 'env-vars',
                    'app.kubernetes.io/component': 'secrets'
                }
            },
            'type': 'Opaque',
            'data': {}
        }
        
        return yaml.dump(secret, default_flow_style=False, sort_keys=False)
    
    def _create_empty_configmap_yaml(self, configmap_name: str) -> str:
        """Create empty configmap YAML"""
        configmap = {
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': configmap_name,
                'namespace': self.namespace,
                'labels': {
                    'app.kubernetes.io/name': 'env-vars',
                    'app.kubernetes.io/component': 'configmap'
                }
            },
            'data': {}
        }
        
        return yaml.dump(configmap, default_flow_style=False, sort_keys=False)
    
    def _escape_env_value(self, value: str) -> str:
        """Escape environment variable value for .env format"""
        # Escape backslashes and quotes
        value = value.replace('\\', '\\\\')
        value = value.replace('"', '\\"')
        
        # Wrap in quotes if value contains spaces or special characters
        if ' ' in value or any(char in value for char in ['$', '`', '!', '&', '|', ';', '(', ')', '<', '>']):
            value = f'"{value}"'
        
        return value
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.now().isoformat()
