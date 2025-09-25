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
        self._connect()

    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.database_name]
            self.reviews_collection = self.db.reviews
            
            # Create unique index on external_id to prevent duplicates
            self.reviews_collection.create_index("external_id", unique=True)
            
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")