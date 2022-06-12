import asyncio
import os
import motor.motor_asyncio


from src.constants import TESTING
from dotenv import load_dotenv

load_dotenv()


if TESTING is not None:
    print("TEST DB")
    MONGO_URL = os.environ.get("TEST_MONGO_URL", "mongodb://mongo:27017/")
else:
    print("PROD DB")
    MONGO_URL = os.environ.get("MONGO_URL", "")


client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
client.get_io_loop = asyncio.get_running_loop
db = client.get_database("messages")


async def get_db():
    yield db
