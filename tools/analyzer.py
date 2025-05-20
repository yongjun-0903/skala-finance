# tools/analyzer.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
from pathlib import Path
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose

# config 모듈 임포트
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
except NameError:
    import inspect
    current_file = Path(inspect.getfile(inspect.currentframe()))
    sys.path.append(str(current_file.parent.parent))

from config import TARGET_COMPANIES
from tools.stock_data import StockDataFetcher

class StockAnalyzer:
    """주식 데이터 분석을 위한 클래스"""
    
    def __init__(self):
        """초기화 메서드"""
        self.stock_fetcher = StockDataFetcher()
        
    def analyze_trend(self, data, window=20):
        """
        추세 분석: 이동평균을 통한 주가 추세 분석
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            window (int): 이동평균 기간
            
        Returns:
            dict: 추세 분석 결과
        """
        # 데이터 복사
        df = data.copy()
        
        # 이동평균
        df['MA'] = df['Close'].rolling(window=window).mean()
        
        # 추세 판단 (현재가 > 이동평균 => 상승 추세)
        current_price = df['Close'].iloc[-1]
        ma_price = df['MA'].iloc[-1]
        
        trend = "상승" if current_price > ma_price else "하락"
        strength = abs(current_price - ma_price) / ma_price * 100
        
        return {
            "추세": trend,
            "강도": strength,
            "현재가": current_price,
            "이동평균": ma_price
        }
    
    def analyze_momentum(self, data, period=14):
        """
        모멘텀 분석: RSI를 통한 모멘텀 측정
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            period (int): RSI 계산 기간
            
        Returns:
            dict: 모멘텀 분석 결과
        """
        # RSI 계산
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # RSI 해석
        if current_rsi > 70:
            status = "과매수"
        elif current_rsi < 30:
            status = "과매도"
        else:
            status = "중립"
            
        return {
            "RSI": current_rsi,
            "상태": status
        }
    
    def analyze_volatility(self, data, window=20):
        """
        변동성 분석: 주가의 표준편차를 통한 변동성 측정
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            window (int): 계산 기간
            
        Returns:
            dict: 변동성 분석 결과
        """
        # 일간 수익률
        returns = data['Close'].pct_change().dropna()
        
        # 변동성 (표준편차)
        volatility = returns.rolling(window=window).std().iloc[-1] * np.sqrt(252) * 100  # 연간화
        
        # 변동성 수준 판단
        if volatility > 40:
            level = "매우 높음"
        elif volatility > 30:
            level = "높음"
        elif volatility > 20:
            level = "보통"
        else:
            level = "낮음"
            
        return {
            "변동성": volatility,
            "수준": level
        }
    
    def analyze_support_resistance(self, data, window=20):
        """
        지지선/저항선 분석
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            window (int): 참조 기간
            
        Returns:
            dict: 지지선/저항선 분석 결과
        """
        recent_data = data.iloc[-window:]
        
        # 지지선 (최근 데이터의 최저가 부근)
        support = recent_data['Low'].min()
        
        # 저항선 (최근 데이터의 최고가 부근)
        resistance = recent_data['High'].max()
        
        current_price = data['Close'].iloc[-1]
        
        return {
            "현재가": current_price,
            "지지선": support,
            "저항선": resistance,
            "지지선까지": (current_price - support) / current_price * 100,
            "저항선까지": (resistance - current_price) / current_price * 100
        }
    
    def predict_price(self, data, days=5):
        """
        간단한 주가 예측 (ARIMA 모델 사용)
        
        Args:
            data (pandas.DataFrame): 주가 데이터
            days (int): 예측 일수
            
        Returns:
            dict: 예측 결과
        """
        try:
            # ARIMA 모델 적합
            model = ARIMA(data['Close'], order=(5, 1, 0))
            model_fit = model.fit()
            
            # 예측
            forecast = model_fit.forecast(steps=days)
            
            # 결과 포맷팅
            current_price = data['Close'].iloc[-1]
            predicted_price = forecast.iloc[-1]
            
            change = (predicted_price - current_price) / current_price * 100
            
            return {
                "현재가": current_price,
                f"{days}일 후 예상가": predicted_price,
                "예상 변화율": change,
                "예측 추세": "상승" if change > 0 else "하락"
            }
        except:
            # 간단한 선형회귀 모델을 대안으로 사용
            x = np.array(range(len(data))).reshape(-1, 1)
            y = data['Close'].values
            
            model = LinearRegression()
            model.fit(x, y)
            
            # 예측
            x_pred = np.array(range(len(data), len(data) + days)).reshape(-1, 1)
            y_pred = model.predict(x_pred)
            
            # 결과 포맷팅
            current_price = data['Close'].iloc[-1]
            predicted_price = y_pred[-1]
            
            change = (predicted_price - current_price) / current_price * 100
            
            return {
                "현재가": current_price,
                f"{days}일 후 예상가": predicted_price,
                "예상 변화율": change,
                "예측 추세": "상승" if change > 0 else "하락"
            }
    
    def compare_sector_performance(self, sector, start=None, end=None):
        """
        특정 업종 내 기업들의 성과 비교
        
        Args:
            sector (str): 업종명
            start (str): 시작일자 (YYYY-MM-DD)
            end (str): 종료일자 (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: 각 기업의 성과 지표
        """
        companies = TARGET_COMPANIES.get(sector, [])
        if not companies:
            raise ValueError(f"지원하지 않는 업종: {sector}")
        
        codes = [company['code'] for company in companies]
        names = [company['name'] for company in companies]
        
        # 여러 종목 데이터 가져오기
        result = []
        
        for code, name in zip(codes, names):
            data = self.stock_fetcher.get_stock_data(code, start, end)
            if data.empty:
                continue
                
            # 수익률 계산
            returns = data['Close'].pct_change().dropna()
            
            # 성과 지표 계산
            total_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100
            volatility = returns.std() * np.sqrt(252) * 100
            sharpe = (total_return / 100) / (volatility / 100) if volatility != 0 else 0
            
            # 최근 모멘텀 (최근 1개월 수익률)
            recent_data = data.iloc[-20:]
            recent_return = (recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0] - 1) * 100
            
            result.append({
                '기업명': name,
                '종목코드': code,
                '총 수익률(%)': total_return,
                '변동성(%)': volatility,
                '샤프 비율': sharpe,
                '최근 모멘텀(%)': recent_return
            })
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(result)
        df.index = pd.DatetimeIndex(df.index.values, freq='B')  # 'B'는 business day를 의미
        # 총 수익률 기준 정렬
        if not df.empty:
            df = df.sort_values('총 수익률(%)', ascending=False)
        
        return df
    
    def full_analysis(self, code, name=None):
        """
        종합 분석: 모든 분석 결과를 종합하여 반환
        
        Args:
            code (str): 종목 코드
            name (str): 종목명
            
        Returns:
            dict: 종합 분석 결과
        """
        if name is None:
            # 종목명 찾기
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
        data = self.stock_fetcher.get_stock_data(code)
        if data.empty:
            return {"오류": f"{name}({code}) 데이터를 가져오는데 실패했습니다."}
        
        # 기술적 지표 계산
        tech_data = self.stock_fetcher.calculate_technical_indicators(data)
        
        # 분석 수행
        trend_analysis = self.analyze_trend(data)
        momentum_analysis = self.analyze_momentum(data)
        volatility_analysis = self.analyze_volatility(data)
        support_resistance = self.analyze_support_resistance(data)
        price_prediction = self.predict_price(data)
        
        # 최근 성과 계산
        recent_return_1m = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100 if len(data) >= 20 else None
        recent_return_3m = (data['Close'].iloc[-1] / data['Close'].iloc[-60] - 1) * 100 if len(data) >= 60 else None
        recent_return_6m = (data['Close'].iloc[-1] / data['Close'].iloc[-120] - 1) * 100 if len(data) >= 120 else None
        recent_return_1y = (data['Close'].iloc[-1] / data['Close'].iloc[-250] - 1) * 100 if len(data) >= 250 else None
        
        # MACD 시그널
        latest_macd = tech_data['MACD'].iloc[-1]
        latest_signal = tech_data['Signal'].iloc[-1]
        macd_status = "매수 신호" if latest_macd > latest_signal else "매도 신호"
        
        # 볼린저 밴드 상태
        latest_close = tech_data['Close'].iloc[-1]
        latest_upper = tech_data['Upper_Band'].iloc[-1]
        latest_lower = tech_data['Lower_Band'].iloc[-1]
        
        if latest_close > latest_upper:
            bb_status = "과매수"
        elif latest_close < latest_lower:
            bb_status = "과매도"
        else:
            bb_status = "중립"
        
        # 종합 분석 결과
        return {
            "기본 정보": {
                "종목명": name,
                "종목코드": code,
                "현재가": data['Close'].iloc[-1],
                "분석일자": datetime.now().strftime('%Y-%m-%d')
            },
            "추세 분석": trend_analysis,
            "모멘텀 분석": momentum_analysis,
            "변동성 분석": volatility_analysis,
            "지지/저항 분석": support_resistance,
            "가격 예측": price_prediction,
            "최근 수익률": {
                "1개월": recent_return_1m,
                "3개월": recent_return_3m,
                "6개월": recent_return_6m,
                "1년": recent_return_1y
            },
            "기술적 지표": {
                "MACD 신호": macd_status,
                "볼린저 밴드": bb_status,
                "RSI": tech_data['RSI'].iloc[-1] if 'RSI' in tech_data.columns else None
            }
        }
