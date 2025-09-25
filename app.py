from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Import routes
from src.routes.reviews import reviews_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Register blueprints
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)