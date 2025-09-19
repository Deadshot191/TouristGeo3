import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(os.environ.get("MONGO_URL"))
        db.database = db.client[os.environ.get("DATABASE_NAME", "tourism_security")]
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB (Digital ID Service)")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB (Digital ID Service)")

async def create_indexes():
    """Create database indexes for optimized queries"""
    try:
        # Secure tourist data collection indexes
        await db.database.secure_tourist_data.create_index([("tourist_id", ASCENDING)], unique=True)
        await db.database.secure_tourist_data.create_index([("created_at", DESCENDING)])
        
        # Data access log collection indexes  
        await db.database.data_access_log.create_index([("tourist_id", ASCENDING)])
        await db.database.data_access_log.create_index([("timestamp", DESCENDING)])
        await db.database.data_access_log.create_index([("authority_id", ASCENDING)])
        await db.database.data_access_log.create_index([("access_type", ASCENDING)])
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    return db.database