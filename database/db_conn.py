import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

ATLAS_URI = os.environ.get("ATLAS_URI", None)
DB_NAME = os.environ.get("DB_NAME", None)

client = MongoClient(ATLAS_URI, server_api=ServerApi('1'))
db_vls = client.vls