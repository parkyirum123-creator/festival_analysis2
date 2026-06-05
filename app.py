import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정 및 레이아웃
st.set_page_config(page_title="축제 성과 분석 대시보드", layout="wide")

# 2. 화면 최상단 JOIN SQL 쿼리문 노출
st.title("📊 축제 예산 투자 대비 성과(ROI) 분석")
st.markdown("### 1. 데이터 전처리 및 복합 JOIN SQL")

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

# 3. 코드 내부 정제 데이터셋 생성 (제공된 수치 반영)
data = {
    '축제명': [
        '해운대모래축제', '대전 0시 축제', '수원화성문화제', 
        '해운대 빛축제', '화순 고인돌축제', '광복로 겨울빛축제', '유성국화축제'
    ],
    '평균예산': [48.11, 38.10, 18.62, 14.53, 11.63, 9.17, 4.32],
    '평균방문객수': 