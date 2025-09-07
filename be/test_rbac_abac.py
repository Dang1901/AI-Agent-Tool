#!/usr/bin/env python3
"""
Test script for RBAC and ABAC system
Run this after initializing the database
"""

import requests
import json
import os
from typing import Dict, Any

# Get port from environment or default to 8000
PORT = os.getenv("PORT", "8000")
BASE_URL = f"http://localhost:{PORT}"

def test_api_endpoint(method: str, endpoint: str, data: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
    """Test API endpoint and return response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"{method} {endpoint} -> {response.status_code}")
        
        if response.status_code >= 400:
            print(f"Error: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
        
        return response.json() if response.content else {"status": "success"}
    
    except Exception as e:
        print(f"Exception: {e}")
        return {"error": str(e)}

def test_rbac_system():
    """Test RBAC system"""
    print("=== Testing RBAC System ===")
    
    # Test roles
    print("\n1. Testing Roles...")
    roles = test_api_endpoint("GET", "/rbac/roles")
    print(f"Found {len(roles)} roles")
    
    # Test permissions
    print("\n2. Testing Permissions...")
    permissions = test_api_endpoint("GET", "/rbac/permissions")
    print(f"Found {len(permissions)} permissions")
    
    # Test resources
    print("\n3. Testing Resources...")
    resources = test_api_endpoint("GET", "/rbac/resources")
    print(f"Found {len(resources)} resources")
    
    # Test role permissions
    if roles and len(roles) > 0:
        role_id = roles[0]["id"]
        print(f"\n4. Testing Role Permissions for role {role_id}...")
        role_permissions = test_api_endpoint("GET", f"/rbac/roles/{role_id}/permissions")
        print(f"Role {role_id} has {len(role_permissions)} permissions")

def test_abac_system():
    """Test ABAC system"""
    print("\n=== Testing ABAC System ===")
    
    # Test policies
    print("\n1. Testing Policies...")
    policies = test_api_endpoint("GET", "/abac/policies")
    print(f"Found {len(policies)} policies")
    
    # Test attributes
    print("\n2. Testing Attributes...")
    attributes = test_api_endpoint("GET", "/abac/attributes")
    print(f"Found {len(attributes)} attributes")
    
    # Test authorization
    print("\n3. Testing Authorization...")
    auth_request = {
        "user_id": 1,
        "resource_type": "user",
        "action": "read",
        "context": {
            "user.department": "IT",
            "user.clearance_level": "internal",
            "resource.sensitivity": "internal"
        }
    }
    
    auth_response = test_api_endpoint("POST", "/abac/authorize", auth_request)
    print(f"Authorization result: {auth_response}")

def test_auth_system():
    """Test authentication system"""
    print("\n=== Testing Authentication System ===")
    
    # Test login (using hardcoded credentials)
    print("\n1. Testing Login...")
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    login_response = test_api_endpoint("POST", "/auth/login", login_data)
    if "access_token" in login_response:
        print("Login successful!")
        token = login_response["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test protected endpoint
        print("\n2. Testing Protected Endpoint...")
        me_response = test_api_endpoint("GET", "/auth/me", headers=headers)
        print(f"User info: {me_response}")
        
        return headers
    else:
        print("Login failed!")
        return None

def main():
    """Main test function"""
    print("Starting RBAC/ABAC System Tests...")
    print("=" * 50)
    
    # Test authentication
    headers = test_auth_system()
    
    # Test RBAC system
    test_rbac_system()
    
    # Test ABAC system
    test_abac_system()
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == "__main__":
    main()
