# log-reprocessor

사용자 행동 로그 중 `fail` 상태로 저장된 로그를 정기적으로 재처리하여 가중치를 업데이트합니다.

## 주요 기능

- MongoDB에 저장된 행동 로그 중 `status: fail`인 항목 스케줄링 재처리
- 성공 시 사용자 가중치 업데이트
- 재처리 성공 여부에 따라 `status` 필드(`success`, `fail`, `process`) 업데이트
- Recommender-server와 역할 분리 (이 서버는 재처리 및 보정 전용)

## 기술 스택

- **Python 3.12**
- Fast API

## 로컬 실행

```bash
# 가상 환경 생성
python3 -m venv venv # Windows: python -m venv venv

# 가상 환경 실행
source venv/bin/activate  # Windows: .\venv\Scripts\Activate

#현재 내 가상환경의 의존성을 requirements.txt에 적용
pip freeze > requirements.txt

# 의존성 설치
pip install -r requirements.txt

# 실행
uvicorn app.main:app --reload --port 8001

```

## 브라우저 접속

    •	루트 경로: http://localhost:8001
    •	Swagger 문서: http://localhost:8001/docs
