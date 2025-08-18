# app.py

import streamlit as st
import pandas as pd
import subprocess
from filters import sidebar_filters
from search import search_movies
# display.py에서 필요한 함수들을 명확하게 가져옵니다.
from display import show_movie_detail, display_movies_list
from streamlit_card import card

# --- 데이터 로딩 ---
@st.cache_data
def load_data():
    """CSV 파일을 로드하고 '매력도' 컬럼을 숫자형으로 변환합니다."""
    try:
        df = pd.read_csv("https://raw.githubusercontent/leejeongyeon-111/mysuni-SKreen/main/영화DB(임시).csv")
        df['매력도'] = pd.to_numeric(df['매력도'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("오류: './data/영화DB(임시).csv' 파일을 찾을 수 없습니다.")
        return None

# 데이터프레임 로드 및 페이지 설정
df = load_data()
st.set_page_config(layout="wide")

if df is None:
    st.stop()

# --- 세션 상태 초기화 ---
if "selected_movie_idx" not in st.session_state:
    st.session_state.selected_movie_idx = None
if "query" not in st.session_state:
    st.session_state.query = ""

# --- 상단 컨트롤 영역 ---
st.markdown("## 🎬 영화 검색하기")
search_col, button_col = st.columns([5, 1])
with search_col:
    st.session_state.query = st.text_input("검색어 입력", value=st.session_state.query, placeholder="영화 제목 입력", label_visibility="collapsed")
with button_col:
    if st.button("검색하기", use_container_width=True):
        st.session_state.selected_movie_idx = None
        st.rerun()

# --- 사이드바 ---
with st.sidebar:
    if st.button("🔄 데이터 업데이트"):
        with st.spinner("데이터를 수집하고 분석 중입니다..."):
            try:
                subprocess.run(["python", "./main.py"], check=True)
                st.success("✅ 데이터 업데이트 완료!")
                st.cache_data.clear()
                st.rerun()
            except (subprocess.CalledProcessError, FileNotFoundError):
                st.error("데이터 업데이트 중 오류가 발생했습니다.")

# ==========================================================
# --- ✅ 메인 콘텐츠 표시 (상세 페이지 vs 메인 페이지) ---
# ==========================================================

# 1. 상세 페이지 표시
# st.session_state.selected_movie_idx에 값이 있으면 이 블록만 실행됩니다.
if st.session_state.selected_movie_idx is not None:
    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.selected_movie_idx = None
        st.rerun()

    # 원본 df에서 인덱스로 영화 정보를 찾아 상세 페이지 함수 호출
    selected_row = df.iloc[st.session_state.selected_movie_idx]
    show_movie_detail(selected_row, df)

# 2. 메인 페이지 표시 (상세보기가 아닐 때)
# st.session_state.selected_movie_idx가 None이면 이 블록이 실행됩니다.
else:
    # "AI VoD 추천작" 섹션
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
            # streamlit-card를 사용해 포스터를 클릭 가능하게 만듭니다.
            has_clicked = card(
                title="", text="", image=row.get('url', ''), key=f"top5_{row.name}",
                styles={
                    "card": {
                        "width": "100%",
                        "height": "400px",
                        "margin": "0px",
                        "border-width": "0px",
                        "padding": "0px",
                        "box-shadow": "none"
                    },
                    "filter": {
                        "background-color": "rgba(0, 0, 0, 0)"  
                    }
                } 
            )
            if has_clicked:
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

    # "검색 결과" 섹션
    st.markdown("---")

    # 1. 항상 사이드바 필터를 생성하고, 사용자가 선택한 필터 값을 가져옵니다.
    filters = sidebar_filters(df)

    # 2. search_movies 함수를 한 번만 호출하여 필터링과 검색을 동시에 처리합니다.
    #    (이 함수는 검색어가 비어있을 때 필터만 적용해야 합니다.)
    results = search_movies(st.session_state.query, filters, df)

    # 3. 필터링 및 검색 결과에 따라 적절한 제목과 목록을 표시합니다.
    if not st.session_state.query:
        st.markdown("### 전체 영화 목록 DB")
        if results.empty:
            st.warning("선택한 필터에 해당하는 영화가 없습니다.")
        else:
            # 필터만 적용된 결과를 표시합니다.
            display_movies_list(results, df)
    else:
        st.markdown(f"**'{st.session_state.query}'**에 대한 검색 결과입니다. (필터 적용됨)")
        if results.empty:
            st.info(f"선택한 조건에 맞는 검색 결과가 없습니다.")
        else:
            # 검색어와 필터가 모두 적용된 결과를 표시합니다.
            display_movies_list(results, df)

