# tools/geopolitical_analyzer.py

import os
import json
from datetime import datetime
from pathlib import Path
import requests
from typing import Dict, List, Any

# config 모듈 임포트
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DATA_DIR
from promts.promts import (
    GEOPOLITICAL_ANALYSIS_PROMPT,
    INDUSTRY_IMPACT_PROMPT,
    INVESTMENT_STRATEGY_PROMPT
)

class GeopoliticalAnalyzer:
    """
    국제 정세가 금융 시장에 미치는 영향을 분석하는 클래스
    """
    
    def __init__(self):
        """초기화 메서드"""
        self.analysis_dir = DATA_DIR / "geopolitical_analysis"
        os.makedirs(self.analysis_dir, exist_ok=True)
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """LLM 초기화 - Langchain 또는 직접 OpenAI API 호출"""
        # 여기서는 간단히 구현. 실제로는 Langchain이나 직접 OpenAI API 연동 필요
        try:
            from langchain.llms import OpenAI
            return OpenAI(temperature=0.2)
        except ImportError:
            print("Langchain을 사용할 수 없습니다. 기본 요약 로직을 사용합니다.")
            return None
            
    def analyze_trump_impact(self) -> Dict[str, Any]:
        """
        트럼프 행정부의 정책이 한국 금융 시장에 미치는 영향 분석
        
        Returns:
            Dict[str, Any]: 분석 결과
        """
        print("트럼프 행정부의 정책이 한국 금융 시장에 미치는 영향 분석 중...")
        
        # LLM이 있으면 프롬프트 사용
        if self.llm:
            analysis = self.llm(GEOPOLITICAL_ANALYSIS_PROMPT)
        else:
            # 기본 분석 제공
            analysis = "트럼프 행정부의 정책은 한국 금융 시장에 다양한 영향을 미칠 것으로 예상됩니다..."
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.analysis_dir / f"trump_analysis_{timestamp}.txt"
        
        with open(results_file, "w", encoding="utf-8") as f:
            f.write(analysis)
        
        return {
            "analysis": analysis,
            "results_file": str(results_file)
        }
    
    def analyze_industry_impact(self, industry: str) -> Dict[str, Any]:
        """
        특정 산업에 대한 트럼프 정책 영향 분석
        
        Args:
            industry (str): 분석할 산업명 (예: 반도체, 자동차, 금융)
            
        Returns:
            Dict[str, Any]: 분석 결과
        """
        print(f"{industry} 산업에 대한 트럼프 정책 영향 분석 중...")
        
        # 프롬프트에 산업명 주입
        prompt = INDUSTRY_IMPACT_PROMPT.format(industry=industry)
        
        # LLM이 있으면 프롬프트 사용
        if self.llm:
            analysis = self.llm(prompt)
        else:
            # 기본 분석 제공
            analysis = f"트럼프 행정부의 정책은 {industry} 산업에 다양한 영향을 미칠 것으로 예상됩니다..."
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.analysis_dir / f"{industry}_impact_{timestamp}.txt"
        
        with open(results_file, "w", encoding="utf-8") as f:
            f.write(analysis)
        
        return {
            "industry": industry,
            "analysis": analysis,
            "results_file": str(results_file)
        }
    
    def generate_investment_strategy(self) -> Dict[str, Any]:
        """
        트럼프 정책 기조를 고려한 투자 전략 생성
        
        Returns:
            Dict[str, Any]: 투자 전략
        """
        print("트럼프 정책 기조를 고려한 투자 전략 생성 중...")
        
        # LLM이 있으면 프롬프트 사용
        if self.llm:
            strategy = self.llm(INVESTMENT_STRATEGY_PROMPT)
        else:
            # 기본 전략 제공
            strategy = "트럼프 행정부의 정책을 고려한 투자 전략은 다음과 같습니다..."
        
        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.analysis_dir / f"investment_strategy_{timestamp}.txt"
        
        with open(results_file, "w", encoding="utf-8") as f:
            f.write(strategy)
        
        return {
            "strategy": strategy,
            "results_file": str(results_file)
        }