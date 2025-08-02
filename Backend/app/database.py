import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGODB_URI")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.footwear
user_collection = database.get_collection("users")
product_collection = database.get_collection("products")
sale_collection = database.get_collection("sales")