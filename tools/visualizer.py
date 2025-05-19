# tools/visualizer.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.font_manager as fm

# config 모듈 임포트
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    import inspect
    current_file = Path(inspect.getfile(inspect.currentframe()))
    sys.path.append(str(current_file.parent.parent))

from config import OUTPUTS_DIR, CHARTS_DIR, TARGET_COMPANIES
from tools.stock_data import StockDataFetcher

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class StockVisualizer:
    """주식 데이터 시각화를 위한 클래스"""
    
    def __init__(self):
        """초기화 메서드"""
        self.outputs_dir = OUTPUTS_DIR
        self.charts_dir = CHARTS_DIR
        os.makedirs(self.charts_dir, exist_ok=True)
        self.stock_fetcher = StockDataFetcher()
    
    def plot_stock_price(self, data, title=None, ma_periods=None, save_path=None):
        """
        주가 차트 시각화
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            title (str): 차트 제목
            ma_periods (list): 이동평균 기간 리스트
            save_path (str): 저장 경로
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        if ma_periods is None:
            ma_periods = [20, 60]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 주가 그래프
        ax.plot(data.index, data['Close'], label='종가', linewidth=2)
        
        # 이동평균선
        for period in ma_periods:
            ma_col = f'MA{period}'
            if ma_col not in data.columns:
                data[ma_col] = data['Close'].rolling(window=period).mean()
            ax.plot(data.index, data[ma_col], label=f'{period}일 이동평균', linestyle='--')
        
        # 그래프 스타일 설정
        ax.set_title(title if title else '주가 차트', fontsize=16)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('가격 (원)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='best')
        
        # 날짜 형식 설정
        ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        fig.autofmt_xdate()
        
        # 금액 단위 설정
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        
        plt.tight_layout()
        
        # 파일 저장
        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
    
    def plot_volume_chart(self, data, title=None, save_path=None):
        """
        거래량 차트 시각화
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            title (str): 차트 제목
            save_path (str): 저장 경로
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 거래량 바 차트
        ax.bar(data.index, data['Volume'], alpha=0.7, label='거래량', color='dodgerblue')
        
        # 20일 이동평균 거래량
        vol_ma = data['Volume'].rolling(window=20).mean()
        ax.plot(data.index, vol_ma, color='red', label='20일 이동평균 거래량', linewidth=2)
        
        # 그래프 스타일 설정
        ax.set_title(title if title else '거래량 차트', fontsize=16)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('거래량', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='best')
        
        # 날짜 형식 설정
        ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        fig.autofmt_xdate()
        
        # 거래량 단위 설정
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        
        plt.tight_layout()
        
        # 파일 저장
        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
    
    def plot_candlestick_chart(self, data, title=None, ma_periods=None, save_path=None):
        """
        캔들스틱 차트 시각화
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            title (str): 차트 제목
            ma_periods (list): 이동평균 기간 리스트
            save_path (str): 저장 경로
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        if ma_periods is None:
            ma_periods = [20, 60]
        
        # 최근 3개월 데이터만 표시
        if len(data) > 60:
            data = data.iloc[-60:]
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        # 캔들스틱 데이터 생성
        width = 0.6
        width2 = 0.05
        
        # 상승
        up = data[data.Close >= data.Open]
        # 하락
        down = data[data.Close < data.Open]
        
        # 캔들 몸통 색상
        col1 = 'red'
        col2 = 'blue'
        
        # 상승봉
        ax.bar(up.index, up.Close-up.Open, width, bottom=up.Open, color=col1, alpha=0.8)
        ax.bar(up.index, up.High-up.Close, width2, bottom=up.Close, color=col1, alpha=0.8)
        ax.bar(up.index, up.Low-up.Open, width2, bottom=up.Open, color=col1, alpha=0.8)
        
        # 하락봉
        ax.bar(down.index, down.Close-down.Open, width, bottom=down.Open, color=col2, alpha=0.8)
        ax.bar(down.index, down.High-down.Open, width2, bottom=down.Open, color=col2, alpha=0.8)
        ax.bar(down.index, down.Low-down.Close, width2, bottom=down.Close, color=col2, alpha=0.8)
        
        # 이동평균선
        for period in ma_periods:
            ma_col = f'MA{period}'
            if ma_col not in data.columns:
                data[ma_col] = data['Close'].rolling(window=period).mean()
            ax.plot(data.index, data[ma_col], label=f'{period}일 이동평균', linestyle='--')
        
        # 그래프 스타일 설정
        ax.set_title(title if title else '캔들스틱 차트', fontsize=16)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('가격 (원)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='best')
        
        # 날짜 형식 설정
        ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        fig.autofmt_xdate()
        
        # 금액 단위 설정
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        
        plt.tight_layout()
        
        # 파일 저장
        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
    
    def plot_technical_indicators(self, data, title=None, save_path=None):
        """
        기술적 지표 시각화
        
        Args:
            data (pandas.DataFrame): 기술적 지표가 포함된 주가 데이터
            title (str): 차트 제목
            save_path (str): 저장 경로
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        # 데이터 준비
        if 'RSI' not in data.columns or 'MACD' not in data.columns:
            data = self.stock_fetcher.calculate_technical_indicators(data)
        
        # 최근 6개월 데이터만 표시
        if len(data) > 120:
            data = data.iloc[-120:]
        
        # 그래프 생성
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # 주가 및 이동평균선
        ax1.plot(data.index, data['Close'], label='종가', color='black')
        ax1.plot(data.index, data['MA20'], label='20일 이동평균', color='blue', linestyle='--')
        ax1.plot(data.index, data['MA60'], label='60일 이동평균', color='red', linestyle='--')
        
        # 볼린저 밴드
        ax1.plot(data.index, data['Upper_Band'], label='상단 밴드', color='green', linestyle='-')
        ax1.plot(data.index, data['Lower_Band'], label='하단 밴드', color='green', linestyle='-')
        ax1.fill_between(data.index, data['Upper_Band'], data['Lower_Band'], color='green', alpha=0.1)
        
        # MACD
        ax2.plot(data.index, data['MACD'], label='MACD', color='blue')
        ax2.plot(data.index, data['Signal'], label='시그널', color='red')
        ax2.bar(data.index, data['MACD'] - data['Signal'], label='히스토그램', alpha=0.5, color='gray')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # RSI
        ax3.plot(data.index, data['RSI'], label='RSI', color='purple')
        ax3.axhline(y=70, color='red', linestyle='--', alpha=0.5)
        ax3.axhline(y=30, color='green', linestyle='--', alpha=0.5)
        ax3.fill_between(data.index, data['RSI'], 70, where=(data['RSI'] >= 70), color='red', alpha=0.3)
        ax3.fill_between(data.index, data['RSI'], 30, where=(data['RSI'] <= 30), color='green', alpha=0.3)
        ax3.set_ylim([0, 100])
        
        # 그래프 설정
        ax1.set_title(title if title else '기술적 지표', fontsize=16)
        ax1.set_ylabel('가격 (원)', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend(loc='best')
        
        ax2.set_ylabel('MACD', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend(loc='best')
        
        ax3.set_xlabel('날짜', fontsize=12)
        ax3.set_ylabel('RSI', fontsize=12)
        ax3.grid(True, linestyle='--', alpha=0.7)
        ax3.legend(loc='best')
        
        # 날짜 형식 설정
        for ax in [ax1, ax2, ax3]:
            ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        
        # 금액 단위 설정
        ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
        
        fig.autofmt_xdate()
        plt.tight_layout()
        
        # 파일 저장
        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
    
    def plot_stock_comparison(self, data, title=None, save_path=None):
        """
        여러 종목 비교 시각화
        
        Args:
            data (pandas.DataFrame): 종목별 정규화된 성과 데이터
            title (str): 차트 제목
            save_path (str): 저장 경로
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 각 종목별 그래프
        for column in data.columns:
            ax.plot(data.index, data[column], label=column)
        
        # 그래프 스타일 설정
        ax.set_title(title if title else '종목 비교', fontsize=16)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('기준 대비 수익률 (%)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='best')
        
        # 날짜 형식 설정
        ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
        fig.autofmt_xdate()
        
        # 수익률 단위 설정
        ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.1f}%'))
        
        # 기준선 (100%) 추가
        ax.axhline(y=100, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        # 파일 저장
        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
    
    def plot_correlation_matrix(self, codes, names=None, start=None, end=None, title=None, save_path=None):
        """
        종목 간 상관관계 행렬 시각화
        
        Args:
            codes (list): 종목 코드 리스트
            names (list): 종목명 리스트
            start (str): 시작일자 (YYYY-MM-DD)
            end (str): 종료일자 (YYYY-MM-DD)
            title (str): 차트 제목
            save_path (str): 저장 경로
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        # 데이터 가져오기
        df = self.stock_fetcher.get_multiple_stocks(codes, start, end)
        
        if df.empty:
            return None
        
        # 종목명 매핑
        if names is None:
            names = codes
        
        col_map = {code: name for code, name in zip(codes, names) if code in df.columns}
        df = df.rename(columns=col_map)
        
        # 수익률 계산
        returns = df.pct_change().dropna()
        
        # 상관관계 계산
        corr = returns.corr()
        
        # 그래프 그리기
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, vmin=-1, vmax=1)
        
        plt.title(title if title else '종목 간 상관관계', fontsize=16)
        plt.tight_layout()
        
        # 파일 저장
        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
    
    def plot_sector_performance(self, sector_data, title=None, save_path=None):
        """
        업종별 성과 시각화
        
        Args:
            sector_data (pandas.DataFrame): 업종별 성과 데이터
            title (str): 차트 제목
            save_path (str): 저장 경로
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        # 성과 데이터 정렬
        data = sector_data.sort_values('총 수익률(%)', ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 수평 막대 그래프
        bars = ax.barh(data['기업명'], data['총 수익률(%)'], color='dodgerblue', alpha=0.7)
        
        # 그래프 스타일 설정
        ax.set_title(title if title else '업종별 성과', fontsize=16)
        ax.set_xlabel('총 수익률 (%)', fontsize=12)
        ax.grid(True, linestyle='--', alpha=0.7, axis='x')
        
        # 값 레이블 추가
        for bar in bars:
            width = bar.get_width()
            label_x_pos = width if width >= 0 else 0
            ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                    va='center', ha='left' if width >= 0 else 'right',
                    fontsize=9, color='black')
        
        # 수익률 표시 형식
        ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.1f}%'))
        
        # 기준선 (0%) 추가
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
        
        plt.tight_layout()
        
        # 파일 저장
        if save_path:
            plt.savefig(save_path, dpi=300)
            plt.close()
            return save_path
        else:
            plt.show()
            plt.close()
            return None
    
    def create_stock_dashboard(self, code, name=None, period=365, save_prefix=None):
        """
        종합 주식 대시보드 생성
        
        Args:
            code (str): 종목 코드
            name (str): 종목명
            period (int): 분석 기간(일)
            save_prefix (str): 저장 파일명 접두사
            
        Returns:
            dict: 차트 파일 경로 목록
        """
        if not name:
            for sector, companies in TARGET_COMPANIES.items():
                for company in companies:
                    if company['code'] == code:
                        name = company['name']
                        break
                if name:
                    break
        
        if not name:
            name = f"종목({code})"
        
        # 데이터 가져오기
        start_date = (datetime.now() - timedelta(days=period)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        data = self.stock_fetcher.get_stock_data(code, start=start_date, end=end_date)
        if data.empty:
            return {"error": f"{name}({code}) 데이터를 가져오는데 실패했습니다."}
        
        # 기술적 지표 계산
        tech_data = self.stock_fetcher.calculate_technical_indicators(data)
        
        # 차트 생성 경로
        chart_paths = {}
        
        if save_prefix:
            # 캔들스틱 차트
            candlestick_path = os.path.join(self.charts_dir, f"{save_prefix}_candlestick.png")
            chart_paths['candlestick'] = self.plot_candlestick_chart(
                data, title=f"{name} 캔들스틱 차트", save_path=candlestick_path
            )
            
            # 거래량 차트
            volume_path = os.path.join(self.charts_dir, f"{save_prefix}_volume.png")
            chart_paths['volume'] = self.plot_volume_chart(
                data, title=f"{name} 거래량 차트", save_path=volume_path
            )
            
            # 기술적 지표 차트
            indicators_path = os.path.join(self.charts_dir, f"{save_prefix}_indicators.png")
            chart_paths['indicators'] = self.plot_technical_indicators(
                tech_data, title=f"{name} 기술적 지표", save_path=indicators_path
            )
            
            # 같은 업종 종목 비교
            sector = None
            for s, companies in TARGET_COMPANIES.items():
                for company in companies:
                    if company['code'] == code:
                        sector = s
                        break
                if sector:
                    break
            
            if sector:
                # 상위 5개 기업 코드 추출
                compare_codes = [company['code'] for company in TARGET_COMPANIES[sector][:5]]
                compare_names = [company['name'] for company in TARGET_COMPANIES[sector][:5]]
                
                if code not in compare_codes:
                    compare_codes[-1] = code
                    compare_names[-1] = name
                
                # 성과 비교 데이터
                compare_data = self.stock_fetcher.compare_performance(
                    compare_codes, compare_names, start=start_date, end=end_date
                )
                
                if not compare_data.empty:
                    comparison_path = os.path.join(self.charts_dir, f"{save_prefix}_comparison.png")
                    chart_paths['comparison'] = self.plot_stock_comparison(
                        compare_data, title=f"{sector} 업종 주요 기업 성과 비교", save_path=comparison_path
                    )
                    
                    correlation_path = os.path.join(self.charts_dir, f"{save_prefix}_correlation.png")
                    chart_paths['correlation'] = self.plot_correlation_matrix(
                        compare_codes, compare_names, start=start_date, end=end_date,
                        title=f"{sector} 업종 주요 기업 상관관계", save_path=correlation_path
                    )
        else:
            # 화면에 차트 표시
            self.plot_candlestick_chart(data, title=f"{name} 캔들스틱 차트")
            self.plot_volume_chart(data, title=f"{name} 거래량 차트")
            self.plot_technical_indicators(tech_data, title=f"{name} 기술적 지표")
        
        return chart_paths


# # 테스트 코드
# if __name__ == "__main__":
#     visualizer = StockVisualizer()
    
#     # KB금융 데이터 가져오기
#     fetcher = StockDataFetcher()
#     kb_code = TARGET_COMPANIES["은행"][0]["code"]
#     kb_name = TARGET_COMPANIES["은행"][0]["name"]
    
#     kb_data = fetcher.get_stock_data(kb_code)
    
#     # 주가 차트 시각화
#     visualizer.plot_stock_price(kb_data, title=f"{kb_name} 주가 차트")
    
#     # 캔들스틱 차트 시각화 (최근 3개월)
#     recent_data = kb_data.iloc[-60:]
#     visualizer.plot_candlestick_chart(recent_data, title=f"{kb_name} 캔들스틱 차트")
    
#     # 기술적 지표 시각화
#     kb_tech_data = fetcher.calculate_technical_indicators(kb_data)
#     visualizer.plot_technical_indicators(kb_tech_data, title=f"{kb_name} 기술적 지표")
    
#     # 은행 업종 상위 3개 기업 성과 비교
#     bank_codes = [company['code'] for company in TARGET_COMPANIES["은행"][:3]]
#     bank_names = [company['name'] for company in TARGET_COMPANIES["은행"][:3]]
#     compare_df = fetcher.compare_performance(bank_codes, bank_names)
    
#     visualizer.plot_stock_comparison(compare_df, title="은행 업종 상위 3개 기업 성과 비교")