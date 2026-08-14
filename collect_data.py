import datetime
import os
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr

def fetch_and_update_indicators():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"[{today}] 6대 핵심 지표 당일 무빙 수집 중...")
    
    indicators = {}
    
    # 1. 국내 지표 및 종목 (FinanceDataReader)
    targets_fdr = {
        'KOSPI': 'KS11',
        'KOSDAQ': 'KQ11',
        'Samsung': '005930',
        'Hynix': '000660'
    }
    
    for name, code in targets_fdr.items():
        df = fdr.DataReader(code, start=start_date)
        if len(df) >= 2:
            prev_close = df.iloc[-2]['Close']
            today_row = df.iloc[-1]
            indicators[name] = {
                'Prev_Close': round(float(prev_close), 2 if name in ['KOSPI', 'KOSDAQ'] else 0),
                'Open': round(float(today_row['Open']), 2 if name in ['KOSPI', 'KOSDAQ'] else 0),
                'High': round(float(today_row['High']), 2 if name in ['KOSPI', 'KOSDAQ'] else 0),
                'Low': round(float(today_row['Low']), 2 if name in ['KOSPI', 'KOSDAQ'] else 0),
                'Close': round(float(today_row['Close']), 2 if name in ['KOSPI', 'KOSDAQ'] else 0),
            }
            
    # 2. 글로벌 매크로 지표 (yfinance)
    targets_yf = {
        'USD_KRW': 'KRW=X',
        'US_10Y': '^TNX',
        'WTI': 'CL=F'
    }
    
    for name, ticker in targets_yf.items():
        df = yf.Ticker(ticker).history(period="5d")
        if len(df) >= 2:
            prev_close = df.iloc[-2]['Close']
            today_row = df.iloc[-1]
            indicators[name] = {
                'Prev_Close': round(float(prev_close), 2),
                'Open': round(float(today_row['Open']), 2),
                'High': round(float(today_row['High']), 2),
                'Low': round(float(today_row['Low']), 2),
                'Close': round(float(today_row['Close']), 2),
            }
            
    # 지표별 변동 계산
    records = []
    for k, v in indicators.items():
        change = round(v['Close'] - v['Prev_Close'], 2)
        pct_change = round((change / v['Prev_Close']) * 100, 2)
        records.append({
            'Date': today,
            'Indicator': k,
            'Prev_Close': v['Prev_Close'],
            'Open': v['Open'],
            'High': v['High'],
            'Low': v['Low'],
            'Close': v['Close'],
            'Change': change,
            'Pct_Change': pct_change
        })
        
    df_result = pd.DataFrame(records)
    csv_file = 'indicators_history.csv'
    df_result.to_csv(csv_file, index=False)
    print("수집 및 저장 완료!")

if __name__ == "__main__":
    fetch_and_update_indicators()
