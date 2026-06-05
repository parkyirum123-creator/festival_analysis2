import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(page_title="축제 예산 대비 방문객 분석 대시보드", layout="wide")

# --- 1. 데이터베이스 스펙 및 SQL 쿼리 노출 ---
st.title("📊 축제 예산 및 방문객 성과 분석 대시보드")
st.subheader("1. 데이터 결합 및 추출 SQL Query")

sql_query = """
SELECT 
    b.축제명,
    b.광역단체지명,
    b.예산 AS '예산_억원',
    v.전체방문객수 AS '방문객수_명',
    b.연도
FROM 
    budget_table b
INNER JOIN 
    visitor_table v ON b.축제명 = v.축제명 AND b.연도 = v.연도
WHERE 
    b.연도 = 2025 -- 가장 최근 연도 분석 예시
ORDER BY 
    b.예산 DESC
LIMIT 7;
"""
st.code(sql_query, language='sql')

# --- 2. 가상 데이터 생성 (Pandas DataFrame) ---
# 예산 순위 TOP 7 축제 데이터 세팅
data = {
    '광역단체지명': ['강원도', '전라남도', '경상북도', '충청남도', '제주특별자치도', '경기도', '전라북도'],
    '축제명': ['눈꽃축제', '대나무축제', '불꽃축제', '머드축제', '유채꽃축제', '도자기축제', '비빔밥축제'],
    '예산_억원': [55, 48, 42, 38, 30, 25, 20],
    '방문객수_명': [120000, 450000, 310000, 520000, 280000, 110000, 190000],
    '연도': [2025, 2025, 2025, 2025, 2025, 2025, 2025]
}

df = pd.DataFrame(data)
# 예산 대비 방문객수(ROI) 계산
df['ROI'] = df['방문객수_명'] / df['예산_억원']

# --- 3. 시각화 (Chart 1 & 2) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Chart 1. TOP7 축제 예산 순위")
    # 예산 내림차순 정렬 (차트 표시를 위해)
    fig1 = px.bar(
        df, 
        x='예산_억원', 
        y='축제명', 
        orientation='h',
        color='예산_억원',
        color_continuous_scale='Blues',
        text='예산_억원',
        title="어떤 축제에 예산이 많이 들어가는가?"
    )
    fig1.update_layout(yaxis={'categoryorder':'total ascending'}) # 높은게 위로 오게 정렬
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("### Chart 2. 예산 vs 방문객 (이중축 콤보)")
    # 이중축 그래프 생성
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    # 막대 그래프 (예산)
    fig2.add_trace(
        go.Bar(x=df['축제명'], y=df['예산_억원'], name="예산(억원)", marker_color='rgba(100, 149, 237, 0.6)'),
        secondary_y=False,
    )

    # 선 그래프 (방문객수)
    fig2.add_trace(
        go.Scatter(x=df['축제명'], y=df['방문객수_명'], name="방문객수(명)", mode='lines+markers', line=dict(color='firebrick', width=3)),
        secondary_y=True,
    )

    fig2.update_layout(
        title_text="예산 투입 대비 실제 방문객 비교",
        xaxis_title="축제명",
        legend=dict(x=0.8, y=1.1, orientation="h")
    )

    fig2.update_yaxes(title_text="<b>예산</b> (억원)", secondary_y=False)
    fig2.update_yaxes(title_text="<b>방문객수</b> (명)", secondary_y=True)

    st.plotly_chart(fig2, use_container_width=True)

# --- 4. 실제 데이터 기반 동적 인사이트 레이아웃 ---
st.divider()
st.subheader("💡 데이터 분석 인사이트")

# 가성비 계산 로직
max_roi_festival = df.loc[df['ROI'].idxmax(), '축제명']
min_roi_festival = df.loc[df['ROI'].idxmin(), '축제명']

# 동적 매핑 3줄 요약
insight_1 = "① **[예산 투자 효율성 양극화]**: 상단 이중축 콤보 차트 분석 결과, 예산 투입량과 실제 방문객 수가 무조건 비례하지 않으며, 축제별 ROI(투자 대비 성과)의 양극화가 명확하게 관측됩니다."
insight_2 = f"② **[최고 가성비 축제 발견]**: 특히 **[{max_roi_festival}]**의 경우, 예산 투입은 적음에도 불구하고 독보적인 방문객 유치 성과를 보여주어 타 지자체가 최우선으로 벤치마킹해야 할 '고효율 가성비 모델'로 도출되었습니다."
insight_3 = f"③ **[하위권 개선 방안 제시]**: 반면, 예산 투입 대비 방문객 유입이 저조한 **[{min_roi_festival}]** 등은 예산 집행 구조를 전면 재검토하고, 디지털 정보시스템(MIS) 기반의 콘텐츠 질적 전환이 시급합니다."

st.markdown(insight_1)
st.markdown(insight_2)
st.markdown(insight_3)