from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

@dataclass
class User:
    email: str
    password_hash: str
    role: str  # 'user' or 'admin'
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    _id: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    @classmethod
    def create_user(cls, email: str, password: str, role: str = 'user') -> 'User':
        password_hash = generate_password_hash(password)
        return cls(
            email=email,
            password_hash=password_hash,
            role=role
        )
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, user_dict: Dict[str, Any]) -> 'User':
        user = cls(
            email=user_dict.get('email', ''),
            password_hash=user_dict.get('password_hash', ''),
            role=user_dict.get('role', 'user'),
            is_active=user_dict.get('is_active', True),
            created_at=cls._parse_datetime(user_dict.get('created_at')),
            updated_at=cls._parse_datetime(user_dict.get('updated_at'))
        )
        user._id = str(user_dict.get('_id', ''))
        return user
    
    @staticmethod
    def _parse_datetime(date_input: Any) -> Optional[datetime]:
        if not date_input:
            return None
        if isinstance(date_input, datetime):
            return date_input
        if isinstance(date_input, str):
            try:
                return datetime.fromisoformat(date_input)
            except Exception:
                return None
        return None
    
    def __str__(self) -> str:
        return f"User(email={self.email}, role={self.role})"