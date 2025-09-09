from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# connnect to mongo atlass cluster
mongo_client = MongoClient(os.getenv("MONGO_URI"))


# acess database
ecommerce_api_db = mongo_client["ecommerce_api_db"]

# pick a connection to operate on
products_collection = ecommerce_api_db["products"]
user_collection = ecommerce_api_db["users"]
carts_collection = ecommerce_api_db["carts"]
