import os
from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

COLLECTION_USERS = "users"
COLLECTION_WORKOUT_PLANS = "workout_plans"
COLLECTION_SESSION_LOGS = "session_logs"


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return MongoClient(uri)


def get_database() -> Database:
    db_name = os.getenv("MONGODB_DB", "healthai_ia")
    return get_mongo_client()[db_name]
