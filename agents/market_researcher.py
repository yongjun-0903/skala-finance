# agents/market_researcher.py

import os
import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR, MARKET_REPORTS_DIR
from tools.rag_tools import MarketTrendAnalyzer, FinancialRagToolkit

class MarketResearcher:
    """
    시장 트렌드 분석을 담당하는 에이전트
    """
    
    def __init__(self):
        """초기화 메서드"""
        self.trend_analyzer = MarketTrendAnalyzer()
        self.rag_toolkit = FinancialRagToolkit()
        self.reports_dir = MARKET_REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def analyze_market(self, query_data):
        """
        시장 분석 수행
        
        Args:
            query_data (dict): 처리된 쿼리 데이터
            
        Returns:
            dict: 시장 분석 결과
        """
        print("시장 분석 수행 중...")
        results = {}
        
        # 시장 분석이 필요한 경우
        if query_data.get("market_analysis", False):
            market_trend = self.trend_analyzer.analyze_market_trend("금융시장")
            results["market_trend"] = market_trend
        
        # 업종 분석이 필요한 경우
        if query_data.get("sector_analysis", False):
            sector_results = {}
            
            # 타겟 업종 분석
            for target in query_data.get("targets", []):
                if target["type"] == "sector":
                    sector_name = target["name"]
                    sector_trend = self.trend_analyzer.analyze_sector_trend(sector_name)
                    sector_results[sector_name] = sector_trend
            
            # 타겟이 없는 경우 기본 업종 분석
            if not sector_results and query_data.get("sector_analysis", False):
                # 기본 업종 (은행, 증권, 보험) 분석
                for sector in ["은행", "증권", "보험"]:
                    sector_trend = self.trend_analyzer.analyze_sector_trend(sector)
                    sector_results[sector] = sector_trend
            
            results["sector_trends"] = sector_results
        
        # 테마 분석
        if "테마" in query_data.get("original_query", "").lower():
            themes = []
            if "AI" in query_data.get("original_query", "").upper() or "인공지능" in query_data.get("original_query", ""):
                themes.append("AI")
            if "빅데이터" in query_data.get("original_query", ""):
                themes.append("빅데이터")
            if "핀테크" in query_data.get("original_query", ""):
                themes.append("핀테크")
            
            if not themes:
                themes = ["핀테크", "AI"]  # 기본 테마
            
            theme_results = {}
            for theme in themes:
                theme_analysis = self.rag_toolkit.analyze_investment_theme(theme)
                theme_results[theme] = theme_analysis
            
            results["theme_analysis"] = theme_results
        
        # 최신 이벤트 검색
        current_events = self.rag_toolkit.fetch_current_events("금융시장")
        results["current_events"] = current_events
        
        # 결과를 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.reports_dir / f"market_research_results_{timestamp}.json"
        
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        results["results_file"] = str(results_file)
        print(f"시장 분석 완료. 결과 저장 위치: {results_file}")
        
        return results