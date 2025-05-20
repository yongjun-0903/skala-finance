# agents/geopolitical_analyst.py

import os
import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR
from tools.geopolitical_analyzer import GeopoliticalAnalyzer

class GeopoliticalAnalyst:
    """
    국제 정세 분석을 담당하는 에이전트
    """
    
    def __init__(self):
        """초기화 메서드"""
        self.geopolitical_analyzer = GeopoliticalAnalyzer()
        self.analysis_dir = DATA_DIR / "geopolitical_results"
        os.makedirs(self.analysis_dir, exist_ok=True)
        self.state = {
            "status": "idle",
            "assigned_task": "",
            "progress": 0.0,
            "results": {}
        }
    
    def analyze_geopolitics(self, query_data):
        """
        국제 정세 분석 수행
        
        Args:
            query_data (dict): 처리된 쿼리 데이터
            
        Returns:
            dict: 국제 정세 분석 결과
        """
        # 상태 업데이트
        self.state["status"] = "running"
        self.state["assigned_task"] = "geopolitical_analysis"
        self.state["progress"] = 0.1
        
        print("국제 정세 분석 수행 중...")
        results = {}
        
        # 트럼프와 관세 영향 분석
        if query_data.get("geopolitical_analysis", False) or "트럼프" or "관세" in query_data.get("raw_query", "").lower():
            self.state["progress"] = 0.3
            trump_impact = self.geopolitical_analyzer.analyze_trump_impact()
            results["trump_impact"] = trump_impact
            
            # 산업별 영향 분석
            self.state["progress"] = 0.5
            industry_impacts = {}
            key_industries = ["금융", "은행", "증권", "보험", "핀테크", "자산운용"]
            
            for industry in key_industries:
                if industry.lower() in query_data.get("raw_query", "").lower():
                    industry_impact = self.geopolitical_analyzer.analyze_industry_impact(industry)
                    industry_impacts[industry] = industry_impact
            
            # 쿼리에 특정 금융권 주요 산업 분석
            if not industry_impacts and query_data.get("general_analysis", False):
                for industry in ["은행", "증권", "보험"]:
                    industry_impact = self.geopolitical_analyzer.analyze_industry_impact(industry)
                    industry_impacts[industry] = industry_impact
            
            results["industry_impacts"] = industry_impacts
            
            # 투자 전략 생성
            self.state["progress"] = 0.8
            if query_data.get("investment_strategy", False) or "전략" in query_data.get("raw_query", "").lower():
                investment_strategy = self.geopolitical_analyzer.generate_investment_strategy()
                results["investment_strategy"] = investment_strategy
        
        # 결과를 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.analysis_dir / f"geopolitical_analysis_results_{timestamp}.json"
        
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        results["results_file"] = str(results_file)
        print(f"국제 정세 분석 완료. 결과 저장 위치: {results_file}")
        
        # 상태 업데이트
        self.state["status"] = "completed"
        self.state["progress"] = 1.0
        self.state["results"] = results
        
        return results