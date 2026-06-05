import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(page_title="축제 예산 대비 방문객 성과 분석 시스템", layout="wide")

# 제목 및 서브타이틀
st.title("📊 축제 예산 투자 대비 성과(ROI) 분석 시스템")
st.markdown("### 1. [데이터 전처리] 복합 JOIN 및 텍스트 정제 SQL")

# 1. SQL 쿼리문 노출 (요구사항 반영)
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

# 2. 데이터셋 생성 (7개 필수 축제 포함)
data = {
    '지역': ['부산', '대전', '경기', '부산', '전남', '부산', '대전'],
    '축제명': ['해운대 빛축제', '대전 0시 축제', '수원화성문화제', '해운대 모래축제', '화순 고인돌축제', '광복로 겨울빛축제', '유성국화축제'],
    '예산': [12.5, 29.0, 35.2, 11.0, 18.5, 9.5, 7.2],  # 억원 단위
    '방문객수': [1100000, 1090000, 1500000, 2100000, 450000, 850000, 600000] # 명 단위
}

df = pd.DataFrame(data)
# 예산 높은 순 정렬
df = df.sort_values(by='예산', ascending=False)

# 3. 시각화 레이아웃
col1, col2 = st.columns(2)

with col1:
    st.subheader("차트 1. TOP7 축제 3개년 평균 예산 순위")
    fig1 = px.bar(
        df, 
        x='예산', 
        y='축제명', 
        orientation='h',
        text='예산',
        labels={'예산': '3개년 평균 예산 (억원)', '축제명': '축제명'},
        color='예산',
        color_continuous_scale='Blues'
    )
    fig1.update_traces(texttemplate='%{text}억', textposition='outside')
    fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("차트 2. 예산 vs 방문객 성과 비교 (이중축)")
    
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 막대 그래프 (예산)
    fig2.add_trace(
        go.Bar(x=df['축제명'], y=df['예산'], name="평균 예산(억원)", marker_color='royalblue'),
        secondary_