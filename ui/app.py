# app.py

import streamlit as st


st.set_page_config(
    page_title="SKreen",
    layout="wide"
)

import pandas as pd
import subprocess
from filters import sidebar_filters
from search import search_movies
from display import show_movie_detail, display_movies_list

# (옵션) streamlit-card가 없을 때도 죽지 않게 가드
try:
    from streamlit_card import card
    HAS_CARD = True
except Exception:
    HAS_CARD = False

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    """CSV 파일을 로드하고 '매력도'를 숫자형으로 변환"""
    try:
        df = pd.read_csv('../data/영화DB(임시).csv')
        df['매력도'] = pd.to_numeric(df['매력도'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("오류: '../data/영화DB(임시).csv' 파일을 찾을 수 없습니다.")
        return None

# 데이터프레임 로드
df = load_data()
if df is None:
    st.stop()

# --- 세션 상태 ---
if "selected_movie_idx" not in st.session_state:
    st.session_state.selected_movie_idx = None
if "query" not in st.session_state:
    st.session_state.query = ""

# --- 상단 컨트롤 ---
st.markdown("## 🎬 영화 검색하기")
search_col, button_col = st.columns([5, 1])
with search_col:
    st.session_state.query = st.text_input("검색어 입력", value=st.session_state.query,
                                           placeholder="영화 제목 입력", label_visibility="collapsed")
with button_col:
    if st.button("검색하기", use_container_width=True):
        st.session_state.selected_movie_idx = None
        st.rerun()

# --- 사이드바 ---
with st.sidebar:
    if st.button("🔄 데이터 업데이트"):
        with st.spinner("데이터를 수집하고 분석 중입니다..."):
            try:
                subprocess.run(["python", "./main.py"], check=True)  # 필요시 같은 인터프리터로 교체: [sys.executable, "main.py"]
                st.success("✅ 데이터 업데이트 완료!")
                st.cache_data.clear()
                st.rerun()
            except (subprocess.CalledProcessError, FileNotFoundError):
                st.error("데이터 업데이트 중 오류가 발생했습니다.")

# ==========================================================
# --- ✅ 메인 콘텐츠 표시 (상세 페이지 vs 메인 페이지) ---
# ==========================================================
if st.session_state.selected_movie_idx is not None:
    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.selected_movie_idx = None
        st.rerun()

    selected_row = df.iloc[st.session_state.selected_movie_idx]
    show_movie_detail(selected_row, df)

else:
    st.markdown("---")
    gradient_style = """
        background-image: linear-gradient(to right, #AA0000, #FFFFFF);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        font-weight: bold;
    """
    st.markdown(f"<h2 style='{gradient_style}'>✨ AI추천 매력도 Top5 VOD</h2>", unsafe_allow_html=True)

    top_5_movies = df.dropna(subset=['매력도']).sort_values(by='매력도', ascending=False).head(5)
    poster_cols = st.columns(5)
    for i, (_, row) in enumerate(top_5_movies.iterrows()):
        with poster_cols[i]:
            clicked = False
            if HAS_CARD:
                clicked = card(
                    title="", text="", image=row.get('url', ''), key=f"top5_{row.name}",
                    styles={
                        "card": {"width": "100%", "height": "400px", "margin": "0px", "border-width": "0px",
                                 "padding": "0px", "box-shadow": "none"},
                        "filter": {"background-color": "rgba(0, 0, 0, 0)"}
                    }
                )
            else:
                # 간단 폴백
                st.image(row.get('url', ''), use_container_width=True)
            if clicked:
                st.session_state.selected_movie_idx = row.name
                st.rerun()

            st.markdown(
                f"""
                <div style="text-align: center;">
                    <b>{row['영화명']}</b><br>
                    <small>매력도: {int(row['매력도']):,}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # 1) 사이드바 필터 수집
    filters = sidebar_filters(df)

    # 2) 검색+필터 한번에
    results = search_movies(st.session_state.query, filters, df)

    # 3) 결과 표시
    if not st.session_state.query:
        st.markdown("### 전체 영화 목록 DB")
        if results.empty:
            st.warning("선택한 필터에 해당하는 영화가 없습니다.")
        else:
            display_movies_list(results, df)
    else:
        st.markdown(f"**'{st.session_state.query}'**에 대한 검색 결과입니다. (필터 적용됨)")
        if results.empty:
            st.info("선택한 조건에 맞는 검색 결과가 없습니다.")
        else:
            display_movies_list(results, df)

