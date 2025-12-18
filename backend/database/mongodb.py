import os
import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "admin")

# SSL certificate configuration for MongoDB Atlas
TLS_CA_FILE = certifi.where()

# Async MongoDB client for FastAPI
async_client: AsyncIOMotorClient = None
async_db = None
async_fs: AsyncIOMotorGridFSBucket = None

# Sync client for non-async operations
sync_client: MongoClient = None
sync_db = None


def get_database():
    """Get synchronous database instance"""
    global sync_client, sync_db
    if sync_db is None:
        sync_client = MongoClient(MONGODB_URI, tlsCAFile=TLS_CA_FILE)
        sync_db = sync_client[DATABASE_NAME]
    return sync_db


async def connect_to_mongodb():
    """Connect to MongoDB on startup"""
    global async_client, async_db, async_fs
    async_client = AsyncIOMotorClient(MONGODB_URI, tlsCAFile=TLS_CA_FILE)
    async_db = async_client[DATABASE_NAME]
    async_fs = AsyncIOMotorGridFSBucket(async_db)
    print(f"✅ Connected to MongoDB: {DATABASE_NAME}")


async def close_mongodb_connection():
    """Close MongoDB connection on shutdown"""
    global async_client
    if async_client:
        async_client.close()
        print("❌ Closed MongoDB connection")


def get_async_database():
    """Get async database instance"""
    return async_db


def get_gridfs():
    """Get GridFS bucket for file storage"""
    return async_fs
