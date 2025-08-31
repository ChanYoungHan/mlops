# 모델 v0 개발 제안서

## 목표
- 제로베이스 파이프라인 검증
- 데이터 → 추론 → DB 삽입의 기본 사이클 정상 동작 확인
- 임계값 기반 단순 분류기로 모델/인프라 기초 검증

---

## 파이프라인 구성

### 1. 수집기 (Collector)
- **역할**: 데이터 시드 생성 후 DB에 삽입
- **DB Schema (input table)**

```sql
id INT PRIMARY KEY,
created_at TIMESTAMP,
data FLOAT,
processed BOOLEAN DEFAULT FALSE
```

- **구현**
  - Python script (`collector.py`)
  - 무작위 `data` 값 생성 후 DB insert
  - `processed = FALSE` 로 저장

---

### 2. 프로세서 (Processor / Inference)
- **역할**: 주기적으로 미처리 데이터 조회 후 추론 및 DB 업데이트
- **스케줄링**
  - Airflow DAG, 10분 주기
- **처리 로직**
  - DB에서 `processed = FALSE` 인 row 조회
  - 간단한 Threshold 모델 적용
    - `y = "HIGH"` if data ≥ θ else `"LOW"`
  - 결과 DB 업데이트 (`predicted`, `model_used`)

- **구현**
  - Python script (`processor.py`)
  - ONNX/XGBoost 같은 복잡 모델은 배제, 단순 threshold
  - Airflow DAG (`dag_inference.py`) 작성

---

### 3. 싱크 (Sink / Output DB)
- **역할**: 추론 결과 저장
- **DB Schema (output table)**

```sql
id INT PRIMARY KEY,
created_at TIMESTAMP,
data FLOAT,
predicted VARCHAR(10),
model_used VARCHAR(50),
processed BOOLEAN DEFAULT TRUE
```

- **구현**
  - `UPDATE input_table SET predicted=?, model_used=?, processed=TRUE WHERE id=?`
  - 결과를 동일 테이블에 update 하거나 별도 `result_table` 로 분리 가능

---

## 개발 단계

1. **v0 Collector**
   - Python script 로 데이터 insert
   - Docker-compose 기반 DB(Postgres) + script 컨테이너 실행 확인

2. **v0 Processor**
   - 단일 스크립트로 threshold 분류 수행
   - Airflow DAG 연결 및 주기 실행 확인

3. **v0 Sink**
   - 추론 결과 update
   - DB에서 결과 select 하여 end-to-end 정상 동작 검증

---

## 산출물
- `collector.py`
- `processor.py`
- `dag_inference.py`
- `docker-compose.yaml` (DB + Airflow 환경)
- `README.md` (실행 및 로컬 테스트 방법)
