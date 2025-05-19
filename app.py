# app.py

import os
import sys
from datetime import datetime
from pathlib import Path

# config 모듈 임포트
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUTS_DIR, REPORTS_DIR, CHARTS_DIR
from agents.supervisor import Supervisor
from agents.market_researcher import MarketResearcher
from agents.stock_analyzer import StockAnalyzer
from agents.report_compiler import ReportCompiler
from agents.geopolitical_analyst import GeopoliticalAnalyst


def setup_environment():
    """환경 설정 및 필요한 디렉토리 생성"""
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(CHARTS_DIR, exist_ok=True)


def run_analysis(query, output_format="markdown"):
    """
    분석 수행

    Args:
        query (str): 사용자 쿼리
        output_format (str): 출력 형식 ('markdown', 'pdf')

    Returns:
        bool: 성공 여부
    """
    print(f"분석 시작: '{query}'")
    print("=" * 50)

    # 에이전트 초기화
    supervisor = Supervisor()
    market_researcher = MarketResearcher()
    stock_analyzer = StockAnalyzer()
    report_compiler = ReportCompiler()
    geopolitical_analyst = GeopoliticalAnalyst()

    # 쿼리 처리
    supervisor.process_query(query)

    # 트럼프 관련 쿼리 확인
    has_trump_component = (
        "트럼프" in query.lower()
        or "대통령" in query.lower()
        or "미국" in query.lower()
    )
    supervisor.state["query"]["processed_query"][
        "has_trump_reference"
    ] = has_trump_component
    supervisor.state["query"]["processed_query"][
        "geopolitical_analysis"
    ] = has_trump_component

    # PDF 출력 여부에 따라 다른 워크플로우 실행
    if output_format.lower() == 'pdf':
        try:
            # 각 단계별 분석 실행
            print("시장 분석 수행 중...")
            market_research_results = market_researcher.analyze_market(supervisor.state["query"]["processed_query"])
            
            print("주식 분석 수행 중...")
            stock_analysis_results = stock_analyzer.analyze_stocks(supervisor.state["query"]["processed_query"], market_research_results)
            
            if has_trump_component:
                print("국제 정세 분석 수행 중...")
                geopolitical_analysis_results = geopolitical_analyst.analyze_geopolitics(supervisor.state["query"]["processed_query"])
            else:
                geopolitical_analysis_results = None
            
            print("PDF 보고서 생성 중...")
            output = report_compiler.generate_pdf_report(
                supervisor.state["query"]["processed_query"],
                market_research_results,
                stock_analysis_results,
                geopolitical_analysis_results
            )
            
            if "pdf_path" in output:
                supervisor.state["output"] = {
                    "status": "completed",
                    "final_report": output["pdf_path"]
                }
                success = True
            else:
                # PDF 생성 실패 시 마크다운 경로 사용
                supervisor.state["output"] = {
                    "status": "completed",
                    "final_report": output["report_path"]
                }
                success = True
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {str(e)}")
            # 오류 발생 시 기본 워크플로우로 진행
            success = supervisor.run(
                market_researcher, 
                stock_analyzer, 
                geopolitical_analyst,
                report_compiler
            )
    else:
        # 기존 워크플로우 실행
        success = supervisor.run(
            market_researcher, 
            stock_analyzer, 
            geopolitical_analyst,
            report_compiler
        )

    if success:
        print("=" * 50)
        print("분석이 성공적으로 완료되었습니다.")
        print(f"보고서 위치: {supervisor.state['output']['final_report']}")
    else:
        print("=" * 50)
        print("분석 중 오류가 발생했습니다.")

    return success


def main():
    """메인 함수"""
    setup_environment()

    print("=" * 50)
    print("금융 시장 트렌드 분석 시스템")
    print("=" * 50)
    print("이 시스템은 금융 시장 트렌드와 관련 기업을 분석합니다.")
    print("예시 쿼리:")
    print("- '금융시장 최근 트렌드 분석해줘'")
    print("- '은행 업종 분석 및 KB금융 기업 분석'")
    print("- '삼성전자와 SK하이닉스 비교 분석'")
    print("=" * 50)

    # 출력 형식 선택
    print("출력 형식을 선택하세요:")
    print("1. 마크다운 (md)")
    print("2. PDF")
    format_choice = input("선택 (1 또는 2): ")

    output_format = "markdown"  # 기본값
    if format_choice == "2":
        output_format = "pdf"
        print("PDF 형식으로 보고서가 생성됩니다.")
    else:
        print("마크다운 형식으로 보고서가 생성됩니다.")

    while True:
        query = input("분석 쿼리를 입력하세요 (종료: 'q'): ")

        if query.lower() in ["q", "quit", "exit"]:
            print("프로그램을 종료합니다.")
            break

        if not query or len(query) < 5:
            print("유효한 쿼리를 입력해주세요.")
            continue

        # 분석 실행 (출력 형식 전달)
        run_analysis(query, output_format)
        print("\n새로운 분석을 시작하려면 새 쿼리를 입력하세요.\n")


if __name__ == "__main__":
    main()
