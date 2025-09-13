import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    logger.info("Connecting to MongoDB...")
    
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable is not set")
    
    db.client = AsyncIOMotorClient(
        mongo_url,
        maxPoolSize=10,
        minPoolSize=1,
    )
    
    # Get database name from environment or use default
    db_name = os.environ.get('DB_NAME', 'tourism_safety')
    db.database = db.client[db_name]
    
    # Test the connection
    try:
        await db.database.command("ping")
        logger.info(f"Successfully connected to MongoDB database: {db_name}")
        
        # Create indexes for better performance
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    logger.info("Closing MongoDB connection...")
    if db.client:
        db.client.close()

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        database = await get_database()
        
        # Users indexes
        await database.users.create_index("email", unique=True)
        await database.users.create_index("badge_number")
        
        # Tourists indexes
        await database.tourists.create_index("digital_id", unique=True)
        await database.tourists.create_index("status")
        await database.tourists.create_index("nationality")
        await database.tourists.create_index("safety_score")
        await database.tourists.create_index("last_location_update")
        
        # Location history indexes
        await database.location_history.create_index("tourist_id")
        await database.location_history.create_index("timestamp")
        await database.location_history.create_index([("coordinates", "2dsphere")])  # Geospatial index
        
        # Alerts indexes
        await database.alerts.create_index("alert_id", unique=True)
        await database.alerts.create_index("tourist_id")
        await database.alerts.create_index("alert_type")
        await database.alerts.create_index("status")
        await database.alerts.create_index("severity")
        await database.alerts.create_index("created_at")
        await database.alerts.create_index([("location.coordinates", "2dsphere")])  # Geospatial index
        
        # Geofences indexes
        await database.geofences.create_index("type")
        await database.geofences.create_index("risk_level")
        await database.geofences.create_index("active")
        await database.geofences.create_index([("coordinates", "2dsphere")])  # Geospatial index
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        # Don't raise here as the app can still function without indexes

# Collection helpers
async def get_users_collection():
    database = await get_database()
    return database.users

async def get_tourists_collection():
    database = await get_database()
    return database.tourists

async def get_location_history_collection():
    database = await get_database()
    return database.location_history

async def get_alerts_collection():
    database = await get_database()
    return database.alerts

async def get_geofences_collection():
    database = await get_database()
    return database.geofences