from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass
import secrets

@dataclass
class RefreshToken:
    token: str
    user_email: str
    expires_at: datetime
    created_at: Optional[datetime] = None
    is_revoked: bool = False
    _id: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @classmethod
    def create_token(cls, user_email: str, days_valid: int = 30) -> 'RefreshToken':
        """Create a new refresh token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=days_valid)
        
        return cls(
            token=token,
            user_email=user_email,
            expires_at=expires_at
        )
    
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return not self.is_revoked and datetime.utcnow() < self.expires_at
    
    def revoke(self):
        """Revoke the token"""
        self.is_revoked = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            'token': self.token,
            'user_email': self.user_email,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_revoked': self.is_revoked
        }
    
    @classmethod
    def from_dict(cls, token_dict: Dict[str, Any]) -> 'RefreshToken':
        """Create from dictionary"""
        token = cls(
            token=token_dict.get('token', ''),
            user_email=token_dict.get('user_email', ''),
            expires_at=cls._parse_datetime(token_dict.get('expires_at')),
            created_at=cls._parse_datetime(token_dict.get('created_at')),
            is_revoked=token_dict.get('is_revoked', False)
        )
        token._id = str(token_dict.get('_id', ''))
        return token
    
    @staticmethod
    def _parse_datetime(date_input: Any) -> datetime:
        """Parse datetime string"""
        if isinstance(date_input, datetime):
            return date_input
        if isinstance(date_input, str):
            return datetime.fromisoformat(date_input)
        return datetime.utcnow()