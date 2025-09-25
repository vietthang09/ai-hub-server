import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class JWTService:
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
        self.algorithm = 'HS256'
        self.access_token_expiry = int(os.getenv('ACCESS_TOKEN_EXPIRY_MINUTES', 15))  # 15 minutes
    
    def generate_access_token(self, user_email: str, role: str) -> str:
        payload = {
            'email': user_email,
            'role': role,
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expiry),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get('type') != 'access':
                return None
                
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Access token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid access token: {str(e)}")
            return None
    
    def extract_token_from_header(self, auth_header: str) -> Optional[str]:
        if not auth_header:
            return None
            
        parts = auth_header.split(' ')
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
            
        return parts[1]