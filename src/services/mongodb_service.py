from pymongo import MongoClient
import os
import logging

logger = logging.getLogger(__name__)

class MongoDBService:
    def __init__(self):
        self.mongo_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
        self.database_name = os.getenv('DATABASE_NAME', 'ai_hub')
        self.client = None
        self.db = None
        self.reviews_collection = None
        self.users_collection = None
        self.refresh_tokens_collection = None
        self._connect()

    def _connect(self):
        try:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.database_name]
            self.reviews_collection = self.db.reviews
            self.users_collection = self.db.users
            self.refresh_tokens_collection = self.db.refresh_tokens
            
            self.reviews_collection.create_index("external_id", unique=True)
            self.users_collection.create_index("email", unique=True)
            self.refresh_tokens_collection.create_index("token", unique=True)
            self.refresh_tokens_collection.create_index("expires_at", expireAfterSeconds=0)
            
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")