import datetime
import os
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr

def fetch_daily_indicators():
    # 실행 당일 날짜 (YYYY-MM-DD)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 1. 해외 매크로 지표 (yfinance)
    # TNX: 미국채 10년 금리, CL=F: WTI 선물, KRW=X: 원/달러 환율
    us10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
    wti = yf.Ticker("CL=F").history(period="1d")['Close'].iloc[-1]
    usdkrw = yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]
    
    # 2. 국내 지수 및 대표 종목 (FinanceDataReader)
    # KS11: 코스피, KQ11: 코스닥, 005930: 삼성전자, 000660: SK하이닉스
    kospi = fdr.DataReader('KS11').iloc[-1]
    kosdaq = fdr.DataReader('KQ11').iloc[-1]
    samsung = fdr.DataReader('005930').iloc[-1]
    hynix = fdr.DataReader('000660').iloc[-1]
    
    # 데이터 구조 생성
    new_data = {
        'Date': today,
        'USD_KRW': round(usdkrw, 1),
        'US_10Y': round(us10y, 2),
        'WTI': round(wti, 2),
        'KOSPI': round(kospi['Close'], 2),
        'KOSDAQ': round(kosdaq['Close'], 2),
        'Samsung': int(samsung['Close']),
        'Hynix': int(hynix['Close'])
    }
    
    df_new = pd.DataFrame([new_data])
    
    # CSV 파일 누적 관리
    csv_file = 'indicators_history.csv'
    if os.path.exists(csv_file):
        df_old = pd.read_csv(csv_file)
        df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['Date'], keep='last')
    else:
        df_combined = df_new
        
    df_combined.to_csv(csv_file, index=False)
    print(f"[{today}] 데이터 수집 완료!")

if __name__ == "__main__":
    fetch_daily_indicators()
