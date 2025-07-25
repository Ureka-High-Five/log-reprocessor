import asyncio
import logging
import math
import time
import numpy as np
from collections import defaultdict
from app.models import db_w2v_mapper
from app.services import weight_strategy
from app.enum.action_type import ActionType
from app.services import redis
from typing import Dict, List
from app.models.word2vec_util import calc_user_vector
from app.util.weight_aging import exponential_decay_weight
from app.repositories.action_log_repository import ActionLogRepository
from app.repositories.user_weight_repository import UserWeightRepository

MAX_RETRIES = 3
RETRY_DELAY_SEC = 1

async def resize_weight(
    action_log_repo: ActionLogRepository,
    user_weight_repo: UserWeightRepository,
):
    # ✅ 모든 로그 조회 재시도 로직
    all_logs = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            all_logs = await action_log_repo.find_all_order_by_user_id()
            break
        except Exception as e:
            logging.warning(f"[daily_weight_resizer][{attempt}/{MAX_RETRIES}] 로그 조회 실패: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY_SEC)
            else:
                logging.error(f"[daily_weight_resizer] 모든 재시도 실패, 로그 조회 불가, error: {e}")
                return


    # 사용자별로 로그 분리
    grouped_logs = group_logs_by_user_id(all_logs)

    failed = []
    for user_id, logs in grouped_logs.items():
        genre_dict = defaultdict(int)
        for log in logs:
            action_type = ActionType[log['action']]
            value = int(log['value'])

            # 로그를 가중치로 변환
            weight = weight_strategy.convert_to_weight(action_type, value)
            # 가중치 resize
            resized_weight = exponential_decay_weight(weight, log['timestamp'])

            # 각 장르에 가중치 적용
            genres = log['metaInfo']['genres']
            for genre in genres:
                translated = db_w2v_mapper.translate_genre(genre)
                if translated:
                    genre_dict[translated] += resized_weight

        # MongoDB에 resized 가중치 저장
        for genre_name, resized_weight in genre_dict.items():
            try:
                await user_weight_repo.reset_weight(user_id, genre_name, resized_weight)
            except:
                failed.append((user_id, genre_name, resize_weight))
                
        # resized 가중치 기반으로 벡터 계산
        vector = calc_user_vector(genre_dict)
        vector_str = np.array2string(vector, separator=', ')

        try:
            await redis.save_user_vector(user_id, vector_str)
            print(f'✅ 사용자 {user_id} 벡터 Redis 저장 완료')
        except Exception as e:
            print(f'❌ 사용자 {user_id} 벡터 Redis 저장 실패: {e}')

        # 실패 로그 재시도
        for user_id, genre_name, resize_weight in failed:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    await user_weight_repo.reset_weight(user_id, genre_name, resized_weight)
                except Exception as e:
                    if (attempt < MAX_RETRIES):
                        logging.warning(f"[daily_weight_resizer][{attempt}/{MAX_RETRIES}] 보상 트랜잭션 재시도")
                    else:
                        logging.error(
                            f"[daily_weight_resizer] 보상트랜잭션 실패, log_id: {log['_id']}, error: {e}"
                        )
    print("✅ 가중치 resizing 완료")
    return

def calc_resized_weight(timestamp : int, weight : float):
  current_timestamp_ms = int(time.time() * 1000)
  delta_ms = current_timestamp_ms - timestamp
  delta_days = delta_ms / (1000 * 60 * 60 * 24)

  resized_weight = weight * math.exp(-1 * delta_days)
  return resized_weight

def group_logs_by_user_id(logs: List[Dict]) -> Dict[int, List[Dict]]:
    grouped = defaultdict(list)
    for log in logs:
        user_id = log["userId"]
        grouped[user_id].append(log)
    return dict(grouped)