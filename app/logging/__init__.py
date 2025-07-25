import logging
from logging.handlers import TimedRotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = "app.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

# 로그 디렉터리 없으면 생성
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 중복 추가 방지
    if not logger.hasHandlers():
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(console_handler)

        # 파일 핸들러 (5MB 로테이션, 최대 5개 백업)
        file_handler = TimedRotatingFileHandler(
            LOG_PATH,
            when="midnight",         # 자정마다 회전
            interval=1,              # 1일마다
            backupCount=14           # 최근 14개 로그 파일 보관 (약 2주)
        )
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)