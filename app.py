import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정
st.set_page_config(page_title="축제 성과 분석 경영정보시스템", layout="wide")

# 2. SQL 쿼리문 노출 (화면 최상단)
st.title("📊 축제 예산 투자 대비 성과(ROI) 분석 대시보드")
st.markdown("### 1. 데이터베이스 스펙 및 3개년 평균 데이터 추출 SQL")

sql_query = """
SELECT 
    b.광역단체지명 AS '지역',
    v.축제명 AS '축제명',
    AVG(b.예산) AS '3개년_평균_예산_억원',
    AVG(v.전체방문객수) AS '3개년_평균_방문객수_명'
FROM 
    budget_table b
INNER JOIN 
    visitor_table v ON v.축제명 LIKE CONCAT('%', REPLACE(REPLACE(b.축제명, '2024 ', ''), '제61회 ', ''), '%') 
    AND b.연도 = v.연도
GROUP BY 
    b.광역단체지명, v.축제명;
"""
st.code(sql_query, language='sql')

# 3. 코드 내부 고정 데이터셋 생성 (제공된 정제 데이터 반영)
data = {
    '지역': ['부산', '대전', '경기', '부산', '전남', '부산', '대전'],
    '축제명': [
        '해운대모래축제', '대전 0시 축제', '수원화성문화제', 
        '해운대 빛축제', '화순 고인돌축제', '광복로 겨울빛축제', '유성국화축제'
    ],
    '평균예산': [48.11, 38.10, 18.62, 14.53, 11.63, 9.17, 4.32],
    '평균방문객수': [956273, 1753308, 385900, 3787196, 510483, 2001843, 694038]
}

df = pd.DataFrame(data)

# 예산 높은 순으로 정렬 (요구사항)
df = df.sort_values(by='평균예산', ascending=False).reset_index(drop=True)

# 4. 시각화 영역
st.markdown("### 2. 예산 대비 방문객 성과 시각화")
col1, col2 = st.columns(2)

with col1:
    st.subheader("차트 1. TOP7 축제 3개년 평균 예산 순위")
    # 가로 막대 그래프
    fig1 = px.bar(
        df,
        x='평균예산',
        y='축제명',
        orientation='h',
        text_auto='.2f',
        labels={'평균예산': '3개년 평균 예산(억원)', '축제명': '축제명'},
        color='평균예산',
        color_continuous_scale='Blues'
    )
    # 내림차순 정렬 유지 (Y축 역순 방지)
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("차트 2. 3개년 평균 예산 vs 방문객 (이중축)")
    # 이중축 콤보 차트 구성
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    # 막대 그래프 (예산 - 왼쪽 Y축)
    fig2.add_trace(
        go.Bar(
            x=df['축제명'], 
            y=df['평균예산'], 
            name="평균 예산(억원)", 
            marker_color='rgba(55, 128, 191, 0.7)'
        ),
        secondary_y=Fa