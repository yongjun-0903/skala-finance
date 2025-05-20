# agents/supervisor.py

import os
import time
from copy import deepcopy
import json
from datetime import datetime
from pathlib import Path

from config import DEFAULT_STATE, OUTPUTS_DIR, REPORTS_DIR

class Supervisor:
    """
    전체 워크플로우를 조정하는 관리자 에이전트
    """
    
    def __init__(self):
        """초기화 메서드"""
        self.state = deepcopy(DEFAULT_STATE)
        self.state["supervisor"]["status"] = "active"
        self.state["supervisor"]["current_task"] = "initializing"
        self.state_history = []
        self._save_state()
    
    def _save_state(self):
        """현재 상태를 저장하고 상태 기록을 업데이트합니다."""
        self.state_history.append(deepcopy(self.state))
        
        # 상태를 JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        state_file = OUTPUTS_DIR / f"State_Definition{len(self.state_history)}.json"
        
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def assign_task(self, agent_name, task):
        """에이전트에 작업 할당"""
        self.state[agent_name]["status"] = "working"
        self.state[agent_name]["assigned_task"] = task
        self.state[agent_name]["progress"] = 0.0
        self.state["supervisor"]["current_task"] = f"supervising_{agent_name}"
        self._save_state()
        
        print(f"태스크 할당: {agent_name} -> {task}")
    
    def update_progress(self, agent_name, progress, results=None):
        """에이전트 진행 상황 업데이트"""
        self.state[agent_name]["progress"] = progress
        
        if results:
            if agent_name == "market_researcher":
                self.state["supervisor"]["market_research_results"].update(results)
            elif agent_name == "stock_analyzer":
                self.state["supervisor"]["stock_analysis_results"].update(results)
            elif agent_name == "report_compiler":
                self.state["supervisor"]["report_draft"].update(results)
        
        self._save_state()
    
    def complete_task(self, agent_name, results=None):
        """에이전트 작업 완료 처리"""
        self.state[agent_name]["status"] = "idle"
        self.state[agent_name]["progress"] = 1.0
        
        if results:
            if agent_name == "market_researcher":
                self.state["supervisor"]["market_research_results"].update(results)
            elif agent_name == "stock_analyzer":
                self.state["supervisor"]["stock_analysis_results"].update(results)
            elif agent_name == "report_compiler":
                self.state["supervisor"]["report_draft"].update(results)
                self.state["output"]["final_report"] = results.get("report_path", "")
        
        self._save_state()
        print(f"태스크 완료: {agent_name}")
    
    def process_query(self, query):
        """사용자 쿼리 처리"""
        self.state["query"]["original_query"] = query
        self._parse_query(query)
        self._save_state()
        
        print(f"쿼리 처리: {query}")
    
    def _parse_query(self, query):
        """쿼리 분석 및 처리 계획 수립"""
        # 간단한 키워드 기반 파싱
        query_lower = query.lower()
        parsed = {
            "market_analysis": False,
            "stock_analysis": False,
            "sector_analysis": False,
            "report_type": "pdf",
            "targets": []
        }
        
        # 키워드 검색
        if any(word in query_lower for word in ["시장", "트렌드", "동향", "추세"]):
            parsed["market_analysis"] = True
        
        if any(word in query_lower for word in ["주식", "종목", "기업", "회사"]):
            parsed["stock_analysis"] = True
        
        if any(word in query_lower for word in ["업종", "은행", "증권", "보험", "산업"]):
            parsed["sector_analysis"] = True
            
            # 업종 추출
            for sector in ["은행", "증권", "보험"]:
                if sector in query_lower:
                    parsed["targets"].append({"type": "sector", "name": sector})
        
        # 타겟 기업 추출 (TARGET_COMPANIES에서 검색)
        from config import TARGET_COMPANIES
        for sector, companies in TARGET_COMPANIES.items():
            for company in companies:
                if company['name'] in query:
                    parsed["targets"].append({
                        "type": "company", 
                        "name": company['name'], 
                        "code": company['code'],
                        "sector": sector
                    })
        
        self.state["query"]["processed_query"] = parsed
        print(f"쿼리 분석 결과: {parsed}")
    
    def run(self, market_researcher, stock_analyzer, geopolitical_analyst, report_compiler):
        try:
            # 상태 업데이트
            self.state["supervisor"]["status"] = "active"
            self.state["supervisor"]["current_task"] = "running_analysis"
            self.state["supervisor"]["progress"] = 0.1
            
            # 쿼리 데이터
            query_data = self.state["query"]["processed_query"]  # 올바른 경로
            
            # 1. 시장 조사
            self.state["supervisor"]["progress"] = 0.2
            market_research_results = market_researcher.analyze_market(query_data)
            self.state["supervisor"]["market_research_results"] = market_research_results
            
            # 2. 주식 분석
            self.state["supervisor"]["progress"] = 0.4
            stock_analysis_results = stock_analyzer.analyze_stocks(query_data, market_research_results)
            self.state["supervisor"]["stock_analysis_results"] = stock_analysis_results
            
            # 3. 국제 정세 분석 - 트럼프 언급이 있는 경우에만 수행
            if query_data.get("has_trump_reference", False) or query_data.get("geopolitical_analysis", False):
                self.state["supervisor"]["progress"] = 0.6
                geopolitical_analysis_results = geopolitical_analyst.analyze_geopolitics(query_data)
                self.state["supervisor"]["geopolitical_analysis_results"] = geopolitical_analysis_results
            else:
                geopolitical_analysis_results = {"analysis": "국제 정세 분석이 요청되지 않았습니다."}
                self.state["supervisor"]["geopolitical_analysis_results"] = geopolitical_analysis_results
            
            # 4. 보고서 생성
            self.state["supervisor"]["progress"] = 0.8
            output = report_compiler.generate_report(
                query_data,
                market_research_results,
                stock_analysis_results,
                geopolitical_analysis_results  # 파라미터 추가
            )
            
            self.state["output"] = {
                "status": "completed",
                "final_report": output.get("report_path", "")
            }
            
            # 완료 상태 업데이트
            self.state["supervisor"]["status"] = "completed"
            self.state["supervisor"]["current_task"] = "analysis_complete"
            self.state["supervisor"]["progress"] = 1.0
            
            return True
        except Exception as e:
            print(f"분석 실행 중 오류 발생: {str(e)}")
            self.state["error"] = str(e)
            self.state["supervisor"]["status"] = "error"
            return False