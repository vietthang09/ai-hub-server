from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class Reviewer:
    name: str
    profile_photo: Optional[str] = None

@dataclass
class Review:
    external_id: str
    reviewer: Reviewer
    rating: int
    content: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    platform: str
    original_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'external_id': self.external_id,
            'reviewer': {
                'name': self.reviewer.name,
                'profile_photo': self.reviewer.profile_photo
            },
            'rating': self.rating,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'platform': self.platform,
            'original_data': self.original_data
        }
    
    @classmethod
    def from_dict(cls, review_dict: Dict[str, Any]) -> 'Review':
        reviewer_data = review_dict.get('reviewer', {})
        reviewer = Reviewer(
            name=reviewer_data.get('name', 'Anonymous'),
            profile_photo=reviewer_data.get('profile_photo')
        )
        
        return cls(
            external_id=review_dict.get('external_id', ''),
            reviewer=reviewer,
            rating=review_dict.get('rating', 0),
            content=review_dict.get('content', ''),
            created_at=cls._parse_datetime(review_dict.get('created_at')),
            updated_at=cls._parse_datetime(review_dict.get('updated_at')),
            platform=review_dict.get('platform', 'unknown'),
            original_data=review_dict.get('original_data', {})
        )

    @classmethod
    def from_google_review(cls, review_data: Dict[str, Any]) -> 'Review':
        reviewer = Reviewer(
            name=review_data.get('reviewer', {}).get('displayName', 'Anonymous'),
            profile_photo=review_data.get('reviewer', {}).get('profilePhotoUrl')
        )
        
        return cls(
            external_id=review_data.get('reviewId', ''),
            reviewer=reviewer,
            rating=cls._normalize_rating(review_data.get('starRating')),
            content=review_data.get('comment', review_data.get('text', '')),
            created_at=cls._parse_datetime(review_data.get('createTime')),
            updated_at=cls._parse_datetime(review_data.get('updateTime')),
            platform='google',
            original_data=review_data
        )
    
    @staticmethod
    def _normalize_rating(star_rating: Any) -> int:
        """Convert star rating to numeric value"""
        if isinstance(star_rating, (int, float)):
            return int(star_rating)
            
        rating_map = {
            'ONE': 1,
            'TWO': 2,
            'THREE': 3,
            'FOUR': 4,
            'FIVE': 5
        }
        return rating_map.get(star_rating, 0)
    
    @staticmethod
    def _parse_datetime(date_input: Any) -> Optional[datetime]:
        """Parse datetime string or return datetime object"""
        if not date_input:
            return None
            
        # If it's already a datetime object, return it
        if isinstance(date_input, datetime):
            return date_input
            
        # If it's a string, parse it
        if isinstance(date_input, str):
            try:
                # Handle ISO format with timezone
                if 'T' in date_input and 'Z' in date_input:
                    return datetime.fromisoformat(date_input.replace('Z', '+00:00'))
                return datetime.fromisoformat(date_input)
            except Exception:
                return None
                
        return None
    
    def __str__(self) -> str:
        return f"Review(external_id={self.external_id}, rating={self.rating}, reviewer={self.reviewer.name})"
    
    def __repr__(self) -> str:
        return self.__str__()