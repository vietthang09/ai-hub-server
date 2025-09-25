from functools import wraps
from flask import request, jsonify, g
from src.services.jwt_service import JWTService
from src.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_service = JWTService()
        
        auth_header = request.headers.get('Authorization')
        token = jwt_service.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        payload = jwt_service.verify_access_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        g.current_user_email = payload['email']
        g.current_user_role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        jwt_service = JWTService()
        
        auth_header = request.headers.get('Authorization')
        token = jwt_service.extract_token_from_header(auth_header)
        
        if not token:
            return jsonify({'error': 'Missing or invalid authorization header'}), 401
        
        payload = jwt_service.verify_access_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        if payload.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        g.current_user_email = payload['email']
        g.current_user_role = payload['role']
        
        return f(*args, **kwargs)
    
    return decorated_function