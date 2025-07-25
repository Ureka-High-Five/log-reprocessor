from fastapi import APIRouter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/log-test")
async def log_test():
    logger.debug("🐛 DEBUG 로그")
    logger.info("✅ INFO 로그")
    logger.warning("⚠️ WARNING 로그")
    logger.error("❌ ERROR 로그")
    logger.critical("🔥 CRITICAL 로그")
    return {"message": "로그 테스트 완료"}