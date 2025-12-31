"""MongoDB database connection management using Motor async driver.

This module handles async MongoDB connections for the application using Motor,
which provides async/await support for MongoDB operations in FastAPI.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
from config import settings

# Global database client and database instances
client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """Establish connection to MongoDB database.
    
    Initializes the global MongoDB client and database instance.
    Tests the connection with a ping command to ensure it's working.
    
    Raises:
        Exception: If connection fails
    """
    global client, db
    try:
        # Create async MongoDB client
        client = AsyncIOMotorClient(settings.mongodb_url)
        # Select database
        db = client[settings.database_name]
        # Test the connection by pinging the database
        await client.admin.command('ping')
        print(f"Connected to MongoDB: {settings.database_name}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection gracefully.
    
    Called during application shutdown to clean up database connections.
    """
    global client
    if client:
        client.close()
        print("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance for dependency injection.
    
    Returns:
        AsyncIOMotorDatabase: The active MongoDB database instance
    """
    return db
