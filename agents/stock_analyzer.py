# agents/stock_analyzer.py 수정

import os
import json
import numpy as np
from datetime import datetime
from pathlib import Path

from config import DATA_DIR, TARGET_COMPANIES
from tools.stock_data import StockDataFetcher
from tools.analyzer import StockAnalyzer as TechnicalAnalyzer  # 이름 변경
from tools.rag_tools import CompanyAnalyzer

class StockAnalyzer:
    """
    주식 분석을 담당하는 에이전트
    """
    
    def __init__(self):
        """초기화 메서드"""
        self.stock_fetcher = StockDataFetcher()
        self.technical_analyzer = TechnicalAnalyzer()  # 이름 변경
        self.company_analyzer = CompanyAnalyzer()
        self.analysis_dir = DATA_DIR / "analysis_results"
        os.makedirs(self.analysis_dir, exist_ok=True)
        # 상태 정보 추가
        self.state = {
            "status": "idle",
            "assigned_task": "",
            "progress": 0.0,
            "results": {}
        }
    
    def analyze_stocks(self, query_data, market_research_results=None):
        """
        주식 분석 수행
        
        Args:
            query_data (dict): 처리된 쿼리 데이터
            market_research_results (dict): 시장 분석 결과 (옵션)
            
        Returns:
            dict: 주식 분석 결과
        """
        # 상태 업데이트
        self.state["status"] = "running"
        self.state["assigned_task"] = "stock_analysis"
        self.state["progress"] = 0.1
        
        print("주식 분석 수행 중...")
        results = {}
        
        # 타겟 기업 분석
        if query_data.get("stock_analysis", False):
            self.state["progress"] = 0.3
            company_results = {}
            
            # 쿼리에서 타겟 추출
            targets = query_data.get("targets", [])
            companies_to_analyze = []
            
            for target in targets:
                if target["type"] == "company":
                    companies_to_analyze.append({
                        "code": target["code"],
                        "name": target["name"]
                    })
            
            # 타겟이 없는 경우 기본 기업 분석
            if not companies_to_analyze and query_data.get("stock_analysis", False):
                # 기본 분석 대상: 각 업종의 대표 기업
                for sector, companies in TARGET_COMPANIES.items():
                    if companies:
                        companies_to_analyze.append({
                            "code": companies[0]["code"],
                            "name": companies[0]["name"]
                        })
            
            # 기업 분석 수행
            total_companies = len(companies_to_analyze)
            for i, company in enumerate(companies_to_analyze):
                # 상태 업데이트 - 기업 분석 진행도
                self.state["progress"] = 0.3 + (0.4 * (i / total_companies))
                
                code = company["code"]
                name = company["name"]
                
                # RAG를 통한 기업 정보 분석
                company_info = self.company_analyzer.analyze_company(code, name)
                
                # 기술적 분석
                data = self.stock_fetcher.get_stock_data(code)
                technical_analysis = self.technical_analyzer.full_analysis(code, name)  # 이름 변경된 메소드 사용
                
                company_results[code] = {
                    "company_info": company_info,
                    "technical_analysis": technical_analysis
                }
            
            results["company_analysis"] = company_results
        
        # 업종 분석이 필요한 경우 - 업종 내 기업 비교
        if query_data.get("sector_analysis", False):
            self.state["progress"] = 0.7
            sector_comparison = {}
            
            for target in query_data.get("targets", []):
                if target["type"] == "sector":
                    sector_name = target["name"]
                    
                    if sector_name in TARGET_COMPANIES:
                        company_codes = [company["code"] for company in TARGET_COMPANIES[sector_name][:5]]
                        comparison = self.company_analyzer.compare_companies(company_codes, sector_name)
                        
                        # 성과 비교
                        company_names = [company["name"] for company in TARGET_COMPANIES[sector_name][:5]]
                        performance = self.stock_fetcher.compare_performance(company_codes, company_names)
                        
                        # 수정 후
                        sector_comparison[sector_name] = {
                            "qualitative_comparison": comparison,
                            "performance_data": performance.to_dict(orient='records') if not performance.empty else {}
                        }
            
            results["sector_comparison"] = sector_comparison
        
        # 결과를 파일로 저장
        self.state["progress"] = 0.9
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.analysis_dir / f"stock_analysis_results_{timestamp}.json"
        
        def numpy_encoder(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.bool_)):
                return bool(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=numpy_encoder)
        
        results["results_file"] = str(results_file)
        print(f"주식 분석 완료. 결과 저장 위치: {results_file}")
        
        # 상태 업데이트
        self.state["status"] = "completed"
        self.state["progress"] = 1.0
        self.state["results"] = results
        
        return results