from fastapi import FastAPI
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

from app.settings import settings


async def load_db(app: FastAPI):
    # MongoDB 연결
    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    app.state.mongo_client = mongo_client
    print("✅ MongoDB 연결 완료")

    # PostgreSQL 연결
    pg_pool = await asyncpg.create_pool(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USERNAME,
        password=settings.DB_PASSWORD,
    )
    app.state.pg_pool = pg_pool
    print("✅ PostgreSQL 연결 완료")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_db(app)
    yield
    print("🛑 앱 종료 중...")


app = FastAPI(
    title="log-reprocessor",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    return {"env": settings.DB_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
