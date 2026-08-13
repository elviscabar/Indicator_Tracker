import datetime
import os
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr

def fetch_historical_indicators():
    # 과거 1년치 데이터 한 번에 수집
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 1. 해외 매크로 지표
    us10y = yf.download("^TNX", start=start_date, end=end_date)['Close']
    wti = yf.download("CL=F", start=start_date, end=end_date)['Close']
    usdkrw = yf.download("KRW=X", start=start_date, end=end_date)['Close']
    
    # 2. 국내 지수 및 대표 종목
    kospi = fdr.DataReader('KS11', start_date, end_date)['Close']
    kosdaq = fdr.DataReader('KQ11', start_date, end_date)['Close']
    samsung = fdr.DataReader('005930', start_date, end_date)['Close']
    hynix = fdr.DataReader('000660', start_date, end_date)['Close']
    
    # 데이터프레임 병합
    df = pd.DataFrame({
        'USD_KRW': usdkrw.round(1),
        'US_10Y': us10y.round(2),
        'WTI': wti.round(2),
        'KOSPI': kospi.round(2),
        'KOSDAQ': kosdaq.round(2),
        'Samsung': samsung.fillna(0).astype(int),
        'Hynix': hynix.fillna(0).astype(int)
    }).dropna()
    
    df.reset_index(inplace=True)
    df.rename(columns={'Date': 'Date'}, inplace=True)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    df.to_csv('indicators_history.csv', index=False)
    print("과거 1년치 데이터 수집 완료!")

if __name__ == "__main__":
    fetch_historical_indicators()
