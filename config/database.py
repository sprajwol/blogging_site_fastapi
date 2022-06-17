from enum import unique
from pymongo import MongoClient, TEXT

from utils import utils
from models.user import ROLES_M

conn_str = MongoClient("mongodb://localhost:27017")

db = conn_str["test_db"]
collection = db["user"]

if not 'user' in db.list_collection_names():

    hashed_password = utils.hash("Testing@123")
    a = collection.insert_one(
        {
            "name": "Admin",
            "email": "admin@admin.com",
            "role": "admin",
            "password": hashed_password,
            "is_approved": True
        }
    )
collection.create_index([('email', 1)], unique=True)


user_vexpr = {
    "$jsonSchema":
    {
        "bsonType": "object",
        "required": ["email", "password", "role"],
        "properties": {
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string and is not required"
            },
            "role": {
                "enum": [e.value for e in ROLES_M],
                "description": "can only be one of the enum values and is required"
            }
        }
    }
}

db.command('collMod', 'user', validator=user_vexpr, validationLevel='moderate')
