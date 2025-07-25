import asyncio
from app.services.log_reprocessor_service import retry_failed_logs
from apscheduler.schedulers.background import BackgroundScheduler


async def load_retry_failed_log_scheduler(app):
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    mongo_client = app.state.mongo_client
    loop = asyncio.get_running_loop()

    def run_retry_job():
        future = asyncio.run_coroutine_threadsafe(retry_failed_logs(mongo_client), loop)
        try:
            future.result() 
        except Exception as e:
            print(f"[actionlog_status_update_failed] 보상트랜잭션 스케줄러 실행 실패: {e}")

    scheduler.add_job(run_retry_job, "cron", minute="*/1")
    scheduler.start()

    print("✅ Retry Failed Log Scheduler 설정 완료")
