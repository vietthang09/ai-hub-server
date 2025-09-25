from flask import request, jsonify
from src.services.auth_service import AuthService
import logging
import re

logger = logging.getLogger(__name__)

class AuthController:
    def __init__(self):
        self.auth_service = AuthService()
    
    def register(self):
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            role = "user"
            
            # Validate input
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            if not self._is_valid_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            
            if len(password) < 6:
                return jsonify({'error': 'Password must be at least 6 characters long'}), 400
            
            if role not in ['user', 'admin']:
                return jsonify({'error': 'Invalid role. Must be "user" or "admin"'}), 400
            
            # Register user
            result = self.auth_service.register_user(email, password, role)
            
            if not result['success']:
                return jsonify({'error': result['error']}), 400
            
            return jsonify({
                'success': True,
                'message': result['message']
            }), 201
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return jsonify({'error': 'Registration failed'}), 500
    
    def login(self):
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400
            
            # Login user
            result = self.auth_service.login_user(email, password)
            
            if not result['success']:
                return jsonify({'error': result['error']}), 401
            
            return jsonify({
                'success': True,
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token'],
                'user': result['user']
            })
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return jsonify({'error': 'Login failed'}), 500
    
    def refresh_token(self):
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'error': 'Refresh token is required'}), 400
            
            result = self.auth_service.refresh_access_token(refresh_token)
            
            if not result['success']:
                return jsonify({'error': result['error']}), 401
            
            return jsonify({
                'success': True,
                'access_token': result['access_token']
            })
            
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return jsonify({'error': 'Token refresh failed'}), 500
    
    def logout(self):
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'error': 'Refresh token is required'}), 400
            
            result = self.auth_service.logout_user(refresh_token)
            
            if not result['success']:
                return jsonify({'error': result['error']}), 400
            
            return jsonify({
                'success': True,
                'message': result['message']
            })
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return jsonify({'error': 'Logout failed'}), 500
    
    def _is_valid_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None