from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import ASCENDING

class ActionLogRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.db = mongo_client["leadme"]
        self.collection: AsyncIOMotorCollection = self.db["action_log"]

    async def find_by_user_id(self, user_id: int) -> List[Dict]:
        cursor = self.collection.find({"userId": user_id})
        return await cursor.to_list(length=None)

    async def find_all_order_by_user_id(self) -> List[Dict]:
        cursor = self.collection.find().sort("userId", ASCENDING)
        return await cursor.to_list(length=None)
