# agents/report_compiler.py

import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import tempfile
import shutil

from config import OUTPUTS_DIR, REPORTS_DIR, CHARTS_DIR
from tools.visualizer import StockVisualizer

class ReportCompiler:
    """
    분석 결과를 종합하여 보고서를 생성하는 에이전트
    """
    
    def __init__(self):
        """초기화 메서드"""
        self.reports_dir = REPORTS_DIR
        self.charts_dir = CHARTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.charts_dir, exist_ok=True)
        self.visualizer = StockVisualizer()
        # 상태 정보 추가
        self.state = {
            "status": "idle",
            "assigned_task": "",
            "progress": 0.0,
            "report_draft": {}
        }
    
    def generate_report(self, query_data, market_research_results, stock_analysis_results, geopolitical_analysis_results=None):
        """
        보고서 생성
        
        Args:
            query_data (dict): 처리된 쿼리 데이터
            market_research_results (dict): 시장 분석 결과
            stock_analysis_results (dict): 주식 분석 결과
            geopolitical_analysis_results (dict, optional): 국제 정세 분석 결과
            
        Returns:
            dict: 보고서 결과
        """
        # 상태 업데이트
        self.state["status"] = "running"
        self.state["assigned_task"] = "generate_report"
        self.state["progress"] = 0.1
        
        print("보고서 생성 중...")
        results = {}
        
        # 보고서 제목 및 기본 정보
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_title = "금융시장 분석 보고서"
        
        if query_data.get("sector_analysis", False) and query_data.get("targets"):
            sectors = [target["name"] for target in query_data.get("targets", []) if target["type"] == "sector"]
            if sectors:
                report_title = f"{', '.join(sectors)} 업종 분석 보고서"
        
        if query_data.get("stock_analysis", False) and query_data.get("targets"):
            companies = [target["name"] for target in query_data.get("targets", []) if target["type"] == "company"]
            if companies:
                report_title = f"{', '.join(companies)} 기업 분석 보고서"
        
        # 트럼프 관련 분석이 있는 경우 제목 수정
        if query_data.get("has_trump_reference", False) or (geopolitical_analysis_results and geopolitical_analysis_results.get("trump_impact")):
            report_title = f"트럼프 정책과 {report_title}"
        
        # 보고서 목차 업데이트 - 국제 정세 분석 추가
        report_sections = ["개요", "시장 동향", "업종 분석", "기업 분석"]
        
        # 국제 정세 분석이 있으면 목차에 추가
        if geopolitical_analysis_results and geopolitical_analysis_results.get("trump_impact"):
            report_sections.append("국제 정세 분석")
        
        report_sections.extend(["투자 전략", "결론"])
        
        # 보고서 객체 생성
        report = {
            "제목": report_title,
            "작성일": datetime.now().strftime("%Y-%m-%d"),
            "목차": report_sections,
            "내용": {}
        }
        
        # 상태 업데이트
        self.state["progress"] = 0.2
        
        # 1. 개요
        report["내용"]["개요"] = {
            "분석 목적": f"본 보고서는 {report_title}을 위해 작성되었습니다.",
            "분석 방법": "시장 데이터 분석, 기술적 분석, 웹 기반 리서치를 활용하여 분석을 수행했습니다.",
            "주요 결과": []  # 주요 결과는 나중에 채움
        }
        
        # 2. 시장 동향
        self.state["progress"] = 0.3
        if market_research_results.get("market_trend"):
            market_trend = market_research_results["market_trend"]
            report["내용"]["시장 동향"] = {
                "최근 동향": self._extract_market_insights(market_trend.get("시장동향", {}).get("결과", [])),
                "주요 이슈": self._extract_market_insights(market_trend.get("주요이슈", {}).get("결과", [])),
                "전문가 전망": self._extract_market_insights(market_trend.get("전문가전망", {}).get("결과", []))
            }
        else:
            report["내용"]["시장 동향"] = {"정보": "시장 동향 분석을 수행하지 않았습니다."}
        
        # 3. 업종 분석
        self.state["progress"] = 0.4
        if market_research_results.get("sector_trends") or stock_analysis_results.get("sector_comparison"):
            report["내용"]["업종 분석"] = {}
            
            # 업종 트렌드
            if market_research_results.get("sector_trends"):
                sector_insights = {}
                for sector, data in market_research_results["sector_trends"].items():
                    sector_insights[sector] = {
                        "동향": self._extract_market_insights(data.get("업종동향", {}).get("결과", [])),
                        "주요 기업 소식": self._extract_market_insights(data.get("주요기업소식", {}).get("결과", [])),
                        "투자 전망": self._extract_market_insights(data.get("투자전망", {}).get("결과", []))
                    }
                report["내용"]["업종 분석"]["업종 트렌드"] = sector_insights
            
            # 업종 내 기업 비교
            if stock_analysis_results.get("sector_comparison"):
                comparison_insights = {}
                
                for sector, data in stock_analysis_results["sector_comparison"].items():
                    qualitative = data.get("qualitative_comparison", {})
                    performance = data.get("performance_data", {})
                    
                    # 성과 비교 시각화
                    if performance:
                        chart_path = None
                        try:
                            # 성과 데이터를 데이터프레임으로 변환
                            if isinstance(performance, dict):
                                df = pd.DataFrame(performance)
                                chart_filename = f"{sector}_업종_성과비교_{timestamp}.png"
                                chart_path = os.path.join(self.charts_dir, chart_filename)
                                self.visualizer.plot_stock_comparison(df, title=f"{sector} 업종 성과 비교", save_path=chart_path)
                        except Exception as e:
                            print(f"차트 생성 중 오류: {e}")
                    
                    comparison_insights[sector] = {
                        "경쟁력 비교": self._extract_company_insights(qualitative.get("경쟁력비교", {}).get("결과", [])),
                        "투자 매력도": self._extract_company_insights(qualitative.get("투자매력도", {}).get("결과", [])),
                        "성과 비교 차트": chart_path
                    }
                
                report["내용"]["업종 분석"]["업종 내 기업 비교"] = comparison_insights
        else:
            report["내용"]["업종 분석"] = {"정보": "업종 분석을 수행하지 않았습니다."}
        
        # 4. 기업 분석
        self.state["progress"] = 0.5
        if stock_analysis_results.get("company_analysis"):
            report["내용"]["기업 분석"] = {}
            
            for code, company_data in stock_analysis_results["company_analysis"].items():
                company_info = company_data.get("company_info", {})
                technical = company_data.get("technical_analysis", {})
                
                company_name = company_info.get("기업명", f"종목({code})")
                
                # 차트 생성
                chart_paths = {}
                try:
                    # 기술적 분석 차트 생성
                    chart_filename = f"{code}_{company_name}_기술분석_{timestamp}.png"
                    chart_path = os.path.join(self.charts_dir, chart_filename)
                    
                    # 시각화 수행 - 이 부분은 실제 데이터에 맞게 조정해야 함
                    # self.visualizer.plot_technical_indicators(technical_data, title=f"{company_name} 기술적 지표", save_path=chart_path)
                    chart_paths["technical"] = chart_path
                except Exception as e:
                    print(f"차트 생성 중 오류: {e}")
                
                # 기업 정보 정리
                company_analysis = {
                    "기업 개요": self._extract_company_insights(company_info.get("기업정보", {}).get("결과", [])),
                    "최근 뉴스": self._extract_company_insights(company_info.get("최근뉴스", {}).get("결과", [])),
                    "재무 정보": self._extract_company_insights(company_info.get("재무정보", {}).get("결과", [])),
                    "투자 의견": self._extract_company_insights(company_info.get("투자의견", {}).get("결과", [])),
                    "사업 전략": self._extract_company_insights(company_info.get("사업전략", {}).get("결과", [])),
                    "기술적 분석": technical.get("기본 정보", {}),
                    "차트": chart_paths
                }
                
                report["내용"]["기업 분석"][company_name] = company_analysis
        else:
            report["내용"]["기업 분석"] = {"정보": "기업 분석을 수행하지 않았습니다."}
        
        # 5. 국제 정세 분석 추가
        self.state["progress"] = 0.6
        if geopolitical_analysis_results and geopolitical_analysis_results.get("trump_impact"):
            report["내용"]["국제 정세 분석"] = {
                "트럼프 정책 영향": geopolitical_analysis_results["trump_impact"].get("analysis", "분석 정보가 없습니다.")
            }
            
            # 산업별 영향 추가
            if "industry_impacts" in geopolitical_analysis_results:
                industry_impacts = {}
                for industry, impact in geopolitical_analysis_results["industry_impacts"].items():
                    industry_impacts[industry] = impact.get("analysis", f"{industry} 산업 영향 분석 정보가 없습니다.")
                
                report["내용"]["국제 정세 분석"]["산업별 영향"] = industry_impacts
            
            # 투자 전략 추가
            if "investment_strategy" in geopolitical_analysis_results:
                report["내용"]["국제 정세 분석"]["투자 전략 제안"] = geopolitical_analysis_results["investment_strategy"].get("strategy", "투자 전략 정보가 없습니다.")
        
        # 6. 투자 전략
        self.state["progress"] = 0.7
        report["내용"]["투자 전략"] = self._generate_investment_strategy(market_research_results, stock_analysis_results, geopolitical_analysis_results)
        
        # 7. 결론
        self.state["progress"] = 0.8
        report["내용"]["결론"] = self._generate_conclusion(report["내용"])
        
        # 주요 결과 채우기
        report["내용"]["개요"]["주요 결과"] = self._generate_key_findings(report["내용"])
        
        # 보고서를 마크다운 파일로 저장
        self.state["progress"] = 0.9
        report_path = self._save_report_as_markdown(report, timestamp)
        
        results["report"] = report
        results["report_path"] = report_path
        print(f"보고서 생성 완료. 저장 위치: {report_path}")
        
        # 상태 업데이트
        self.state["status"] = "completed"
        self.state["progress"] = 1.0
        self.state["report_draft"] = report
        
        return results
    
    def generate_pdf_report(self, query_data, market_research_results, stock_analysis_results, geopolitical_analysis_results=None):
        """
        puppeteer를 사용하여 PDF 보고서 생성
        
        Args:
            query_data (dict): 처리된 쿼리 데이터
            market_research_results (dict): 시장 분석 결과
            stock_analysis_results (dict): 주식 분석 결과
            geopolitical_analysis_results (dict, optional): 국제 정세 분석 결과
                
        Returns:
            dict: 보고서 결과 (PDF 경로 포함)
        """
        # 먼저 마크다운 보고서 생성
        md_results = self.generate_report(
            query_data, 
            market_research_results, 
            stock_analysis_results, 
            geopolitical_analysis_results
        )
        
        try:
            import markdown
            import os
            import tempfile
            import json
            
            markdown_file = md_results["report_path"]
            
            # 출력 PDF 파일 경로 설정
            pdf_filename = os.path.splitext(os.path.basename(markdown_file))[0] + '.pdf'
            pdf_filepath = os.path.join(self.reports_dir, pdf_filename)
            
            # 마크다운 파일 읽기
            with open(markdown_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # 마크다운을 HTML로 변환
            html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
            
            # HTML에 스타일 추가
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{md_results["report"]["제목"]}</title>
                <style>
                    body {{
                        font-family: 'Noto Sans KR', Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 900px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    h1 {{
                        color: #0066cc;
                        border-bottom: 2px solid #0066cc;
                        padding-bottom: 10px;
                        margin-top: 30px;
                    }}
                    h2 {{
                        color: #0080ff;
                        border-bottom: 1px solid #0080ff;
                        padding-bottom: 5px;
                        margin-top: 25px;
                    }}
                    /* 추가 스타일 생략... */
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{md_results["report"]["제목"]}</h1>
                    <p>생성일: {md_results["report"]["작성일"]}</p>
                </div>
                {html_content}
                <div class="footer">
                    <p>© 2024 금융 시장 분석 시스템</p>
                </div>
            </body>
            </html>
            """
            
            # 임시 HTML 파일 생성
            temp_html_file = os.path.splitext(markdown_file)[0] + '_temp.html'
            # 먼저 경로 변환을 수행
            temp_html_file_fixed = temp_html_file.replace('\\', '/')
            pdf_filepath_fixed = pdf_filepath.replace('\\', '/')
            with open(temp_html_file_fixed, 'w', encoding='utf-8') as f:
                f.write(styled_html)
            
            print(f"임시 HTML 파일 생성: {temp_html_file}")
            
            # 그 다음 f-string에 사용
            script_content = f"""
            const puppeteer = require('puppeteer');

            (async () => {{
                const browser = await puppeteer.launch({{
                    headless: 'new'
                }});
                const page = await browser.newPage();
                await page.goto('file://{temp_html_file_fixed}', {{
                    waitUntil: 'networkidle0'
                }});
                await page.pdf({{
                    path: '{pdf_filepath_fixed}',
                    format: 'A4',
                    margin: {{
                        top: '1cm',
                        right: '1cm',
                        bottom: '1cm',
                        left: '1cm'
                    }},
                    printBackground: true
                }});
                await browser.close();
                console.log('PDF generated successfully');
            }})();
            """
            
            # 임시 스크립트 파일 생성
            temp_script_file = os.path.join(tempfile.gettempdir(), 'pdf_generator.js')
            with open(temp_script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"임시 스크립트 파일 생성: {temp_script_file}")
            
            # puppeteer가 설치되어 있는지 확인하고 필요한 경우 설치
            import subprocess
            try:
                # package.json 생성
                package_dir = os.path.join(tempfile.gettempdir(), 'pdf_generator')
                os.makedirs(package_dir, exist_ok=True)
                
                package_json = {
                    "name": "pdf-generator",
                    "version": "1.0.0",
                    "description": "Generate PDF from HTML",
                    "dependencies": {
                        "puppeteer": "^22.0.0"
                    }
                }
                
                package_json_path = os.path.join(package_dir, 'package.json')
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(package_json, f)
                
                # puppeteer 설치
                print("puppeteer 설치 중...")
                subprocess.run(['npm', 'install'], cwd=package_dir, check=True)
                
                # 스크립트 실행
                print("Node.js 스크립트 실행 중...")
                subprocess.run(['node', temp_script_file], cwd=package_dir, check=True)
                
                # 임시 파일 삭제
                os.remove(temp_html_file)
                os.remove(temp_script_file)
                
                print(f"PDF 보고서 생성 완료. 저장 위치: {pdf_filepath}")
                
                # 자동으로 PDF 열기
                try:
                    import webbrowser
                    webbrowser.open('file://' + os.path.abspath(pdf_filepath))
                    print("PDF 보고서가 브라우저에서 열렸습니다.")
                except Exception as e:
                    print(f"PDF 파일 열기 실패: {e}")
                
                return {
                    "report": md_results["report"],
                    "report_path": md_results["report_path"],
                    "pdf_path": pdf_filepath
                }
                
            except Exception as e:
                import traceback
                print(f"PDF 생성 중 오류 발생: {e}")
                print("오류 상세 정보:")
                traceback.print_exc()
                return md_results
                
        except Exception as e:
            import traceback
            print(f"PDF 변환 중 오류 발생: {e}")
            print("오류 상세 정보:")
            traceback.print_exc()
            return md_results
    
    def _extract_market_insights(self, results):
        """웹 검색 결과에서 인사이트 추출"""
        insights = []
        
        for result in results[:3]:  # 상위 3개 결과만 사용
            title = result.get("title", "제목 없음")
            content = result.get("content", "내용 없음")
            url = result.get("url", "#")
            
            # 내용을 100자로 제한
            if len(content) > 100:
                content = content[:97] + "..."
            
            insights.append({
                "제목": title,
                "내용": content,
                "출처": url
            })
        
        return insights
    
    def _extract_company_insights(self, results):
        """기업 관련 웹 검색 결과에서 인사이트 추출"""
        return self._extract_market_insights(results)
    
    def _generate_investment_strategy(self, market_research, stock_analysis, geopolitical_analysis=None):
        """투자 전략 생성"""
        # 실제 프로젝트에서는 더 고급 알고리즘 또는 LLM을 사용하여 전략을 생성할 수 있음
        strategy = {
            "시장 전망": "현재 시장 상황을 고려할 때, 다음과 같은 투자 전략을 고려할 수 있습니다.",
            "단기 전략": [
                "시장 변동성이 높은 시기에는 위험 관리에 중점을 두는 것이 중요합니다.",
                "성장성과 안정성이 균형 잡힌 포트폴리오 구성을 권장합니다."
            ],
            "중장기 전략": [
                "기본적으로 튼튼한 기업에 대한 장기 투자가 권장됩니다.",
                "업종별 대표 기업에 분산 투자하는 전략이 유효할 수 있습니다."
            ],
            "주목할 포인트": [
                "글로벌 경제 지표 및 정책 변화에 주목해야 합니다.",
                "기업의 실적과 함께 사업 전략 및 미래 성장성을 고려하세요."
            ]
        }
        
        # 국제 정세 분석 결과가 있는 경우 투자 전략에 반영
        if geopolitical_analysis and geopolitical_analysis.get("investment_strategy"):
            strategy["트럼프 정책 관련 전략"] = [
                "미국 정책 변화에 민감한 산업에 대한 투자는 신중하게 진행하세요.",
                "보호무역 강화 시 내수 중심 기업에 더 높은 비중을 고려할 수 있습니다.",
                "환율 변동성 대비가 필요합니다."
            ]
        
        return strategy
    
    def _generate_conclusion(self, content):
        """결론 생성"""
        # 실제 프로젝트에서는 더 고급 알고리즘 또는 LLM을 사용하여 결론을 생성할 수 있음
        conclusion = {
            "요약": "본 보고서는 금융 시장 및 주요 기업에 대한 분석을 제공했습니다.",
            "주요 결론": [
                "시장은 변동성이 있으나 장기적 관점에서 기회가 있습니다.",
                "업종별 대표 기업들은 상대적으로 안정적인 성과를 보이고 있습니다.",
                "투자 결정 시 분산 투자와 리스크 관리가 중요합니다."
            ],
            "향후 모니터링 포인트": [
                "글로벌 경제 지표의 변화",
                "기업들의 실적 발표",
                "정책 변화 및 규제 환경"
            ]
        }
        
        # 국제 정세 분석 결과가 있는 경우 결론에 반영
        if "국제 정세 분석" in content:
            conclusion["주요 결론"].append("트럼프 행정부의 정책은 한국 금융 시장에 상당한 영향을 미칠 것으로 예상됩니다.")
            conclusion["향후 모니터링 포인트"].append("미국의 무역 및 외교 정책 변화")
            conclusion["향후 모니터링 포인트"].append("한미 관계 발전 방향")
        
        return conclusion
    
    def _generate_key_findings(self, content):
        """주요 발견 사항 생성"""
        findings = []
        
        # 시장 동향에서 발견
        if "시장 동향" in content and isinstance(content["시장 동향"], dict):
            if "최근 동향" in content["시장 동향"] and content["시장 동향"]["최근 동향"]:
                for insight in content["시장 동향"]["최근 동향"][:1]:
                    findings.append(f"시장 동향: {insight.get('제목', '')}")
        
        # 업종 분석에서 발견
        if "업종 분석" in content and isinstance(content["업종 분석"], dict):
            if "업종 트렌드" in content["업종 분석"]:
                for sector, data in list(content["업종 분석"]["업종 트렌드"].items())[:1]:
                    if "동향" in data and data["동향"]:
                        findings.append(f"{sector} 업종: {data['동향'][0].get('제목', '')}")
        
        # 기업 분석에서 발견
        if "기업 분석" in content and isinstance(content["기업 분석"], dict):
            for company, data in list(content["기업 분석"].items())[:1]:
                if "투자 의견" in data and data["투자 의견"]:
                    findings.append(f"{company}: {data['투자 의견'][0].get('제목', '')}")
        
        # 국제 정세 분석에서 발견
        if "국제 정세 분석" in content and isinstance(content["국제 정세 분석"], dict):
            if "트럼프 정책 영향" in content["국제 정세 분석"]:
                findings.append("트럼프 정책: 한국 금융 시장에 상당한 영향을 미칠 것으로 예상")
            
            if "산업별 영향" in content["국제 정세 분석"]:
                for industry in list(content["국제 정세 분석"]["산업별 영향"].keys())[:1]:
                    findings.append(f"트럼프 정책의 {industry} 산업 영향: 집중 분석 수행")
        
        return findings
    
    def _save_report_as_markdown(self, report, timestamp):
        """보고서를 마크다운 파일로 저장"""
        report_title = report["제목"].replace(" ", "_")
        filename = f"{report_title}_{timestamp}.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            # 제목과 날짜 (더 큰 폰트와 정렬)
            f.write(f"<div align='center'>\n\n")
            f.write(f"# {report['제목']}\n\n")
            f.write(f"**작성일: {report['작성일']}**\n\n")
            f.write(f"</div>\n\n")
            
            # 목차 (네비게이션 리스트로)
            f.write("## 📑 목차\n\n")
            for i, item in enumerate(report["목차"], 1):
                f.write(f"{i}. [{item}](#{item.lower().replace(' ', '-')})\n")
            f.write("\n\n")
            
            # 개요
            f.write("## 📋 개요\n\n")
            if "개요" in report["내용"]:
                overview = report["내용"]["개요"]
                f.write(f"### 🎯 분석 목적\n{overview.get('분석 목적', '')}\n\n")
                f.write(f"### 🔍 분석 방법\n{overview.get('분석 방법', '')}\n\n")
                
                f.write("### ✨ 주요 결과\n\n")
                for finding in overview.get("주요 결과", []):
                    f.write(f"- **{finding}**\n")
                f.write("\n\n")
            
            # 시장 동향
            f.write("## 📈 시장 동향\n\n")
            if "시장 동향" in report["내용"]:
                market_trend = report["내용"]["시장 동향"]
                
                if isinstance(market_trend, dict) and market_trend != {"정보": "시장 동향 분석을 수행하지 않았습니다."}:
                    # 최근 동향
                    f.write("### 최근 동향\n\n")
                    for insight in market_trend.get("최근 동향", []):
                        f.write(f"**{insight.get('제목', '')}**\n\n")
                        f.write(f"{insight.get('내용', '')}\n\n")
                        f.write(f"출처: [{insight.get('출처', '#')}]({insight.get('출처', '#')})\n\n")
                    
                    # 주요 이슈
                    f.write("### 주요 이슈\n\n")
                    for insight in market_trend.get("주요 이슈", []):
                        f.write(f"**{insight.get('제목', '')}**\n\n")
                        f.write(f"{insight.get('내용', '')}\n\n")
                        f.write(f"출처: [{insight.get('출처', '#')}]({insight.get('출처', '#')})\n\n")
                    
                    # 전문가 전망
                    f.write("### 전문가 전망\n\n")
                    for insight in market_trend.get("전문가 전망", []):
                        f.write(f"**{insight.get('제목', '')}**\n\n")
                        f.write(f"{insight.get('내용', '')}\n\n")
                        f.write(f"출처: [{insight.get('출처', '#')}]({insight.get('출처', '#')})\n\n")
                else:
                    f.write(market_trend.get("정보", "정보가 없습니다.") + "\n\n")
            
            # 업종 분석
            f.write("## 🏢 업종 분석\n\n")
            if "업종 분석" in report["내용"]:
                sector_analysis = report["내용"]["업종 분석"]
                
                if isinstance(sector_analysis, dict) and sector_analysis != {"정보": "업종 분석을 수행하지 않았습니다."}:
                    # 업종 트렌드
                    if "업종 트렌드" in sector_analysis:
                        f.write("### 업종 트렌드\n\n")
                        for sector, data in sector_analysis["업종 트렌드"].items():
                            f.write(f"#### {sector} 업종\n\n")
                            
                            f.write("**동향**\n\n")
                            for insight in data.get("동향", []):
                                f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                            f.write("\n")
                            
                            f.write("**주요 기업 소식**\n\n")
                            for insight in data.get("주요 기업 소식", []):
                                f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                            f.write("\n")
                            
                            f.write("**투자 전망**\n\n")
                            for insight in data.get("투자 전망", []):
                                f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                            f.write("\n\n")
                    
                    # 업종 내 기업 비교
                    if "업종 내 기업 비교" in sector_analysis:
                        f.write("### 업종 내 기업 비교\n\n")
                        for sector, data in sector_analysis["업종 내 기업 비교"].items():
                            f.write(f"#### {sector} 업종 기업 비교\n\n")
                            
                            f.write("**경쟁력 비교**\n\n")
                            for insight in data.get("경쟁력 비교", []):
                                f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                            f.write("\n")
                            
                            f.write("**투자 매력도**\n\n")
                            for insight in data.get("투자 매력도", []):
                                f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                            f.write("\n")
                            
                            if "성과 비교 차트" in data and data["성과 비교 차트"]:
                                f.write(f"![{sector} 업종 성과 비교]({data['성과 비교 차트']})\n\n")
                else:
                    f.write(sector_analysis.get("정보", "정보가 없습니다.") + "\n\n")
            
            # 기업 분석
            f.write("## 🏭 기업 분석\n\n")
            if "기업 분석" in report["내용"]:
                company_analysis = report["내용"]["기업 분석"]
                
                if isinstance(company_analysis, dict) and company_analysis != {"정보": "기업 분석을 수행하지 않았습니다."}:
                    for company, data in company_analysis.items():
                        f.write(f"### {company}\n\n")
                        
                        f.write("#### 기업 개요\n\n")
                        for insight in data.get("기업 개요", []):
                            f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                        f.write("\n")
                        
                        f.write("#### 최근 뉴스\n\n")
                        for insight in data.get("최근 뉴스", []):
                            f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                        f.write("\n")
                        
                        f.write("#### 재무 정보\n\n")
                        for insight in data.get("재무 정보", []):
                            f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                        f.write("\n")
                        
                        f.write("#### 투자 의견\n\n")
                        for insight in data.get("투자 의견", []):
                            f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                        f.write("\n")
                        
                        f.write("#### 사업 전략\n\n")
                        for insight in data.get("사업 전략", []):
                            f.write(f"- {insight.get('제목', '')}: {insight.get('내용', '')}\n")
                        f.write("\n")
                        
                        if "차트" in data and "technical" in data["차트"]:
                            f.write(f"![{company} 기술적 분석]({data['차트']['technical']})\n\n")
                else:
                    f.write(company_analysis.get("정보", "정보가 없습니다.") + "\n\n")
            
            # 국제 정세 분석
            if "국제 정세 분석" in report["목차"]:
                section_index = report["목차"].index("국제 정세 분석") + 1
                f.write(f"## 🌐 국제 정세 분석\n\n")
                
                if "국제 정세 분석" in report["내용"]:
                    geopolitical_analysis = report["내용"]["국제 정세 분석"]
                    
                    # 트럼프 정책 영향
                    if "트럼프 정책 영향" in geopolitical_analysis:
                        f.write("### 🇺🇸 트럼프 정책 영향\n\n")
                        f.write(f"```\n{geopolitical_analysis['트럼프 정책 영향']}\n```\n\n")
                    
                    # 산업별 영향
                    if "산업별 영향" in geopolitical_analysis:
                        f.write("### 🏭 산업별 영향\n\n")
                        for industry, analysis in geopolitical_analysis["산업별 영향"].items():
                            f.write(f"#### {industry} 산업\n\n")
                            f.write(f"```\n{analysis}\n```\n\n")
                    
                    # 투자 전략 제안
                    if "투자 전략 제안" in geopolitical_analysis:
                        f.write("### 💰 투자 전략 제안\n\n")
                        f.write(f"```\n{geopolitical_analysis['투자 전략 제안']}\n```\n\n")
            
            # 투자 전략
            strategy_index = report["목차"].index("투자 전략") + 1
            f.write(f"## 💼 투자 전략\n\n")
            if "투자 전략" in report["내용"]:
                strategy = report["내용"]["투자 전략"]
                
                f.write(f"### 시장 전망\n{strategy.get('시장 전망', '')}\n\n")
                
                f.write("### 단기 전략\n\n")
                for item in strategy.get("단기 전략", []):
                    f.write(f"- {item}\n")
                f.write("\n")
                
                f.write("### 중장기 전략\n\n")
                for item in strategy.get("중장기 전략", []):
                    f.write(f"- {item}\n")
                f.write("\n")
                
                # 트럼프 정책 관련 전략
                if "트럼프 정책 관련 전략" in strategy:
                    f.write("### 트럼프 정책 관련 전략\n\n")
                    for item in strategy.get("트럼프 정책 관련 전략", []):
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                f.write("### 주목할 포인트\n\n")
                for item in strategy.get("주목할 포인트", []):
                    f.write(f"- {item}\n")
                f.write("\n\n")
            
            # 결론
            conclusion_index = report["목차"].index("결론") + 1
            f.write(f"## 📝 결론\n\n")
            if "결론" in report["내용"]:
                conclusion = report["내용"]["결론"]
                
                f.write(f"### 요약\n{conclusion.get('요약', '')}\n\n")
                
                f.write("### 주요 결론\n\n")
                for item in conclusion.get("주요 결론", []):
                    f.write(f"- **{item}**\n")
                f.write("\n")
                
                f.write("### 향후 모니터링 포인트\n\n")
                for item in conclusion.get("향후 모니터링 포인트", []):
                    f.write(f"- ⚠️ {item}\n")
                f.write("\n")
        
        return filepath