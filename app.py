import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="지표추적자 무빙 대시보드", layout="wide")

# CSS 스타일링 (카드 디자인 및 폰트)
st.markdown("""
<style>
    .indicator-card {
        background-color: #1E222D;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 6px solid #4B5563;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .card-title {
        font-size: 16px;
        color: #9CA3AF;
        margin-bottom: 8px;
        font-weight: 600;
    }
    .card-movement {
        font-size: 22px;
        font-weight: 700;
        color: #F9FAFB;
        margin-bottom: 6px;
    }
    .up {
        color: #EF4444 !important; /* 상승: 빨강 */
    }
    .down {
        color: #3B82F6 !important; /* 하락: 파랑 */
    }
    .flat {
        color: #9CA3AF !important;
    }
    .card-sub {
        font-size: 13px;
        color: #6B7280;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 알상무 스타일 일일 지표 무빙 대시보드")
st.caption("어제 지표 ➔ 오늘 지표 (당일 변동폭 & 장중 무빙 추적)")

csv_file = 'indicators_history.csv'

if not os.path.exists(csv_file):
    st.warning("아직 수집된 데이터가 없습니다. GitHub Actions 실행을 기다려주세요.")
else:
    df = pd.read_csv(csv_file)
    
    # 지표 표시 이름 & 단위 매핑
    info_map = {
        'USD_KRW': {'title': '💵 원/달러 환율', 'unit': '원'},
        'US_10Y': {'title': '🇺🇸 미국채 10년물 금리', 'unit': '%'},
        'WTI': {'title': '🛢️ WTI 원유 선물', 'unit': '$'},
        'KOSPI': {'title': '🇰🇷 KOSPI 지수', 'unit': 'pt'},
        'KOSDAQ': {'title': '🇰🇷 KOSDAQ 지수', 'unit': 'pt'},
        'Samsung': {'title': '🏢 삼성전자', 'unit': '원'},
        'Hynix': {'title': '💾 SK하이닉스', 'unit': '원'}
    }
    
    st.subheader("🔥 6대 핵심 지표 당일 무빙 (전일 ➔ 금일)")
    
    # 2개 열(Columns)로 카드 배치
    col1, col2 = st.columns(2)
    
    for i, row in df.iterrows():
        ind = row['Indicator']
        if ind not in info_map:
            continue
            
        title = info_map[ind]['title']
        unit = info_map[ind]['unit']
        prev = f"{row['Prev_Close']:,}"
        curr = f"{row['Close']:,}"
        chg = row['Change']
        pct = row['Pct_Change']
        
        # 상승/하락 클래스 및 기호
        if chg > 0:
            color_class = "up"
            sign = "▲ +"
        elif chg < 0:
            color_class = "down"
            sign = "▼ "
        else:
            color_class = "flat"
            sign = "- "
            
        card_html = f"""
        <div class="indicator-card">
            <div class="card-title">{title}</div>
            <div class="card-movement">
                {prev} {unit} &nbsp;➔&nbsp; <span class="{color_class}">{curr} {unit}</span>
                <span class="{color_class}" style="font-size: 17px; margin-left: 10px;">
                    ({sign}{abs(chg):,} {unit}, {sign}{abs(pct):.2f}%)
                </span>
            </div>
            <div class="card-sub">
                당일 장중 범위: 저가 {row['Low']:,} ~ 고가 {row['High']:,} {unit} (시가: {row['Open']:,})
            </div>
        </div>
        """
        
        if i % 2 == 0:
            col1.markdown(card_html, unsafe_allow_html=True)
        else:
            col2.markdown(card_html, unsafe_allow_html=True)
            
    st.divider()
    
    # 당일 등락률(%) 한눈에 비교 바 차트
    st.subheader("📈 당일 등락률(%) 한눈에 비교")
    df['Name'] = df['Indicator'].map(lambda x: info_map.get(x, {}).get('title', x))
    fig_bar = px.bar(
        df,
        x='Name',
        y='Pct_Change',
        text='Pct_Change',
        color='Pct_Change',
        color_continuous_scale=['#3B82F6', '#9CA3AF', '#EF4444'],
        labels={'Pct_Change': '등락률 (%)', 'Name': '지표명'},
        title="지표별 전일 대비 등락률 (%)"
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)
