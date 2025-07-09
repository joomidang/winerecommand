# WineRecommend

와인 추천 시스템을 위한 FastAPI 기반 웹 애플리케이션입니다.

## 데이터베이스 초기화 방식 구분

- **자동 초기화:**
  - FastAPI 서버(`src/app.py`)를 실행하면, 서버 시작 시 데이터베이스와 테이블이 자동으로 생성되고 샘플 데이터가 삽입됩니다.
  - 별도의 초기화 명령 없이 바로 API를 사용할 수 있습니다.
  - (Docker, uvicorn 등으로 서버 실행 시 자동 적용)

- **수동/선택적 초기화:**
  - `src/init_db.py`를 직접 실행하면, 원하는 데이터셋을 선택하여 데이터베이스를 초기화할 수 있습니다.
  - 여러 데이터셋 중 선택, 통계 출력 등 개발/테스트에 유용합니다.
  - `.env` 파일, 명령행 인자, 대화형 선택 등 다양한 방식 지원

---

## 기능

- 와인 데이터 관리 및 검색
- 와인 추천 시스템
- RESTful API 제공
- 데이터베이스 통계 및 분석

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

프로젝트 루트에 `.env` 파일을 생성하고 설정을 추가합니다:

```bash
# env.example을 복사하여 .env 파일 생성
cp env.example .env
```

`.env` 파일에서 데이터셋을 선택할 수 있습니다:
```env
# 데이터셋 선택 (sample_csv, winemag 중 선택)
DATASET_CHOICE=sample_csv
```

### 3. 데이터베이스 초기화

프로젝트에는 두 가지 데이터셋이 포함되어 있습니다:
- `sample_wine_dataset.csv`: 샘플 데이터
- `winemag-data-130k-v2.csv`: 실제 와인 데이터 (130K 레코드)

데이터베이스를 초기화할 때 원하는 데이터셋을 선택할 수 있습니다:

#### 방법 1: .env 파일 사용 (권장)
```bash
# .env 파일에서 DATASET_CHOICE 설정 후 실행
python src/init_db.py
```

#### 방법 2: 명령행 인자 사용
```bash
# 샘플 데이터 사용
python src/init_db.py sample_csv

# 실제 데이터 사용
python src/init_db.py winemag
```

#### 방법 3: 대화형 선택
```bash
python src/init_db.py
```

### 3. 애플리케이션 실행

```bash
uvicorn src.app:app --reload
```

## API 엔드포인트

- `GET /wines/`: 모든 와인 목록 조회
- `GET /wines/{wine_id}`: 특정 와인 조회
- `GET /wines/search/`: 와인 검색 (필터링 옵션 포함)
- `GET /wines/stats/`: 와인 통계 정보

## 개발 도구

### 데이터베이스 설정 스크립트

```bash
# 직접 실행 (.env 파일 설정 사용)
python src/database/setup.py

# 특정 데이터셋 선택 (명령행 인자)
python src/database/setup.py winemag
```

### 사용 가능한 데이터셋 ID

- `sample_csv`: 샘플 데이터 (CSV)
- `winemag`: 실제 와인 데이터 (130K)

## 프로젝트 구조

```
WineRecommend/
├── data/                          # 데이터 파일
│   ├── sample_wine_dataset.csv
│   └── winemag-data-130k-v2.csv
├── src/
│   ├── api/                       # API 라우터
│   │   └── wines.py
│   ├── database/                  # 데이터베이스 설정
│   │   └── setup.py
│   ├── app.py                     # FastAPI 애플리케이션
│   └── init_db.py                 # 데이터베이스 초기화 스크립트
├── tests/                         # 테스트 파일
├── requirements.txt               # 의존성 목록
└── README.md
```

## Docker 지원

```bash
# Docker Compose로 실행
docker-compose up --build
```

## 라이선스

MIT License
