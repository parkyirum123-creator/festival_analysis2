import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 페이지 설정
st.set_page_config(page_title="3개년 평균 축제 성과 분석", layout="wide")

# --- 1. 데이터 로드 및 3개년 평균 전처리 ---
@st.cache_data
def get_avg_data():
    # 방문자 데이터
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
    
    # 예산 데이터
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

    # 매칭을 위한 이름 전처리 (공백 제거)
    v_df['match_key'] = v_df['축제명'].str.replace(' ', '')
    b_df['match_key'] = b_df['축제명'].str.replace(' ', '')

    # JOIN
    merged = pd.merge(b_df, v_df, on=['match_key', '연도'], suffixes=('', '_v'))
    
    # 3개년 평균 계산
    avg_df = merged.groupby(['match_key', '지역']).agg({
        '축제명': 'first',
        '예산': 'mean',
        '방문객수': 'mean'
    }).reset_index()

    # ROI 계산 및 정렬
    avg_df['ROI'] = avg_df['방문객수'] / avg_df['예산']
    return avg_df.sort_values('예산', ascending=False).head(7)

df_avg = get_avg_data()

# --- 2. SQL 쿼리 노출 (3개년 평균 산출 쿼리) ---
st.title("📊 3개년 평균 축제 예산 대비 성과 분석")
st.subheader("1. 3개년 평균 데이터 추출 SQL Query")
st.code("""
SELECT 
    b.축제명,
    AVG(b.예산) AS '평균예산_억원',
    AVG(v.전체방문객수) AS '평균방문객수_명'
FROM 
    budget_table b
INNER JOIN 
    visitor_table v ON REPLACE(b.축제명, ' ', '') = REPLACE(v.축제명, ' ', '') 
    AND b.연도 = v.연도
GROUP BY 
    REPLACE(b.축제명, ' ', '')
ORDER BY 
    평균예산_억원 DESC
LIMIT 7;
""", language='sql')

# --- 3. 시각화 영역 ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 차트 1. TOP7 축제 평균 예산 순위")
    fig1 = px.bar(
        df_avg, 
        x='예산', 
        y='축제명', 
        orientation='h',
        color='예산',
        color_continuous_scale='GnBu',
        text_auto='.1f',
        labels={'예산': '3개년 평균 예산(억원)'}
    )
    fig1.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("#### 차트 2. 평균 예산 vs 평균 방문객 (이중축)")
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig2.add_trace(
        go.Bar(x=df_avg['축제명'], y=df_avg['예산'], name="평균 예산(억원)", marker_color='rgba(158,202,225,0.8)'),
        secondary_y=False,
    )
    fig2.add_trace(
        go.Scatter(x=df_avg['축제명'], y=df_avg['방문객수'], name="평균 방문객수(명)", 
                   mode='lines+markers+text', text=df_avg['방문객수'].apply(lambda x: f'{x/10000:.0f}만'),
                   textposition="top center", line=dict(color='orange', width=4)),
        secondary_y=True,
    )
    
    fig2.update_layout(title_text="예산 투입 대비 방문객 유치 효율 (3개년 평균)")
    fig2.update_yaxes(title_text="평균 예산 (억원)", secondary_y=False)
    fig2.update_yaxes(title_text="평균 방문객수 (명)", secondary_y=True)
    st.plotly_chart(fig2, use_container_width=True)

# --- 4. 실제 데이터 기반 동적 인사이트 ---
st.divider()
st.subheader("💡 3개년 통합 분석 인사이트")

# 분석용 변수 도출
highest_budget_fest = df_avg.iloc[0] # 예산 1위
best_efficiency_fest = df_avg.loc[df_avg['ROI'].idxmax()] # 가성비 1위
worst_efficiency_fest = df_avg.loc[df_avg['ROI'].idxmin()] # 가성비 최하위

st.markdown(f"""
- **① [예산 투자 효율성 양극화]**: 3개년 평균 분석 결과, **[{highest_budget_fest['축제명']}]**은 평균 {highest_budget_fest['예산']:.1f}억이라는 최대 예산을 투입했음에도 불구하고, 예산 규모가 훨씬 적은 타 축제들보다 평균 방문객 유입이 낮거나 비슷한 수준으로 나타났습니다. 이는 **예산 증액이 곧 방문객 수의 비례적 증가로 이어지지 않는다**는 사실을 데이터로 입증합니다.
- **② [최고 가성비 축제 발견]**: 반면, **[{best_efficiency_fest['축제명']}]**의 경우 3개년 평균 예산 대비 방문객 유치 성과(ROI)가 가장 압도적입니다. 이는 예산 규모보다는 해당 축제만이 가진 고유한 콘텐츠 경쟁력이나 자연 발생적인 집객 요인이 효율성을 결정짓는 핵심 지표임을 보여주며, 타 지자체의 벤치마킹 1순위 모델입니다.
- **③ [하위권 개선 방안 제시]**: 예산 투입 대비 효율이 저조한 **[{worst_efficiency_fest['축제명']}]** 등은 단순한 예산 증액보다는 방문객의 니즈를 재분석해야 합니다. 대형 가수 초청 등 일회성 비용 지출을 줄이고, 자발적 SNS 확산을 유도하는 포토존 강화나 디지털 기술을 접목한 스마트 관광 시스템(MIS) 구축을 통해 운영 구조를 혁신해야 합니다.
""")