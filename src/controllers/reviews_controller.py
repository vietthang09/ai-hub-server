from flask import request, jsonify
from src.services.reviews_service import ReviewsService
import logging
from datetime import datetime
logger = logging.getLogger(__name__)

class ReviewsController:
    def __init__(self):
        self.reviews_service = ReviewsService()

    def pull_reviews(self):
        try:
            selected_location = "accounts/114352055335928504389/locations/2304352560750351356"

            logger.info(f"Fetching reviews for: {selected_location}")

            result = self.reviews_service.pull_reviews(selected_location)

            if not result['success']:
                return jsonify({
                    'error': 'Failed to fetch reviews',
                    'details': result['error']
                }), 500

            return jsonify({
                'success': True,
                'total_count': len(result['reviews']),
                'saved_count': result['saved_count'],
                'skipped_count': result['skipped_count'],
                'metadata': {
                    'selected_location': selected_location,
                    'pulled_at': datetime.utcnow().isoformat()
                }
            })

        except Exception as e:
            logger.error(f"Reviews controller error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500
        
    def get_reviews(self):
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 24))
            
            if page < 1:
                page = 1
            if limit < 1:
                limit = 24
            if limit > 100: 
                limit = 100
                
            result = self.reviews_service.find_reviews(page=page, limit=limit)
            
            return jsonify({
                'success': True,
                'total_count': result['total_count'],
                'page': page,
                'limit': limit,
                'total_pages': result['total_pages'],
                'reviews': result['reviews']
            })

        except ValueError as e:
            logger.error(f"Invalid query parameters: {str(e)}")
            return jsonify({
                'error': 'Invalid query parameters',
                'message': 'Page and limit must be valid integers'
            }), 400
        except Exception as e:
            logger.error(f"Get reviews error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e)
            }), 500