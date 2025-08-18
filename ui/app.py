# app.py

import streamlit as st

# ✅ 반드시 가장 먼저 호출
st.set_page_config(
    page_title="SKreen",
    layout="wide"
)

# 표준 라이브러리 / 외부 모듈
import sys
import subprocess
from pathlib import Path
import pandas as pd

# 내부 모듈
from filters import sidebar_filters
from search import search_movies
from display import show_movie_detail, display_movies_list

# (옵션) streamlit-card가 없을 때도 죽지 않게 가드
try:
    from streamlit_card import card
    HAS_CARD = True
except Exception:
    HAS_CARD = False

# CSV 로더 (리포 루트의 data/movies.csv 또는 data/영화DB(임시).csv를 탐색)
try:
    from csv_loader import load_csv, debug_info
except Exception as e:
    # csv_loader가 없다면 친절한 에러 메시지
    st.error(
        "csv_loader 모듈을 불러오지 못했습니다. 리포 루트에 csv_loader.py를 추가해주세요.\n"
        "임시로 업로드 방식으로 진행할 수 있습니다."
    )
    def load_csv():
        return None
    def debug_info():
        return [], []


# =========================
# 데이터 로딩
# =========================
@st.cache_data
def load_data():
    """
    csv_loader.load_csv()는 아래 순서로 CSV를 탐색해 읽습니다.
    - 리포 루트의 data/movies.csv
    - 리포 루트의 data/영화DB(임시).csv
    - (있다면) 환경변수 DATA_CSV_PATH
    인코딩은 utf-8-sig → cp949 → utf-8 순서로 시도
    """
    df = load_csv()
    return df

df = load_data()

# CSV를 찾지 못한 경우: 디버그 + 업로더 폴백
if df is None:
    st.error("CSV를 찾지 못했어. 아래 디버그 정보를 확인하고, 필요하면 CSV를 업로드해줘.")
    cand, listing = debug_info()
    if cand:
        st.caption("🔎 Tried paths:")
        st.write(cand)
    st.caption("📁 CWD/data listing:")
    st.write(listing)

    up = st.file_uploader("CSV 업로드", type=["csv"])
    if up:
        # 업로드 파일로 진행
        try:
            # 한글 CSV 인코딩 안전 로드
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
            st.success("업로드된 CSV로 진행할게!")
        except Exception as e:
            st.exception(e)
            st.stop()
    else:
        st.stop()

# 숫자 컬럼 정리 (매력도)
if "매력도" in df.columns:
    df["매력도"] = pd.to_numeric(df["매력도"], errors="coerce")

# =========================
# 세션 상태
# =========================
if "selected_movie_idx" not in st.session_state:
    st.session_state.selected_movie_idx = None
if "query" not in st.session_state:
    st.session_state.query = ""

# =========================
# 상단: 검색 컨트롤
# =========================
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

# =========================
# 사이드바: 데이터 업데이트 실행
# =========================
with st.sidebar:
    if st.button("🔄 데이터 업데이트"):
        with st.spinner("데이터를 수집하고 분석 중입니다..."):
            try:
                # 현재 인터프리터로 main.py 실행 (환경 혼선 방지)
                subprocess.run([sys.executable, "main.py"], check=True)
                st.success("✅ 데이터 업데이트 완료!")
                st.cache_data.clear()
                st.rerun()
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                st.error(f"데이터 업데이트 중 오류: {e}")

# =========================
# 상세 페이지 or 메인 페이지
# =========================

# 1) 상세 페이지
if st.session_state.selected_movie_idx is not None:
    if st.button("⬅️ 목록으로 돌아가기"):
        st.session_state.selected_movie_idx = None
        st.rerun()

    # df의 인덱스로 해당 영화 선택
    try:
        selected_row = df.iloc[st.session_state.selected_movie_idx]
    except Exception:
        st.warning("선택한 항목을 찾을 수 없습니다. 목록으로 돌아갑니다.")
        st.session_state.selected_movie_idx = None
        st.rerun()

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

    # 상위 5개
    top_5_movies = (
        df.dropna(subset=['매력도'])
          .sort_values(by='매력도', ascending=False)
          .head(5)
    )

    poster_cols = st.columns(5) if len(top_5_movies) >= 1 else [st]

    for i, (idx, row) in enumerate(top_5_movies.iterrows()):
        with poster_cols[i % len(poster_cols)]:
            clicked = False
            poster_url = row.get('url', '') or row.get('poster_url', '') or row.get('image', '')

            if HAS_CARD and poster_url:
                try:
                    clicked = card(
                        title="",
                        text="",
                        image=poster_url,
                        key=f"top5_{idx}",
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
                except Exception:
                    # 카드 에러 시 폴백
                    st.image(poster_url, use_column_width=True)
            else:
                if poster_url:
                    st.image(poster_url, use_column_width=True)
                else:
                    st.write("포스터 이미지 없음")

            if clicked:
                st.session_state.selected_movie_idx = idx
                st.rerun()

            # 타이틀/매력도 표기
            title_text = str(row.get('영화명', '제목 없음'))
            try:
                charm = row.get('매력도')
                charm_txt = f"{int(charm):,}" if pd.notna(charm) else "N/A"
            except Exception:
                charm_txt = "N/A"

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
