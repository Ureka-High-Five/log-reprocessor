from typing import List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


class ManagedActionLogRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.db = mongo_client["leadme"]
        self.collection: AsyncIOMotorCollection = self.db["managed_action_log"]

    async def find_failed_logs(self) -> List[dict]:
        cursor = self.collection.find({"status": "FAIL"})
        return await cursor.to_list(length=None)

    async def delete_by_id(self, _id: str):
        await self.collection.delete_one({"_id": _id})
