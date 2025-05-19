# config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 설정 - 환경 변수에서 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 모델 설정
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# 경로 설정
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MARKET_REPORTS_DIR = DATA_DIR / "market_reports"
COMPANY_DOCS_DIR = DATA_DIR / "company_docs"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# 분석 대상 기업 설정
# 한국 금융권 업종별 주요 기업
TARGET_COMPANIES = {
    "은행": [
        {"code": "105560", "name": "KB금융지주"},
        {"code": "055550", "name": "신한지주"},
        {"code": "086790", "name": "하나금융지주"},
        {"code": "316140", "name": "우리금융지주"},
        {"code": "138930", "name": "BNK금융지주"},
        {"code": "139130", "name": "DGB금융지주"},
        {"code": "175330", "name": "JB금융지주"},
        {"code": "024110", "name": "기업은행"},
        {"code": "071050", "name": "한국금융지주"},
        {"code": "138040", "name": "메리츠금융지주"}
    ],
    "증권": [
        {"code": "006800", "name": "미래에셋증권"},
        {"code": "005940", "name": "NH투자증권"},
        {"code": "016360", "name": "삼성증권"},
        {"code": "039490", "name": "키움증권"},
        {"code": "078020", "name": "한국투자증권"},
        {"code": "008560", "name": "메리츠증권"},
        {"code": "003540", "name": "대신증권"},
        {"code": "001720", "name": "신영증권"},
        {"code": "003470", "name": "유안타증권"},
        {"code": "030610", "name": "교보증권"}
    ],
    "보험": [
        {"code": "032830", "name": "삼성생명"},
        {"code": "000810", "name": "삼성화재"},
        {"code": "005830", "name": "DB손해보험"},
        {"code": "001450", "name": "현대해상"},
        {"code": "000060", "name": "메리츠화재"},
        {"code": "088350", "name": "한화생명"},
        {"code": "000400", "name": "롯데손해보험"},
        {"code": "093050", "name": "LIG손해보험"},
        {"code": "057050", "name": "코리안리"},
        {"code": "237350", "name": "교보라이프플래닛"}
    ]
}

DEFAULT_STATE = {
    "supervisor": {
        "status": "active",
        "current_task": "initializing",
        "progress": 0.0,
        "market_research_results": {},
        "stock_analysis_results": {},
        "geopolitical_analysis_results": {},  # 추가
        "report_draft": {}
    },
    "market_researcher": {
        "status": "idle",
        "assigned_task": "",
        "progress": 0.0,
        "results": {}
    },
    "stock_analyzer": {
        "status": "idle",
        "assigned_task": "",
        "progress": 0.0,
        "results": {}
    },
    "geopolitical_analyst": {  # 추가
        "status": "idle",
        "assigned_task": "",
        "progress": 0.0,
        "results": {}
    },
    "report_compiler": {
        "status": "idle",
        "assigned_task": "",
        "progress": 0.0,
        "report_draft": {}
    },
    "query": {
        "original_query": "",
        "processed_query": {},
        "has_geopolitical_component": False,  # 추가
        "has_trump_reference": False,  # 추가
    },
    "output": {
        "status": "not_started",
        "final_report": ""
    }
}