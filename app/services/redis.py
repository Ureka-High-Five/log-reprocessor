from redis.asyncio import Redis
from app.settings import settings

redis = None

async def init_redis():
    global redis
    redis = Redis(host=settings.DEV_REDIS_HOST, port=settings.DEV_REDIS_PORT, decode_responses=True)
    print(f"✅ Redis 연결 성공: {redis}")

async def close_redis():
    if redis:
        await redis.close()
        print("🧹 Redis 연결 종료")

async def save_user_vector(user_id: int, value: str):
    await redis.set(user_id, value)