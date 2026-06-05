import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. 페이지 설정
st.set_page_config(page_title="축제 성과 분석 시스템", layout="wide")

# 2. 화면 최상단 JOIN SQL 쿼리문 노출
st.title("📊 축제 예산 투자 대비 성과(ROI) 데이터 대시보드")
st.markdown("### 1. 데이터베이스 3개년 평균 데이터 추출 SQL")

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

# 3. 데이터셋 선언 (에러 방지를 위해 가장 단순한 리스트 구조 사용)
# [괄호 매칭 검증 완료]
data = [
    ["해운대모래축제", 48.11, 956273],
    ["대전 0시 축제", 38.10, 1753308],
    ["수원화성문화제", 18.62, 385900],
    ["해운대 빛축제", 14.53, 3787196],
    ["화순 고인돌축제", 11.63, 510483],
    ["광복로 겨울빛축제", 9.17, 2001843],
    ["유성국화축제", 4.32, 694038]
]

df = pd.DataFrame(data, columns=["축제명", "평균예산", "평균방문객수"])

# [정렬] 예산 높은 순(내림차순)
df = df.sort_values(by="평균예산", ascending=False)

# 4. 시각화 영역
st.markdown("### 2. 투자 예산 순위 및 방문객 성과 지표")
col1, col2 = st.columns(2)

with col1:
    st.subheader("차트 1. TOP7 축제 3개년 평균 예산 순위")
    # 가로 막대 그래프
    fig1 = px.bar(
        df,
        x="평균예산",
        y="축제명",
        orientation="h",
        text_auto=".2f",
        labels={"평균예산": "평균 예산(억원)", "축제명": "축제명"},
        color="평균예산",
        color_continuous_scale="Blues"
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("차트 2. 3개년 평균 예산 vs 방문객 성과")
    # 이중축 콤보 차트 생성 (괄호 매칭 검증 완료)
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])

    # 막대 그래프: 예산 (왼쪽 Y축)
    fig2.add_trace(
        go.Bar(
            x=df["축제명"],
            y=df["평균예산"],
            name="평균 예산(억원)",
            marker_color="rgba(135, 206, 250, 0.8)"
        ),
        secondary_y=False
    )

    # 선 그래프: 방문객수 (오른쪽 Y축)
    fig2.add_trace(
        go.Scatter(
            x=df["축제명"],
            y=df["평균방문객수"],
            name="평균 방문객수(명)",
            mode="lines+markers",
            line=dict(color="firebrick", width=3)
        ),
        secondary_y=True
    )

    fig2.update_layout(
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=50, b=20)
    )

    fig2.update_yaxes(title_text="평균 예산 (억원)", secondary_y=False)
    fig2.update_yaxes(title_text="평균 방문객 수 (명)", secondary_y=True)

    st.plotly_chart(fig2, use_c