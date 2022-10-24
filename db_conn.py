import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv

# Get the path to the directory this file is in
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Connect the path with your '.env' file name
load_dotenv(os.path.join(BASEDIR, '.env'), verbose=True)

ATLAS_URI = os.getenv("ATLAS_URI")

client = MongoClient(ATLAS_URI, server_api=ServerApi('1'))
db_vls = client.vls