import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(page_title="3개년 축제 성과 분석", layout="wide")

# --- 1. 데이터 로드 및 정제 ---
@st.cache_data
def get_data():
    # 방문자 데이터 (Raw)
    visitor_raw = [
        ["부산", "해운대 빛축제", 3787000, 2023], ["대전", "대전 0시 축제", 1090120, 2023],
        ["부산", "해운대모래축제", 853000, 2023], ["전남", "화순 고인돌 가을꽃 축제", 506150, 2023],
        ["경기", "수원화성문화제", 201011, 2023], ["부산", "광복로 겨울빛 트리축제", 0, 2023],
        ["부산", "해운대 빛축제", 3879810, 2024], ["부산", "광복로 겨울빛 트리축제", 2900000, 2024],
        ["대전", "대전 0시 축제", 2008240, 2024], ["부산", "해운대모래축제", 1009910, 2024],
        ["대전", "유성국화축제", 683921, 2024], ["전남", "화순 고인돌 가을꽃 축제", 315300, 2024],
        ["경기", "수원화성문화제", 246537, 2024], ["부산", "해운대 빛축제", 3694744, 2025],
        ["부산", "광복로 겨울빛 트리축제", 3105529, 2025], ["대전", "대전 0시 축제", 2161566, 2025],
        ["부산", "해운대모래축제", 1009910, 2025], ["전남", "화순 고인돌 가을꽃 축제", 710000, 2025],
        ["경기", "수원화성문화제", 709154, 2025], ["대전", "유성국화축제", 704156, 2025]
    ]
    
    # 예산 데이터 (Raw) - 이름 정제 포함
    budget_raw = [
        ["해운대모래축제", 68.04, 2023], ["대전 0시 축제", 33.5, 2023], ["수원화성문화제", 15.72, 2023],
        ["화순 고인돌 가을꽃 축제", 10, 2023], ["광복로 겨울빛 트리축제", 9, 2023],
        ["광복로 겨울빛 트리축제", 9, 2024], ["대전 0시 축제", 33.5, 2024], ["해운대모래축제", 68.04, 2024],
        ["화순 고인돌 가을꽃 축제", 10, 2024], ["수원화성문화제", 15.72, 2024],
        ["광복로 겨울빛 트리축제", 9.5, 2025], ["대전 0시 축제", 47.3, 2025], ["유성국화축제", 6.14, 2025],
        ["해운대모래축제", 8.24, 2025], ["화순 고인돌 가을꽃 축제", 14.9, 2025], ["수원화성문화제", 24.43, 2025]
    ]

    v_df = pd.DataFrame(visitor_raw, columns=['지역', '축제명', '방문객수', '연도'])
    b_df = pd.DataFrame(budget_raw, columns=['축제명', '예산', '연도'])

    # 이름 띄어쓰기 등 공통화 작업
    v_df['match_key'] = v_df['축제명'].str.replace(' ', '')
    b_df['match_key'] = b_df['축제명'].str.replace(' ', '')

    # JOIN (연도와 이름 기준)
    merged = pd.merge(b_df, v_df, on=['match_key', '연도'], suffixes=('', '_v'))
    return merged[['연도', '지역', '축제명', '예산', '방문객수']]

df = get_data()

# --- 2. SQL 쿼리 노출 ---
st.title("📊 3개년 축제 예산 대비 방문객 성과 분석")
st.markdown("### 1. 데이터베이스 통합 SQL 쿼리")
st.code("""
SELECT 
    b.축제명,
    b.예산 AS '예산_억원',
    v.전체방문객수 AS '방문객수_명',
    b.연도
FROM budget_table b
INNER JOIN visitor_table v 
    ON REPLACE(b.축제명, ' ', '') = REPLACE(v.축제명, ' ', '') 
    AND b.연도 = v.연도
WHERE b.연도 = 2025
ORDER BY b.예산 DESC;
""", language='sql')

# --- 3. 시각화 영역 (2025년 기준) ---
df_2025 = df[df['연도'] == 2025].sort_values('예산', ascending=False)
df_2025['ROI'] = df_2025['방문객수'] / df_2025['예산']

col1, col2 = st.columns(2)

with col1:
    st.subheader("TOP 축제 예산 순위 (2025)")
    fig1 = px.bar(df_2025, x='예산', y='축제명', orientation='h', 
                 color='예산', color_continuous_scale='Viridis',
                 labels={'예산':'예산(억원)'}, text_auto=True)
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("예산 vs 방문객 성과 비교")
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(go.Bar(x=df_2025['축제명'], y=df_2025['예산'], name="예산(억원)", marker_color='gray'), secondary_y=False)
    fig2.add_trace(go.Scatter(x=df_2025['축제명'], y=df_2025['방문객수'], name="방문객수(명)", mode='lines+markers+text',
                              line=dict(color='red', width=3)), secondary_y=True)
    fig2.update_yaxes(title_text="예산 (억원)", secondary_y=False)
    fig2.update_yaxes(title_text="방문객수 (명)", secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)

# --- 4. 실제 데이터 기반 인사이트 분석 ---
st.divider()
st.subheader("📝 데이터 기반 실질적 성과 분석")

# 분석 변수 추출
most_expensive_festival = df_2025.iloc[0]['축제명']
most_expensive_budget = df_2025.iloc[0]['예산']
most_expensive_visitors = df_2025.iloc[0]['방문객수']

best_roi_festival = df_2025.loc[df_2025['ROI'].idxmax(), '축제명']
worst_roi_festival = df_2025.loc[df_2025['ROI'].idxmin(), '축제명']

# 3개년 추세 분석 (대전 0시 축제 예시)
dj_trend = df[df['축제명'] == '대전 0시 축제']
dj_budget_growth = dj_trend[dj_trend['연도']==2025]['예산'].values[0] - dj_trend[dj_trend['연도']==2023]['예산'].values[0]

# 동적 인사이트 출력
st.markdown(f"""
- **① [예산 투자 효율성 양극화]**: 분석 결과, 가장 많은 예산({most_expensive_budget}억)을 투입한 **{most_expensive_festival}**의 방문객 수는 약 {most_expensive_visitors/10000:.1f}만 명으로 집계되었습니다. 이는 예산 투입량과 방문객 수가 반드시 비례하지 않음을 보여주며, 축제 규모 확대를 위한 예산 증액이 곧바로 압도적인 방문객 유치로 이어지지는 않는 '성장통' 구간이 관측됩니다.
- **② [최고 가성비 축제 발견]**: 특히 **[{best_roi_festival}]**의 경우, 예산 투입 대비 방문객 유치 성과(ROI)가 전체 축제 중 가장 높게 나타났습니다. 이는 대규모 홍보비 집행보다 지역 특화 콘텐츠의 매력도와 접근성이 방문객 유입에 더 핵심적인 역할을 하고 있음을 시사하며, 타 지자체가 최우선으로 벤치마킹해야 할 모델입니다.
- **③ [하위권 개선 방안 제시]**: 반면, 예산 규모 대비 성과가 정체된 **[{worst_roi_festival}]** 등은 단순히 예산액을 조정하는 것을 넘어, 방문객 체류 시간을 늘릴 수 있는 체험형 콘텐츠 강화나 디지털 기반의 타겟 마케팅(MIS) 도입 등 질적 전환이 시급히 요구됩니다.
""")