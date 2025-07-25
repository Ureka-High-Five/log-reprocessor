import asyncio

from logging import getLogger

from app.logger import setup_logging
from app.models.word2vec_model import Word2VecModel
from app.services.scheduler.retry_scheduler import load_retry_failed_log_scheduler
from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.background import BackgroundScheduler

from app.router import scheduler_router, test_log
from app.services.redis import close_redis, init_redis
from app.settings import settings
from app.services.daily_weight_resizer import remove_managed_action_log, resize_weight
from app.repositories.action_log_repository import ActionLogRepository
from app.repositories.user_weight_repository import UserWeightRepository

setup_logging()
logger = getLogger(__name__)

async def load_db(app: FastAPI):
    # MongoDB 연결
    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    app.state.mongo_client = mongo_client
    print("✅ MongoDB 연결 완료")

async def load_daily_weight_scheduler(app: FastAPI):
    scheduler = BackgroundScheduler(timezone='Asia/Seoul')

    mongo_client = app.state.mongo_client

    action_log_repo = ActionLogRepository(mongo_client)
    user_weight_repo = UserWeightRepository(mongo_client)
    async def schedule_resize_weight():
        await resize_weight(action_log_repo, user_weight_repo)
        await remove_managed_action_log()

    loop = asyncio.get_running_loop()

    def schedule_resize_weight_wrapper():
        asyncio.run_coroutine_threadsafe(schedule_resize_weight(), loop)

    scheduler.add_job(schedule_resize_weight_wrapper, "cron", hour=3, minute=0)
    scheduler.start()

    print("✅ Daily Weight Scheduler 설정 완료")
    

async def load_model():
    Word2VecModel.load_model(settings.W2V_MODEL_PATH)
    print("✅ Word2Vec 모델 로드 완료")


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await load_db(app)
    await init_redis()
    await load_model()
    await load_daily_weight_scheduler(app)
    await load_retry_failed_log_scheduler(app)
    
    yield
    print("🛑 앱 종료 중...")
    await close_redis()


app = FastAPI(
    title="log-reprocessor",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    return {"env": settings.DB_NAME}


app.include_router(scheduler_router.router)
app.include_router(test_log.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
