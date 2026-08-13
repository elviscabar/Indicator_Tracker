import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="지표추적자 대시보드", layout="wide")

st.title("📈 알상무 스타일 매일 지표 추적 대시보드")
st.caption("자동 업데이트되는 매크로 / 지수 / 대표 종목 가격 지표")

csv_file = 'indicators_history.csv'

if not os.path.exists(csv_file):
    st.warning("아직 수집된 데이터가 없습니다. GitHub Actions 실행을 기다려주세요.")
else:
    df = pd.read_csv(csv_file)
    latest = df.iloc[-1]
    
    # 상단 핵심 메트릭 카드 4종
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("원/달러 환율", f"{latest['USD_KRW']:,} 원")
    col2.metric("미국채 10년 금리", f"{latest['US_10Y']}%")
    col3.metric("WTI 유가", f"${latest['WTI']}")
    col4.metric("KOSPI 지수", f"{latest['KOSPI']:,} pt")
    
    st.divider()
    
    # 차트 섹션 1: KOSPI / KOSDAQ 추이
    st.subheader("📊 지수 추이 (KOSPI & KOSDAQ)")
    fig_idx = px.line(df, x='Date', y=['KOSPI', 'KOSDAQ'], markers=True)
    st.plotly_chart(fig_idx, use_container_width=True)
    
    # 차트 섹션 2: 삼성전자 / SK하이닉스 주가 추이
    st.subheader("🏢 대표 주도주 주가 추이 (삼성전자 & SK하이닉스)")
    fig_stock = px.line(df, x='Date', y=['Samsung', 'Hynix'], markers=True)
    st.plotly_chart(fig_stock, use_container_width=True)
