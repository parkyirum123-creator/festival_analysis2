import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(page_title="축제 데이터 분석 대시보드", layout="wide")

# 1. 화면 최상단 JOIN SQL 쿼리문 노출
st.subheader("📊 데이터 추출 SQL 쿼리 (3개년 평균 데이터)")
sql_query = """SELECT 
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
    b.광역단체지명, v.축제명;"""
st.code(sql_query, language='sql')

st.divider()

# 2. 코드 내부 데이터셋 선언 (리스트 구조)
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
# 예산 높은 순 정렬
df = df.sort_values(by="평균예산", ascending=False)

# 3. 시각화 세부 스펙 (차트 2개)

# 차트 1. TOP7 축제 3개년 평균 예산 순위 (가로 막대 그래프)
st.subheader("📉 차트 1. TOP7 축제 3개년 평균 예산 순위")
fig1 = px.bar(
    df, 
    x="평균예산", 
    y="축제명", 
    orientation='h', 
    title="축제별 평균 예산 (억원)",
    labels={"평균예산": "평균 예산 (억원)", "축제명": "축제명"},
    text_auto=True
)
fig1.update_layout(yaxis={'categoryorder': 'total ascending'}) # 정렬 유지
st.plotly_chart(fig1, use_container_width=True)

# 차트 2. 3개년 평균 예산 vs 방문객 (이중축 콤보 차트)
st.subheader("📈 차트 2. 3개년 평균 예산 vs 방문객 성과 분석")
fig2 = make_subplots(specs=[[{"secondary_y": True}]])

# 왼쪽 Y축: 예산 (막대)
fig2.add_trace(
    go.Bar(
        x=df["축제명"], 
        y=df["평균예산"], 
        name="평균예산(억원)", 
        marker_color='royalblue'
    ), 
    secondary_y=False
)

# 오른쪽 Y축: 방문객수 (선)
fig2.add_trace(
    go.Scatter(
        x=df["축제명"], 
        y=df["평균방문객수"], 
        name="평균방문객수(명)", 
        mode='lines+markers+text',
        line=dict(color='firebrick', width=3)
    ), 
    secondary_y=True
)

fig2.update_layout(
    title_text="예산 투입 대비 방문객 유치 성과 (이중축)",
    xaxis_title="축제명",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

fig2.update_yaxes(title_text="<b>예산</b> (억원)", secondary_y=False)
fig2.update_yaxes(title_text="<b>방문객수</b> (명)", secondary_y=True)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# 4. 고정형 핵심 인사이트 출력
st.subheader("💡 핵심 데이터 분석 인사이트")
st.markdown("""
- **① [데이터 기반 ROI 판정문]**: "상단 이중축 콤보 차트 분석 결과, 예산 투자 규모와 실제 방문객 수의 흐름이 일치하지 않으며, 이는 단순히 돈을 많이 쓴다고 해서 방문객이 비례하여 늘어나지 않음을 증명합니다."
- **② [최고 가성비 및 리스크 축제 팩트 체크]**: "실제 3개년 평균 데이터를 기준으로 보면, 가장 효율적인 성과를 낸 가성비 우수 축제는 예산 투입 대비 방문객이 압도적인 **[해운대 빛축제]**인 반면, 투입 예산 대비 성과 개선이 필요한 축제는 **[해운대모래축제]**로 분석됩니다."
- **③ [경영정보시스템(MIS)적 최종 해결책 제언]**: "따라서 향후 지자체들은 무조건적인 예산 증액 경쟁을 중단해야 합니다. 단 하나의 축제를 열더라도 디지털 정보시스템(MIS) 기반의 체류형 인프라 연계, 빅데이터 타겟 마케팅, 그리고 지역 독점적 킬러 콘텐츠 개발 같은 '질적 요소'를 강화하는 방향으로 행정 체질을 개선해야 합니다."
""")