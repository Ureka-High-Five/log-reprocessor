from redis.asyncio import Redis
from app.settings import settings

redis = None


def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis가 초기화되지 않았습니다.")
    return redis

async def init_redis():
    global redis
    redis = Redis(host=settings.DEV_REDIS_HOST,
                  port=settings.DEV_REDIS_PORT,
                  decode_responses=True, 
                  socket_timeout=5,
                  socket_connect_timeout=5,
                  max_connections=50,
                  ssl=True,)
    print(f"✅ Redis 연결 성공: {redis}")

async def close_redis():
    if redis:
        await redis.close()
        print("🧹 Redis 연결 종료")

async def save_user_vector(user_id: int, value: str):
    try:
        await get_redis().set(str(user_id), value)
    except Exception as e:
        print(f"❌ Redis 저장 실패: {e}")