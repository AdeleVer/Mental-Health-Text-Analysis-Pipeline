"""
Proper API integration tests with safe test data.
Tests authentication and protected endpoints.
"""

import pytest
import json
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app import app, db
from src.models.sql_models import User


class TestAPI:
    """API endpoint tests with proper setup and teardown"""
    
    def setup_method(self):
        """Setup before each test method"""
        # Configure test environment
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        self.client = app.test_client()
        
        # Create application context and database
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user with safe credentials
        self.test_user = User(
            username="test_user_001",
            email="test@example.com"
        )
        self.test_user.set_password("safe_test_password_123")
        db.session.add(self.test_user)
        db.session.commit()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post('/api/auth/register', json={
            'username': 'new_test_user',
            'email': 'newuser@example.com',
            'password': 'new_secure_password_456'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data
        assert data['user']['username'] == 'new_test_user'
        print("✅ User registration test passed")
    
    def test_successful_login(self):
        """Test successful user login"""
        response = self.client.post('/api/auth/login', json={
            'username': 'test_user_001',
            'password': 'safe_test_password_123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert data['user']['username'] == 'test_user_001'
        print("✅ Successful login test passed")
    
    def test_failed_login_wrong_password(self):
        """Test login with incorrect password"""
        response = self.client.post('/api/auth/login', json={
            'username': 'test_user_001',
            'password': 'wrong_password'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        print("✅ Failed login (wrong password) test passed")
    
    def test_failed_login_wrong_username(self):
        """Test login with non-existent username"""
        response = self.client.post('/api/auth/login', json={
            'username': 'non_existent_user',
            'password': 'any_password'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        print("✅ Failed login (wrong username) test passed")
    
    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid JWT token"""
        # First, login to get token
        login_response = self.client.post('/api/auth/login', json={
            'username': 'test_user_001',
            'password': 'safe_test_password_123'
        })
        token = json.loads(login_response.data)['token']
        
        # Access protected endpoint
        response = self.client.get('/api/profile', 
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['username'] == 'test_user_001'
        print("✅ Protected endpoint with valid token test passed")
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token"""
        response = self.client.get('/api/profile')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        print("✅ Protected endpoint without token test passed")
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        response = self.client.get('/api/profile', 
            headers={'Authorization': 'Bearer invalid_token_123'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
        print("✅ Protected endpoint with invalid token test passed")


def run_all_tests():
    """Run all tests sequentially"""
    print("🧪 Starting API tests...")
    
    test_instance = TestAPI()
    
    try:
        test_instance.setup_method()
        
        # Run tests in order
        test_instance.test_user_registration()
        test_instance.test_successful_login()
        test_instance.test_failed_login_wrong_password()
        test_instance.test_failed_login_wrong_username()
        test_instance.test_protected_endpoint_with_valid_token()
        test_instance.test_protected_endpoint_without_token()
        test_instance.test_protected_endpoint_with_invalid_token()
        
        test_instance.teardown_method()
        
        print("🎉 All API tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        test_instance.teardown_method()
        return False


if __name__ == "__main__":
    # Run tests when file is executed directly
    success = run_all_tests()
    exit(0 if success else 1)