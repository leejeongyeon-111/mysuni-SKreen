# app.py

import streamlit as st

# ✅ 가장 먼저 페이지 설정
st.set_page_config(page_title="SKreen", layout="wide")

import pandas as pd
from pathlib import Path
import sys, os

from filters import sidebar_filters
from search import search_movies
from display import show_movie_detail, display_movies_list

# streamlit-card가 없을 때 안 죽도록 가드
try:
    from streamlit_card import card
    HAS_CARD = True
except Exception:
    HAS_CARD = False

# --- 데이터 로딩 ---
RAW_URL = "https://raw.githubusercontent.com/leejeongyeon-111/mysuni-SKreen/main/data/%E1%84%8B%E1%85%A7%E1%86%BC%E1%84%92%E1%85%AADB(%E1%84%8B%E1%85%B5%E1%86%B7%E1%84%89%E1%85%B5).csv"

@st.cache_data
def load_data():
    """원격 CSV를 로드하고 '매력도'를 숫자형으로 변환 (실패 시 None 반환)."""
    try:
        # 인코딩 안전 시도
        for enc in ("utf-8-sig", "cp949", "utf-8"):
            try:
                df = pd.read_csv(RAW_URL, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            df = pd.read_csv(RAW_URL)

        if "매력도" in df.columns:
            df["매력도"] = pd.to_numeric(df["매력도"], errors="coerce")
        return df
    except Exception:
        # 원격 실패 시 None (화면에서 업로더 폴백 처리)
        return None

# 데이터프레임 로드
df = load_data()

# 원격 실패 → 업로더 폴백 (오류 대신 안내)
if df is None:
    st.info("원격 CSV를 불러오지 못했어요. 아래에서 파일을 업로드하면 바로 진행할게요.")
    up = st.file_uploader("CSV 업로드", type=["csv"])
    if up:
        # 업로드 파일도 인코딩 안전 처리
        for enc in ("utf-8-sig", "cp949", "utf-8"):
            try:
                df = pd.read_csv(up, encoding=enc)
                break
            except UnicodeDecodeError:
                up.seek(0)
                continue
        else:
            up.seek(0)
            df = pd.read_csv(up)
        if "매력도" in df.columns:
            df["매력도"] = pd.to_numeric(df["매력도"], errors="coerce")
        st.success("업로드한 CSV로 진행할게요.")
    else:
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
    st.session_state.query = st.text_input(
        "검색어 입력",
        value=st.session_state.query,
        placeholder="영화 제목 입력",
        label_visibility="collapsed"
    )
with button_col:
    if st.button("검색하기", use_container_width=True):
        st.session_state.selected_movie_idx = None
        st.rerun()

# --- 사이드바 (배포 안전: 캐시 새로고침만) ---
with st.sidebar:
    if st.button("🔄 원격 CSV 새로고침"):
        st.cache_data.clear()
        st.rerun()

# ==========================================================
# --- ✅ 메인 콘텐츠 표시 (상세 페이지 vs 메인 페이지) ---
# ==========================================================

# 1) 상세 페이지
if st.session_state.selected_movie_idx is not None:
    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.selected_movie_idx = None
        st.rerun()

    selected_row = df.iloc[st.session_state.selected_movie_idx]
    show_movie_detail(selected_row, df)

# 2) 메인 페이지
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

    top_5_movies = (
        df.dropna(subset=["매력도"])
          .sort_values(by="매력도", ascending=False)
          .head(5)
    )
    poster_cols = st.columns(5)

    for i, (idx, row) in enumerate(top_5_movies.iterrows()):
        with poster_cols[i]:
            poster_url = row.get("url", "") or row.get("poster_url", "") or row.get("image", "")
            clicked = False

            if HAS_CARD and poster_url:
                try:
                    clicked = card(
                        title="", text="", image=poster_url, key=f"top5_{idx}",
                        styles={
                            "card": {
                                "width": "100%", "height": "400px",
                                "margin": "0px", "border-width": "0px",
                                "padding": "0px", "box-shadow": "none"
                            },
                            "filter": { "background-color": "rgba(0, 0, 0, 0)" }
                        }
                    )
                except Exception:
                    if poster_url:
                        st.image(poster_url, use_column_width=True)
            else:
                if poster_url:
                    st.image(poster_url, use_column_width=True)
                else:
                    st.write("포스터 이미지 없음")

            if clicked:
                st.session_state.selected_movie_idx = idx
                st.rerun()

            title_text = str(row.get("영화명", "제목 없음"))
            charm = row.get("매력도")
            charm_txt = f"{int(charm):,}" if pd.notna(charm) else "N/A"

            st.markdown(
                f"""
                <div style="text-align: center;">
                    <b>{title_text}</b><br>
                    <small>매력도: {charm_txt}</small>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # 필터 수집 및 검색/필터 적용
    filters = sidebar_filters(df)
    results = search_movies(st.session_state.query, filters, df)

    # 결과 표시
    if not st.session_state.query:
        st.markdown("### 전체 영화 목록 DB")
        if results is None or results.empty:
            st.warning("선택한 필터에 해당하는 영화가 없습니다.")
        else:
            display_movies_list(results, df)
    else:
        st.markdown(f"**'{st.session_state.query}'**에 대한 검색 결과입니다. (필터 적용됨)")
        if results is None or results.empty:
            st.info("선택한 조건에 맞는 검색 결과가 없습니다.")
        else:
            display_movies_list(results, df)
