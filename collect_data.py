import datetime
import os
import pandas as pd
import yfinance as yf
import FinanceDataReader as fdr

def get_latest_data():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 1. 해외 매크로 지표
    us10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
    wti = yf.Ticker("CL=F").history(period="1d")['Close'].iloc[-1]
    usdkrw = yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]
    
    # 2. 국내 지수 및 종목
    kospi = fdr.DataReader('KS11').iloc[-1]['Close']
    kosdaq = fdr.DataReader('KQ11').iloc[-1]['Close']
    samsung = fdr.DataReader('005930').iloc[-1]['Close']
    hynix = fdr.DataReader('000660').iloc[-1]['Close']
    
    return {
        'Date': today,
        'USD_KRW': round(float(usdkrw), 1),
        'US_10Y': round(float(us10y), 2),
        'WTI': round(float(wti), 2),
        'KOSPI': round(float(kospi), 2),
        'KOSDAQ': round(float(kosdaq), 2),
        'Samsung': int(samsung),
        'Hynix': int(hynix)
    }

def fetch_and_update_indicators():
    csv_file = 'indicators_history.csv'
    
    # 파일이 없으면 과거 60일치 초기화 생성
    if not os.path.exists(csv_file):
        print("초기 과거 데이터 수집 시작...")
        end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime('%Y-%m-%d')
        
        df_kospi = fdr.DataReader('KS11', start_date, end_date)[['Close']].rename(columns={'Close': 'KOSPI'})
        df_kosdaq = fdr.DataReader('KQ11', start_date, end_date)[['Close']].rename(columns={'Close': 'KOSDAQ'})
        df_samsung = fdr.DataReader('005930', start_date, end_date)[['Close']].rename(columns={'Close': 'Samsung'})
        df_hynix = fdr.DataReader('000660', start_date, end_date)[['Close']].rename(columns={'Close': 'Hynix'})
        
        # yfinance 데이터
        us10y = yf.Ticker("^TNX").history(start=start_date, end=end_date)['Close'].to_frame('US_10Y')
        wti = yf.Ticker("CL=F").history(start=start_date, end=end_date)['Close'].to_frame('WTI')
        usdkrw = yf.Ticker("KRW=X").history(start=start_date, end=end_date)['Close'].to_frame('USD_KRW')
        
        # Index의 timezone 제거
        for df_item in [us10y, wti, usdkrw]:
            df_item.index = df_item.index.tz_localize(None)
            
        # 데이터프레임 병합
        df_init = df_kospi.join([df_kosdaq, df_samsung, df_hynix, us10y, wti, usdkrw], how='inner').dropna()
        df_init.reset_index(inplace=True)
        df_init['Date'] = df_init['Date'].dt.strftime('%Y-%m-%d')
        
        # 반올림 및 정수 변환
        df_init['USD_KRW'] = df_init['USD_KRW'].round(1)
        df_init['US_10Y'] = df_init['US_10Y'].round(2)
        df_init['WTI'] = df_init['WTI'].round(2)
        df_init['KOSPI'] = df_init['KOSPI'].round(2)
        df_init['KOSDAQ'] = df_init['KOSDAQ'].round(2)
        df_init['Samsung'] = df_init['Samsung'].astype(int)
        df_init['Hynix'] = df_init['Hynix'].astype(int)
        
        # 컬럼 순서 정렬
        df_init = df_init[['Date', 'USD_KRW', 'US_10Y', 'WTI', 'KOSPI', 'KOSDAQ', 'Samsung', 'Hynix']]
        df_init.to_csv(csv_file, index=False)
        print("과거 60일 데이터 생성 완료!")
    
    # 일별 데이터 업데이트 (당일 데이터 추가)
    new_data = get_latest_data()
    df_old = pd.read_csv(csv_file)
    df_new = pd.DataFrame([new_data])
    
    df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=['Date'], keep='last')
    df_combined.to_csv(csv_file, index=False)
    print("오늘자 데이터 업데이트 완료!")

if __name__ == "__main__":
    fetch_and_update_indicators()
