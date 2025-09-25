import requests
import os
from typing import Dict, List, Any
import logging
from src.modal.review import Review
from pymongo.errors import DuplicateKeyError
from src.services.mongodb_service import MongoDBService

logger = logging.getLogger(__name__)

class ReviewsService:
    def __init__(self):
        self.api_url = os.getenv('REVIEWS_API_URL')
        self.api_cookie = os.getenv('REVIEWS_API_COOKIE')
        self.mongodb_service = MongoDBService()
        
        self.session = requests.Session()
        self.session.headers.update({
            'Cookie': self.api_cookie,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.session.timeout = 30

    def pull_reviews(self, business_url: str, options: Dict = None) -> Dict[str, Any]:
        if options is None:
            options = {}
            
        try:
            payload = {
                'selectedLocation': business_url
            }

            response = self.session.post(
                f"{self.api_url}/google/getReviews",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            reviews = self._create_review_models(data.get('reviews', []))

            saved_count, skipped_count = self._save_reviews_to_db(reviews)
            
            return {
                'success': True,
                'data': data,
                'reviews': reviews,
                'saved_count': saved_count,
                'skipped_count': skipped_count
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching reviews: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'data': None
            }
    
    def find_reviews(self, page: int = 1, limit: int = 24, query: Dict = None) -> Dict[str, Any]:
        try:
            if query is None:
                query = {}
            skip = (page - 1) * limit
            total_count = self.mongodb_service.reviews_collection.count_documents(query)
            total_pages = (total_count + limit - 1) // limit 
            review_dicts = self.mongodb_service.reviews_collection.find(query)\
                .sort("created_at", -1)\
                .skip(skip)\
                .limit(limit)
            
            reviews = [Review.from_dict(rd).to_dict() for rd in review_dicts]
            
            return {
                'reviews': reviews,
                'total_count': total_count,
                'total_pages': total_pages,
                'current_page': page,
                'limit': limit
            }
            
        except Exception as e:
            logger.error(f"Error finding paginated reviews: {str(e)}")
            return {
                'reviews': [],
                'total_count': 0,
                'total_pages': 0,
                'current_page': page,
                'limit': limit
            }
        
    def _create_review_models(self, reviews_data: List[Dict]) -> List[Review]:
        reviews = []
        
        for review_data in reviews_data:
            try:
                review = Review.from_google_review(review_data)
                reviews.append(review)
            except Exception as e:
                logger.warning(f"Error creating review model: {str(e)}")
                continue
                
        return reviews
    
    def _save_reviews_to_db(self, reviews: List[Review]) -> tuple[int, int]:
        saved_count = 0
        skipped_count = 0
        
        for review in reviews:
            try:
                review_dict = review.to_dict()
                self.mongodb_service.reviews_collection.insert_one(review_dict)
                saved_count += 1
                logger.info(f"Saved review: {review.external_id}")
            except DuplicateKeyError:
                skipped_count += 1
                logger.info(f"Review already exists, skipping: {review.external_id}")
            except Exception as e:
                logger.error(f"Error saving review {review.external_id}: {str(e)}")
                continue
        
        logger.info(f"Reviews saved: {saved_count}, skipped: {skipped_count}")
        return saved_count, skipped_count