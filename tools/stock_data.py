# tools/stock_data.py

import FinanceDataReader as fdr
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# config 모듈 임포트
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    import inspect
    current_file = Path(inspect.getfile(inspect.currentframe()))
    sys.path.append(str(current_file.parent.parent))

from config import TARGET_COMPANIES

class StockDataFetcher:
    """주식 데이터를 가져오고 처리하는 클래스"""
    
    def __init__(self):
        """초기화 메서드"""
        pass
    
    def get_stock_data(self, code, start=None, end=None):
        """
        주식 코드에 해당하는 데이터를 가져옴
        
        Args:
            code (str): 주식 코드
            start (str): 시작일자 (YYYY-MM-DD)
            end (str): 종료일자 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: 주식 데이터
        """
        # 기본값 설정
        if end is None:
            end = datetime.now().strftime('%Y-%m-%d')
        if start is None:
            # 기본값: 1년 전
            start = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # FinanceDataReader로 데이터 가져오기
        try:
            data = fdr.DataReader(code, start, end)
            return data
        except Exception as e:
            print(f"데이터 가져오기 실패 ({code}): {e}")
            return pd.DataFrame()  # 빈 데이터프레임 반환
    
    def get_multiple_stocks(self, codes, start=None, end=None):
        """
        여러 주식 코드에 해당하는 종가 데이터를 한 번에 가져옴
        
        Args:
            codes (list): 주식 코드 리스트
            start (str): 시작일자 (YYYY-MM-DD)
            end (str): 종료일자 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: 각 주식의 종가를 컬럼으로 갖는 데이터프레임
        """
        result = pd.DataFrame()
        
        for code in codes:
            data = self.get_stock_data(code, start, end)
            if not data.empty:
                if result.empty:
                    result.index = data.index
                result[code] = data['Close']
        
        return result
    
    def get_index_data(self, index_code='KS11', start=None, end=None):
        """
        지수 데이터 가져오기
        
        Args:
            index_code (str): 지수 코드 (KS11: KOSPI, KQ11: KOSDAQ)
            start (str): 시작일자 (YYYY-MM-DD)
            end (str): 종료일자 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: 지수 데이터
        """
        return self.get_stock_data(index_code, start, end)
    
    def calculate_returns(self, data, period='daily'):
        """
        수익률 계산
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            period (str): 기간 ('daily', 'weekly', 'monthly', 'yearly')
            
        Returns:
            pandas.DataFrame: 수익률 데이터
        """
        if period == 'daily':
            return data['Close'].pct_change().dropna()
        
        elif period == 'weekly':
            return data['Close'].resample('W').last().pct_change().dropna()
        
        elif period == 'monthly':
            return data['Close'].resample('M').last().pct_change().dropna()
        
        elif period == 'yearly':
            return data['Close'].resample('Y').last().pct_change().dropna()
        
        else:
            raise ValueError(f"지원하지 않는 기간: {period}")
    
    def calculate_technical_indicators(self, data):
        """
        기술적 지표 계산
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            
        Returns:
            pandas.DataFrame: 기술적 지표가 추가된 데이터
        """
        df = data.copy()
        
        # 이동평균
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        df['MA120'] = df['Close'].rolling(window=120).mean()
        
        # 볼린저 밴드 (20일 기준)
        df['MA20_STD'] = df['Close'].rolling(window=20).std()
        df['Upper_Band'] = df['MA20'] + (df['MA20_STD'] * 2)
        df['Lower_Band'] = df['MA20'] - (df['MA20_STD'] * 2)
        
        # MACD
        df['EMA12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI (14일 기준)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    def get_sector_data(self, sector):
        """
        특정 업종의 모든 기업 데이터 가져오기
        
        Args:
            sector (str): 업종명 (config.py의 TARGET_COMPANIES 키)
            
        Returns:
            dict: 각 기업별 주가 데이터
        """
        if sector not in TARGET_COMPANIES:
            raise ValueError(f"지원하지 않는 업종: {sector}")
        
        result = {}
        for company in TARGET_COMPANIES[sector]:
            code = company['code']
            name = company['name']
            data = self.get_stock_data(code)
            result[code] = {
                'name': name,
                'data': data
            }
        
        return result
    
    def compare_performance(self, codes, names=None, start=None, end=None):
        """
        여러 종목의 성과 비교 (첫 날 기준 정규화)
        
        Args:
            codes (list): 주식 코드 리스트
            names (list): 종목명 리스트 (없으면 코드 사용)
            start (str): 시작일자 (YYYY-MM-DD)
            end (str): 종료일자 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: 정규화된 성과 데이터
        """
        if names is None:
            names = codes
        
        # 데이터 가져오기
        df = self.get_multiple_stocks(codes, start, end)
        if df.empty:
            return df
        
        # 첫날 기준 정규화
        normalized_df = pd.DataFrame(index=df.index)
        for i, code in enumerate(codes):
            if code in df.columns:
                name = names[i] if i < len(names) else code
                normalized_df[name] = df[code] / df[code].iloc[0] * 100
        
        return normalized_df


# # 테스트 코드
# if __name__ == "__main__":
#     fetcher = StockDataFetcher()
    
#     # KB금융 데이터 가져오기
#     kb_code = TARGET_COMPANIES["은행"][0]["code"]
#     kb_name = TARGET_COMPANIES["은행"][0]["name"]
#     kb_data = fetcher.get_stock_data(kb_code)
    
#     print(f"{kb_name} ({kb_code}) 데이터:")
#     print(kb_data.tail())
    
#     # 기술적 지표 계산
#     kb_with_indicators = fetcher.calculate_technical_indicators(kb_data)
#     print("\n기술적 지표:")
#     print(kb_with_indicators[['Close', 'MA20', 'RSI', 'MACD']].tail())
    
#     # 은행 업종 내 상위 3개 기업 성과 비교
#     bank_codes = [company['code'] for company in TARGET_COMPANIES["은행"][:3]]
#     bank_names = [company['name'] for company in TARGET_COMPANIES["은행"][:3]]
#     compare_df = fetcher.compare_performance(bank_codes, bank_names)
    
#     print("\n은행 업종 상위 3개 기업 성과 비교:")
#     print(compare_df.tail())
    
#     # KOSPI 지수 데이터 가져오기
#     kospi_data = fetcher.get_index_data('KS11')
#     print("\nKOSPI 지수 데이터:")
#     print(kospi_data.tail())
    
#     # 월간 수익률 계산
#     monthly_returns = fetcher.calculate_returns(kb_data, period='monthly')
#     print("\nKB금융 월간 수익률:")
#     print(monthly_returns.tail())