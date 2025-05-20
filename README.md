# SKALA Finance - 금융 시장 트렌드 분석 시스템

SKALA Finance는 한국 금융 시장 트렌드와 관련 기업들을 분석하고 종합적인 보고서를 생성하는 다중 에이전트 시스템입니다. 이 시스템은 마켓 리서치, 주식 분석, 국제 정세 분석을 통합하여 사용자 쿼리에 따른 맞춤형 금융 분석 보고서를 제공합니다.

## 주요 기능

* 시장 트렌드 분석: 최신 금융 시장 동향과 주요 이슈를 분석합니다.
* 업종 분석: 은행, 증권, 보험 등 주요 금융 업종의 트렌드와 기업 비교를 제공합니다.
* 기업 분석: 개별 기업의 기술적 분석, 재무 정보, 뉴스 등을 종합 분석합니다.
* 국제 정세 분석: 특히 트럼프 정책이 한국 금융 시장에 미치는 영향을 분석합니다.
* 보고서 생성: 분석 결과를 마크다운 또는 PDF 형식의 종합 보고서로 제공합니다.

## 시스템 구조

프로젝트는 다음과 같은 구조로 구성되어 있습니다:

```
skala-finance/
├── agents/                    # 다중 에이전트 시스템 구현
│   ├── supervisor.py          # 전체 에이전트 조정 및 워크플로우 관리
│   ├── market_researcher.py   # 시장 동향 분석 에이전트
│   ├── stock_analyzer.py      # 주식 분석 에이전트
│   ├── geopolitical_analyst.py # 국제 정세 분석 에이전트
│   └── report_compiler.py     # 분석 결과 종합 및 보고서 생성 에이전트
├── tools/                     # 분석 도구 모듈
│   ├── analyzer.py            # 기본 분석 도구
│   ├── stock_data.py          # 주식 데이터 수집 도구
│   ├── visualizer.py          # 데이터 시각화 도구
│   ├── rag_tools.py           # 검색 증강 도구
│   └── geopolitical_analyzer.py # 국제 정세 분석 도구
├── data/                      # 데이터 저장소
│   ├── market_reports/        # 시장 분석 보고서 데이터
│   ├── company_docs/          # 기업 문서 데이터
│   ├── geopolitical_analysis/ # 국제 정세 분석 데이터
│   └── web_cache/             # 웹 검색 결과 캐시
├── outputs/                   # 출력 결과물
│   ├── reports/               # 생성된 보고서
│   └── charts/                # 생성된 차트 이미지
├── promts/                    # 프롬프트 템플릿
├── config.py                  # 시스템 설정 및 환경 변수
├── app.py                     # 메인 애플리케이션
└── .env                       # 환경 변수 (API 키 등)
```

## 설치 및 사용 방법

### 필수 요구 사항

* Python 3.9 이상
* weasyprint==65.1
* OpenAI API 키 또는 호환 LLM API

### 설치

1. 저장소 클론
   ```bash
   git clone https://github.com/username/skala-finance.git
   cd skala-finance
   ```

2. 가상 환경 설정 및 패키지 설치
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 또는
   .venv\Scripts\activate     # Windows
   
   pip install -r requirements.txt
   ```

3. 환경 변수 설정
   `.env` 파일에 필요한 API 키 등을 설정합니다:
   ```
   OPENAI_API_KEY=your_openai_api_key
   MODEL_NAME=gpt-4o-mini
   ```

### 실행

터미널에서 다음 명령어로 애플리케이션을 실행합니다:
```bash
python app.py
```

## 사용 예시

실행 후 프롬프트가 표시되면 분석 쿼리를 입력합니다. 예를 들어:

- `금융시장 최근 트렌드 분석해줘`
- `KB금융지주와 신한지주 비교 분석`
- `트럼프 정책이 한국 은행 업종에 미치는 영향은?`
- `보험 업종 내 기업 성과 비교해줘`

## 개발 정보

- **언어**: Python
- **주요 라이브러리**:
  - 데이터 분석: pandas, numpy
  - 시각화: matplotlib, seaborn
  - 금융 데이터: FinanceDataReader
  - 웹 서치: tavliy
  - PDF 생성: weasyprint
  - 마크다운 변환: markdown
  - LLM 연동: openai

## 주의사항

- 이 시스템은 금융 투자 결정을 위한 전문적인 조언을 제공하지 않습니다.
- 분석 결과는 참고용으로만 사용해야 하며, 실제 투자 결정은 전문가와 상담하세요.
