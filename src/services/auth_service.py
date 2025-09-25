from typing import Dict, Any, Optional, Tuple
import logging
from src.modal.user import User
from src.modal.refresh_token import RefreshToken
from src.services.mongodb_service import MongoDBService
from src.services.jwt_service import JWTService
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.mongodb_service = MongoDBService()
        self.jwt_service = JWTService()
    
    def register_user(self, email: str, password: str, role: str = 'user') -> Dict[str, Any]:
        try:
            if role not in ['user', 'admin']:
                return {
                    'success': False,
                    'error': 'Invalid role. Must be "user" or "admin"'
                }
            
            user = User.create_user(email=email, password=password, role=role)
            
            user_dict = user.to_dict()
            self.mongodb_service.users_collection.insert_one(user_dict)
            
            logger.info(f"User registered successfully: {email}")
            return {
                'success': True,
                'message': 'User registered successfully'
            }
            
        except DuplicateKeyError:
            return {
                'success': False,
                'error': 'User with this email already exists'
            }
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to register user'
            }
    
    def login_user(self, email: str, password: str) -> Dict[str, Any]:
        try:
            user_dict = self.mongodb_service.users_collection.find_one({'email': email})
            if not user_dict:
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            user = User.from_dict(user_dict)
            
            if not user.is_active:
                return {
                    'success': False,
                    'error': 'User account is deactivated'
                }
            
            if not user.check_password(password):
                return {
                    'success': False,
                    'error': 'Invalid email or password'
                }
            
            access_token = self.jwt_service.generate_access_token(user.email, user.role)
            refresh_token = RefreshToken.create_token(user.email)
            
            self.mongodb_service.refresh_tokens_collection.insert_one(refresh_token.to_dict())
            
            logger.info(f"User logged in successfully: {email}")
            return {
                'success': True,
                'access_token': access_token,
                'refresh_token': refresh_token.token,
                'user': {
                    'email': user.email,
                    'role': user.role
                }
            }
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return {
                'success': False,
                'error': 'Login failed'
            }
    
    def refresh_access_token(self, refresh_token_str: str) -> Dict[str, Any]:
        try:
            token_dict = self.mongodb_service.refresh_tokens_collection.find_one({
                'token': refresh_token_str
            })
            
            if not token_dict:
                return {
                    'success': False,
                    'error': 'Invalid refresh token'
                }
            
            refresh_token = RefreshToken.from_dict(token_dict)
            
            if not refresh_token.is_valid():
                return {
                    'success': False,
                    'error': 'Refresh token expired or revoked'
                }
            
            user_dict = self.mongodb_service.users_collection.find_one({
                'email': refresh_token.user_email
            })
            
            if not user_dict:
                return {
                    'success': False,
                    'error': 'User not found'
                }
            
            user = User.from_dict(user_dict)
            
            access_token = self.jwt_service.generate_access_token(user.email, user.role)
            
            return {
                'success': True,
                'access_token': access_token
            }
            
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to refresh token'
            }
    
    def logout_user(self, refresh_token_str: str) -> Dict[str, Any]:
        try:
            result = self.mongodb_service.refresh_tokens_collection.update_one(
                {'token': refresh_token_str},
                {'$set': {'is_revoked': True}}
            )
            
            if result.modified_count == 0:
                return {
                    'success': False,
                    'error': 'Invalid refresh token'
                }
            
            return {
                'success': True,
                'message': 'Logged out successfully'
            }
            
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return {
                'success': False,
                'error': 'Logout failed'
            }
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        try:
            user_dict = self.mongodb_service.users_collection.find_one({'email': email})
            if user_dict:
                return User.from_dict(user_dict)
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None