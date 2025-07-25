from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from pymongo import UpdateOne

from app.models import db_w2v_mapper


class UserWeightRepository:
    def __init__(self, mongo_client: AsyncIOMotorClient):
        self.db = mongo_client["leadme"]
        self.collection: AsyncIOMotorCollection = self.db["user_weight"]

    def update_user_weights(
        self, user_id: int, meta_info: list[tuple[int, str]], weight: float
    ):
        operations = []
        for meta_id, name in meta_info:
            name = db_w2v_mapper.translate_genre(name)
            operations.append(
                UpdateOne(
                    {"user_id": user_id, "meta_info_id": meta_id},
                    {
                        "$inc": {"weight": weight},
                        "$set": {"name": name},
                    },
                    upsert=True,
                )
            )
        if operations:
            self.collection.bulk_write(operations)

    async def update_user_weights_from_log(self, log: dict, weight: float):
        user_id = log["userId"]
        meta_info = log.get("metaInfo", {})

        operations = []

        # 1. 장르
        for genre in meta_info.get("genres", []):
            name = db_w2v_mapper.translate_genre(genre)
            operations.append(
                UpdateOne(
                    {"user_id": user_id, "name": name},
                    {"$inc": {"weight": weight}, "$set": {"type": "genre"}},
                    upsert=True,
                )
            )

        # 2. 감독
        director = meta_info.get("director")
        if director:
            operations.append(
                UpdateOne(
                    {"user_id": user_id, "name": director},
                    {"$inc": {"weight": weight}, "$set": {"type": "director"}},
                    upsert=True,
                )
            )

        # 3. 배우
        for actor in meta_info.get("actors", []):
            operations.append(
                UpdateOne(
                    {"user_id": user_id, "name": actor},
                    {"$inc": {"weight": weight}, "$set": {"type": "actor"}},
                    upsert=True,
                )
            )

        # 4. 국가
        country = meta_info.get("country")
        if country:
            operations.append(
                UpdateOne(
                    {"user_id": user_id, "name": country},
                    {"$inc": {"weight": weight}, "$set": {"type": "country"}},
                    upsert=True,
                )
            )

        if operations:
            self.collection.bulk_write(operations)

    async def find_by_user_id(self, user_id: int) -> List[Dict]:
        cursor = self.collection.find({"user_id": user_id})
        results = await cursor.to_list(length=None)
        return results

    async def reset_weight(self, user_id: int, genre: str, weight: float):
        filter = {"user_id": user_id, "name": genre}
        update = {"$set": {"weight": weight}}
        await self.collection.update_one(filter, update, upsert=True)
