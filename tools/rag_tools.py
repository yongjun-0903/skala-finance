# tools/rag_tools.py

import os
import sys
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# config 모듈 임포트
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_DIR, MARKET_REPORTS_DIR, COMPANY_DOCS_DIR, TARGET_COMPANIES

# 필요한 디렉토리 생성
os.makedirs(MARKET_REPORTS_DIR, exist_ok=True)
os.makedirs(COMPANY_DOCS_DIR, exist_ok=True)


class TavilySearchTool:
    """Tavily API를 사용하여 웹 검색을 수행하는 클래스"""
    
    def __init__(self, api_key=None):
        """
        Tavily 검색 도구 초기화
        
        Args:
            api_key (str): Tavily API 키. 없으면 환경 변수에서 가져옵니다.
        """
        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")
        
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
        
        # 에러 메시지 설정
        if not self.api_key:
            print("경고: Tavily API 키가 설정되지 않았습니다. 환경 변수 TAVILY_API_KEY를 설정하세요.")

    def search(self, query: str, max_results: int = 5, search_depth: str = "basic") -> List[Dict]:
        """
        Tavily API를 사용하여 웹 검색 수행
        
        Args:
            query (str): 검색 쿼리
            max_results (int): 반환할 최대 결과 수
            search_depth (str): 검색 깊이 ("basic" 또는 "advanced")
            
        Returns:
            List[Dict]: 검색 결과 목록
        """
        if not self.api_key:
            print("오류: Tavily API 키가 없습니다. 환경 변수 TAVILY_API_KEY를 설정하세요.")
            return []
        
        # 한국 금융 사이트 포함
        include_domains = [
            # 글로벌 금융 사이트
            "finance.yahoo.com", "bloomberg.com", "cnbc.com", "ft.com", 
            "wsj.com", "reuters.com", "investing.com", "marketwatch.com",
            
            # 한국 금융 사이트
            "finance.naver.com", "stock.naver.com", "hankyung.com", "mk.co.kr",
            "edaily.co.kr", "sedaily.com", "fnnews.com", "fnguide.com", 
            "infostock.co.kr", "investing.kr", "paxnet.co.kr", "cbs.co.kr",
            "news.naver.com", "news.daum.net", "thebell.co.kr"
        ]
        
        # Tavily API 요청 파라미터
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_domains": include_domains
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.base_url, json=payload, headers=headers)
            response.raise_for_status()  # HTTP 오류 체크
            result_data = response.json()
            
            # API 응답 형식에 따라 결과 추출
            if "results" in result_data:
                return result_data["results"]
            return []
            
        except Exception as e:
            print(f"Tavily API 호출 중 오류 발생: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"응답 내용: {e.response.text}")
            return []


class MarketTrendAnalyzer:
    """금융 시장 트렌드 분석 도구"""
    
    def __init__(self):
        """Market Trend Analyzer 초기화"""
        self.search_tool = TavilySearchTool()
        self.reports_dir = MARKET_REPORTS_DIR
        
    def analyze_market_trend(self, market_type: str = "금융시장", days: int = 7) -> Dict[str, Any]:
        """
        금융 시장 트렌드 분석
        
        Args:
            market_type (str): 시장 유형 (예: "금융시장", "주식시장", "채권시장")
            days (int): 검색할 기간(일)
            
        Returns:
            Dict[str, Any]: 시장 트렌드 분석 결과
        """
        print(f"{market_type} 트렌드 분석 중...")
        
        # 시장 동향 검색
        trend_query = f"{market_type} 최근 동향 분석"
        trend_results = self.search_tool.search(trend_query, max_results=5)
        
        # 키워드 검색
        keyword_query = f"{market_type} 주요 이슈 키워드"
        keyword_results = self.search_tool.search(keyword_query, max_results=3)
        
        # 전문가 전망 검색
        forecast_query = f"{market_type} 전문가 전망 분석"
        forecast_results = self.search_tool.search(forecast_query, max_results=3)
        
        # 결과 취합
        result = {
            "시장유형": market_type,
            "분석일자": datetime.now().strftime("%Y-%m-%d"),
            "검색기간": f"{days}일",
            "시장동향": {
                "검색쿼리": trend_query,
                "결과": trend_results
            },
            "주요이슈": {
                "검색쿼리": keyword_query,
                "결과": keyword_results
            },
            "전문가전망": {
                "검색쿼리": forecast_query,
                "결과": forecast_results
            }
        }
        
        # 결과 저장
        self._save_trend_analysis(result, market_type)
        
        return result
    
    def analyze_sector_trend(self, sector: str) -> Dict[str, Any]:
        """
        특정 업종의 트렌드 분석
        
        Args:
            sector (str): 업종명 (예: "은행", "증권", "보험")
            
        Returns:
            Dict[str, Any]: 업종 트렌드 분석 결과
        """
        print(f"{sector} 업종 트렌드 분석 중...")
        
        # 업종 동향 검색
        trend_query = f"{sector} 업종 최근 동향 분석"
        trend_results = self.search_tool.search(trend_query, max_results=5)
        
        # 업종 내 주요 기업 검색
        if sector in TARGET_COMPANIES:
            companies = [company['name'] for company in TARGET_COMPANIES[sector][:5]]
            companies_str = ", ".join(companies)
            companies_query = f"{companies_str} 기업 최근 소식"
            companies_results = self.search_tool.search(companies_query, max_results=5)
        else:
            companies_query = f"{sector} 주요 기업 최근 소식"
            companies_results = self.search_tool.search(companies_query, max_results=5)
        
        # 업종 투자 전망 검색
        forecast_query = f"{sector} 업종 투자 전망"
        forecast_results = self.search_tool.search(forecast_query, max_results=3)
        
        # 결과 취합
        result = {
            "업종": sector,
            "분석일자": datetime.now().strftime("%Y-%m-%d"),
            "업종동향": {
                "검색쿼리": trend_query,
                "결과": trend_results
            },
            "주요기업소식": {
                "검색쿼리": companies_query,
                "결과": companies_results
            },
            "투자전망": {
                "검색쿼리": forecast_query,
                "결과": forecast_results
            }
        }
        
        # 결과 저장
        self._save_trend_analysis(result, f"{sector}_업종")
        
        return result
    
    def _save_trend_analysis(self, result: Dict[str, Any], prefix: str) -> str:
        """
        트렌드 분석 결과를 파일로 저장
        
        Args:
            result (Dict[str, Any]): 분석 결과
            prefix (str): 파일명 접두사
            
        Returns:
            str: 저장된 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_트렌드분석_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"분석 결과가 {filepath}에 저장되었습니다.")
        return filepath


class CompanyAnalyzer:
    """기업 분석 도구"""
    
    def __init__(self):
        """Company Analyzer 초기화"""
        self.search_tool = TavilySearchTool()
        self.company_docs_dir = COMPANY_DOCS_DIR
    
    def analyze_company(self, code: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        기업 정보 및 사업 방향 분석
        
        Args:
            code (str): 종목 코드
            name (str, optional): 기업명. 없으면 TARGET_COMPANIES에서 검색
            
        Returns:
            Dict[str, Any]: 기업 분석 결과
        """
        # 기업명 검색
        sector_name = "미분류"
        if not name:
            for sector, companies in TARGET_COMPANIES.items():
                for company in companies:
                    if company['code'] == code:
                        name = company['name']
                        sector_name = sector
                        break
                if name:
                    break
        
        if not name:
            name = f"종목({code})"
        
        print(f"{name} 기업 분석 중...")
        
        # 기업 정보 검색
        info_query = f"{name} 기업 개요 사업영역"
        info_results = self.search_tool.search(info_query, max_results=3)
        
        # 최근 뉴스 검색
        news_query = f"{name} 최근 뉴스 소식"
        news_results = self.search_tool.search(news_query, max_results=5)
        
        # 재무 정보 검색
        financial_query = f"{name} 재무제표 실적"
        financial_results = self.search_tool.search(financial_query, max_results=3)
        
        # 투자 의견 검색
        investment_query = f"{name} 주식 투자의견 목표가"
        investment_results = self.search_tool.search(investment_query, max_results=3)
        
        # 사업 전략 검색
        strategy_query = f"{name} 사업 전략 방향"
        strategy_results = self.search_tool.search(strategy_query, max_results=3)
        
        # 결과 취합
        result = {
            "기업코드": code,
            "기업명": name,
            "업종": sector_name,
            "분석일자": datetime.now().strftime("%Y-%m-%d"),
            "기업정보": {
                "검색쿼리": info_query,
                "결과": info_results
            },
            "최근뉴스": {
                "검색쿼리": news_query,
                "결과": news_results
            },
            "재무정보": {
                "검색쿼리": financial_query,
                "결과": financial_results
            },
            "투자의견": {
                "검색쿼리": investment_query,
                "결과": investment_results
            },
            "사업전략": {
                "검색쿼리": strategy_query,
                "결과": strategy_results
            }
        }
        
        # 결과 저장
        self._save_company_analysis(result)
        
        return result
    
    def compare_companies(self, company_codes: List[str], sector: Optional[str] = None) -> Dict[str, Any]:
        """
        여러 기업 비교 분석
        
        Args:
            company_codes (List[str]): 비교할 기업 코드 리스트
            sector (str, optional): 업종명. 없으면 개별적으로 검색
            
        Returns:
            Dict[str, Any]: 기업 비교 분석 결과
        """
        # 기업명 리스트 생성
        companies = []
        for code in company_codes:
            name = None
            company_sector = sector
            
            if not sector:
                for s, company_list in TARGET_COMPANIES.items():
                    for company in company_list:
                        if company['code'] == code:
                            name = company['name']
                            company_sector = s
                            break
                    if name:
                        break
            
            if not name:
                if sector:
                    for company in TARGET_COMPANIES.get(sector, []):
                        if company['code'] == code:
                            name = company['name']
                            break
                
                if not name:
                    name = f"종목({code})"
            
            companies.append({
                "code": code,
                "name": name,
                "sector": company_sector or "미분류"
            })
        
        # 기업명 문자열 생성
        companies_str = ", ".join([company['name'] for company in companies])
        print(f"기업 비교 분석 중: {companies_str}")
        
        # 기업 비교 검색
        comparison_query = f"{companies_str} 기업 비교 분석"
        comparison_results = self.search_tool.search(comparison_query, max_results=5)
        
        # 업종 내 경쟁력 검색
        if sector:
            competition_query = f"{sector} 업종 내 {companies_str} 경쟁력 비교"
        else:
            competition_query = f"{companies_str} 기업 경쟁력 비교"
        competition_results = self.search_tool.search(competition_query, max_results=3)
        
        # 투자 매력도 검색
        investment_query = f"{companies_str} 투자 매력도 비교"
        investment_results = self.search_tool.search(investment_query, max_results=3)
        
        # 결과 취합
        result = {
            "비교기업": companies,
            "분석일자": datetime.now().strftime("%Y-%m-%d"),
            "업종": sector or "복합업종",
            "비교분석": {
                "검색쿼리": comparison_query,
                "결과": comparison_results
            },
            "경쟁력비교": {
                "검색쿼리": competition_query,
                "결과": competition_results
            },
            "투자매력도": {
                "검색쿼리": investment_query,
                "결과": investment_results
            }
        }
        
        # 결과 저장
        filename = f"기업비교분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.company_docs_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"비교 분석 결과가 {filepath}에 저장되었습니다.")
        return result
    
    def _save_company_analysis(self, result: Dict[str, Any]) -> str:
        """
        기업 분석 결과를 파일로 저장
        
        Args:
            result (Dict[str, Any]): 분석 결과
            
        Returns:
            str: 저장된 파일 경로
        """
        code = result["기업코드"]
        name = result["기업명"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{code}_{name}_분석_{timestamp}.json"
        filepath = os.path.join(self.company_docs_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"기업 분석 결과가 {filepath}에 저장되었습니다.")
        return filepath


class FinancialRagToolkit:
    """금융 RAG 종합 툴킷"""
    
    def __init__(self):
        """Financial RAG Toolkit 초기화"""
        self.market_analyzer = MarketTrendAnalyzer()
        self.company_analyzer = CompanyAnalyzer()
        self.search_tool = TavilySearchTool()
    
    def search_financial_info(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        금융 정보 검색
        
        Args:
            query (str): 검색어
            max_results (int): 최대 결과 수
            
        Returns:
            List[Dict]: 검색 결과
        """
        print(f"금융 정보 검색 중: '{query}'")
        results = self.search_tool.search(query, max_results=max_results)
        return results
    
    def analyze_investment_theme(self, theme: str) -> Dict[str, Any]:
        """
        투자 테마 분석
        
        Args:
            theme (str): 투자 테마 (예: "AI", "친환경", "바이오")
            
        Returns:
            Dict[str, Any]: 테마 분석 결과
        """
        print(f"'{theme}' 투자 테마 분석 중...")
        
        # 테마 개요 검색
        overview_query = f"{theme} 투자 테마 개요"
        overview_results = self.search_tool.search(overview_query, max_results=3)
        
        # 관련 기업 검색
        companies_query = f"{theme} 관련 주요 기업"
        companies_results = self.search_tool.search(companies_query, max_results=5)
        
        # 시장 전망 검색
        forecast_query = f"{theme} 투자 테마 전망"
        forecast_results = self.search_tool.search(forecast_query, max_results=3)
        
        # 투자 전략 검색
        strategy_query = f"{theme} 테마 투자 전략"
        strategy_results = self.search_tool.search(strategy_query, max_results=3)
        
        # 결과 취합
        result = {
            "투자테마": theme,
            "분석일자": datetime.now().strftime("%Y-%m-%d"),
            "테마개요": {
                "검색쿼리": overview_query,
                "결과": overview_results
            },
            "관련기업": {
                "검색쿼리": companies_query,
                "결과": companies_results
            },
            "시장전망": {
                "검색쿼리": forecast_query,
                "결과": forecast_results
            },
            "투자전략": {
                "검색쿼리": strategy_query,
                "결과": strategy_results
            }
        }
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{theme}_테마분석_{timestamp}.json"
        filepath = os.path.join(MARKET_REPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"테마 분석 결과가 {filepath}에 저장되었습니다.")
        return result
    
    def fetch_current_events(self, category: str = "금융", max_results: int = 5) -> List[Dict]:
        """
        최신 금융 이벤트 검색
        
        Args:
            category (str): 검색 카테고리 (예: "금융", "경제", "주식")
            max_results (int): 최대 결과 수
            
        Returns:
            List[Dict]: 검색 결과
        """
        query = f"{category} 최신 뉴스 오늘"
        print(f"{category} 최신 이벤트 검색 중...")
        
        results = self.search_tool.search(query, max_results=max_results)
        return results
    
    def generate_financial_report(self, topic: str) -> Dict[str, Any]:
        """
        금융 보고서 생성
        
        Args:
            topic (str): 보고서 주제
            
        Returns:
            Dict[str, Any]: 생성된 보고서
        """
        print(f"'{topic}' 금융 보고서 생성 중...")
        
        # 주제 개요 검색
        overview_query = f"{topic} 개요 설명"
        overview_results = self.search_tool.search(overview_query, max_results=3)
        
        # 주요 정보 검색
        main_query = f"{topic} 중요 정보 분석"
        main_results = self.search_tool.search(main_query, max_results=5)
        
        # 전문가 의견 검색
        expert_query = f"{topic} 전문가 의견"
        expert_results = self.search_tool.search(expert_query, max_results=3)
        
        # 결론 및 권장사항 검색
        conclusion_query = f"{topic} 결론 전망"
        conclusion_results = self.search_tool.search(conclusion_query, max_results=2)
        
        # 결과 취합
        report = {
            "제목": f"{topic} 금융 보고서",
            "작성일": datetime.now().strftime("%Y-%m-%d"),
            "개요": {
                "검색쿼리": overview_query,
                "결과": overview_results
            },
            "주요정보": {
                "검색쿼리": main_query,
                "결과": main_results
            },
            "전문가의견": {
                "검색쿼리": expert_query,
                "결과": expert_results
            },
            "결론": {
                "검색쿼리": conclusion_query,
                "결과": conclusion_results
            }
        }
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{topic}_보고서_{timestamp}.json"
        filepath = os.path.join(MARKET_REPORTS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"금융 보고서가 {filepath}에 저장되었습니다.")
        return report


# # 테스트 코드
# if __name__ == "__main__":
#     # RAG 툴킷 생성
#     toolkit = FinancialRagToolkit()
    
#     # API 키 설정 확인
#     if not os.getenv("TAVILY_API_KEY"):
#         print("경고: TAVILY_API_KEY 환경 변수가 설정되지 않았습니다. API 호출이 실패할 수 있습니다.")
#         print("예시: export TAVILY_API_KEY='your_api_key'")
    
#     # 기본 검색 테스트
#     print("\n===== 기본 검색 테스트 =====")
#     search_results = toolkit.search_financial_info("KB금융 최근 실적", max_results=3)
#     if search_results:
#         print(f"검색 결과: {len(search_results)}개 항목 찾음")
#         for idx, result in enumerate(search_results, 1):
#             print(f"{idx}. 제목: {result.get('title', '제목 없음')}")
#             print(f"   URL: {result.get('url', 'URL 없음')}")
#             print(f"   내용 일부: {result.get('content', '내용 없음')[:100]}...")
#             print("-" * 50)
#     else:
#         print("검색 결과가 없거나 API 호출에 실패했습니다.")
    
#     print("\n테스트 완료!")