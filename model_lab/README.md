# Model Lab

MLOps 파이프라인에서 사용할 **모델 버전별 실험 환경**입니다.  
각 버전별 디렉토리(`models/vN/`, `output/vN/`)에서 모델 파라미터와 결과를 관리합니다.

---

## 디렉토리 구조
```
model_lab/
├── models/
│   ├── v0/          # threshold 모델 (baseline)
│   ├── v1/          # onnx 모델 (예: Logistic Regression)
│   └── vN/          # 이후 버전 확장
├── output/
│   ├── v0/
│   ├── v1/
│   └── vN/
├── v0_infer_single.py
└── README.md
```

---

## v0: Threshold Baseline

### 1. 모델 파라미터 수정
`models/v0/model.yaml`
```yaml
model_name: threshold-binary
model_version: 0.1.0
params:
  theta_low: 0.60
  theta_high: 0.60  # 단일 임계값일 경우 동일하게 설정
```

### 2. 추론 실행 방법

#### (1) 합성 데이터로 실행
```bash
python v0_infer_single.py \
  --model ./models/v0/model.yaml \
  --sample-n 40 \
  --output-csv ./output/v0/predictions.csv
```

#### (2) CSV 입력으로 실행
```bash
python v0_infer_single.py \
  --model ./models/v0/model.yaml \
  --input-csv your_data.csv \
  --output-csv ./output/v0/predictions.csv
```

### 3. 결과 확인
`./output/v0/predictions.csv`
- id, created_at, data
- predicted (pos/neg)
- proba (v0에서는 NULL)
- model_used (버전 + 해시)

---

## v1 이후: ONNX 기반 모델
- `models/v1/`에 `model.onnx`, `schema.json`, `model_card.yaml` 파일을 둡니다.
- 추론 스크립트는 `onnxruntime`을 사용하여 실행됩니다.  
- 설정 파일 예시:
```yaml
model:
  type: onnx
  dir: ./models/v1/
```

---

## vN 확장 전략
- **v2**: 캘리브레이션 적용(LogisticRegression + Calibrator)
- **v3**: 앙상블 모델
- **vN**: 프로젝트 필요에 맞는 고도화된 모델

각 버전은 동일한 인터페이스(`--model`, `--input-csv`, `--output-csv`)를 따르도록 유지하여,  
파이프라인 및 스크립트 호환성을 확보합니다.
