# display.py

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
import platform
import os, platform


SHOW_FONT_WARNING = False 

def set_korean_font() -> bool:
    """
    운영체제에 맞는 한글 폰트를 설정합니다.
    Matplotlib 그래프에서 한글이 깨지는 현상을 방지합니다.
    """
    system_os = platform.system()
    try:
        if system_os == "Windows":
            font_path = "C:/Windows/Fonts/malgun.ttf"
        elif system_os == "Darwin":  # macOS
          
            font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
        elif system_os == "Linux":
    
            font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
        else:
            font_path = ""

        if not font_path or not os.path.exists(font_path):
            raise FileNotFoundError(font_path)

        font_prop = fm.FontProperties(fname=font_path)
        plt.rc('font', family=font_prop.get_name())
        plt.rcParams["axes.unicode_minus"] = False
        return True

    except FileNotFoundError:
        
        if SHOW_FONT_WARNING:
            st.warning("한글 폰트 파일을 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
        return False


def format_number_display(raw_value):
    """
    다양한 숫자/문자 형식을 처리하여 천 단위 쉼표가 있는 문자열로 변환합니다.
    'X만' 형식과 숫자형 데이터를 모두 처리합니다.
    """
    if pd.isna(raw_value):
        return '-'
    try:
        
        if '만' in str(raw_value):
            num_part = float(str(raw_value).replace('만', ''))
            value = int(num_part * 10000)
            return f"{value:,}"
       
        else:
            return f"{int(float(raw_value)):,}"
    except (ValueError, TypeError):
        
        return str(raw_value)


def show_movie_detail(row, full_df):
    """선택된 영화 한 편의 상세 정보를 모두 표시하는 함수"""
    set_korean_font()

    # --- 1. 포스터 및 기본 정보 ---
    col1, col2 = st.columns([1, 2])
    with col1:
    # col1 내부에 새로운 열 3개를 생성합니다. (좌측여백, 콘텐츠, 우측여백)
    # 비율을 조정하여 포스터 크기를 바꿀 수 있습니다. 예: [1, 5, 1]로 하면 더 작아집니다.
        c1, c2, c3 = st.columns([1, 8, 1])

        with c2: # 중앙 열(c2)에만 콘텐츠를 표시합니다.
            poster_url = str(row.get('url', '')).strip()
            if poster_url and poster_url.startswith("http"):
                st.image(poster_url, use_container_width=True)
            else:
                # 포스터 없음 표시도 동일한 높이를 유지해줍니다.
                st.markdown("<div style='width:100%;height:420px;border:2px solid #ccc;border-radius:8px;display:flex;align-items:center;justify-content:center;'><span style='color:#bbb;'>포스터 없음</span></div>", unsafe_allow_html=True)
                
    with col2:
        # 1. 제목과 정보에 적용할 CSS 스타일을 정의합니다.
        title_style = "font-size: 2.8rem; font-weight: bold; margin-right: 15px;"
        meta_style = "font-size: 1.2rem; color: #808080;" # 정보 텍스트는 회색으로

        # --- 개봉일, 장르, 상영시간 정보 처리 (기존 코드와 동일) ---
        raw_date_val = row.get('개봉일')
        if pd.notna(raw_date_val):
            raw_date_str = str(int(raw_date_val))
            formatted_date = f"{raw_date_str[:4]}/{raw_date_str[4:6]}/{raw_date_str[6:]}" if len(raw_date_str) >= 8 else "형식 오류"
        else:
            formatted_date = "정보 없음"

        runtime_val = row.get('상영시간')
        runtime = f"{int(float(runtime_val))}분" if pd.notna(runtime_val) else '정보 없음'
        genre = row.get('장르', '정보 없음')


        # 2. 제목과 정보를 하나의 HTML 문자열로 합칩니다.
        # display: flex와 align-items: baseline을 사용해 깔끔하게 정렬합니다.
        display_html = f"""
        <div style="display: flex; align-items: baseline; flex-wrap: wrap;">
            <span style="{title_style}">{row['영화명']}</span>
            <span style="{meta_style}">{formatted_date} | {genre} | {runtime}</span>
        </div>
        """

        # 3. 한 번의 st.markdown 호출로 모든 정보를 출력합니다.
        st.markdown(display_html, unsafe_allow_html=True)

        gradient_text_html = "<h3 style='background-image: linear-gradient(to right, #87CEEB, #4B0082);-webkit-background-clip: text;background-clip: text;color: transparent;font-weight: bold;'>AI 매력도 예측 (3개월간 예상 온라인 판매실적)</h3>"
        st.markdown(gradient_text_html, unsafe_allow_html=True)
        
        charm_pred = row.get('예측 매력도', None)
        if pd.notna(charm_pred):
            all_charms = pd.to_numeric(full_df['예측 매력도'], errors='coerce').dropna()
            fig, ax = plt.subplots(figsize=(10, 3))
            sns.histplot(all_charms, ax=ax, bins=30, color="#EAEAEA", alpha=1)
            
            highlight_color = '#4B0082'
            for patch in ax.patches:
                x_min, x_max = patch.get_x(), patch.get_x() + patch.get_width()
                if x_min <= charm_pred < x_max:
                    patch.set_facecolor(highlight_color)
                    bar_height = patch.get_height()
                    ax.text(patch.get_x() + patch.get_width() / 2, bar_height, f'{int(charm_pred):,}\n', ha='center', va='bottom', color=highlight_color, fontweight='bold')
                    break
            
            #ax.set_title("전체 작품 내 매력도 분포", fontsize=14, pad=20)
            ax.set_yticks([])
            ax.set_ylabel('')
            ax.set_xlabel('')
            for spine in ['top', 'right', 'left']:
                ax.spines[spine].set_visible(False)
            st.pyplot(fig)

        # TMDB 키워드
        tmdb_keywords = str(row.get('TMDB 키워드', '')).strip()
        if tmdb_keywords:
            keywords_list = tmdb_keywords.split(', ')
            hashtag_string = " ".join([f"#{kw}" for kw in keywords_list[:5]])
            st.markdown(f"<p style='color: #007BFF;'>{hashtag_string}</p>", unsafe_allow_html=True)


    st.write(f"**줄거리**: {row.get('줄거리', '-')}")

    st.markdown("---")        
    font_style = "font-size: 18px;"

    info_cols = st.columns(6)
    actors = ", ".join(str(row.get('배우', '')).split(',')[:3])
    info_cols[0].markdown(f"<div style='{font_style}'><b>배우</b><br>{actors}</div>", unsafe_allow_html=True)
    info_cols[1].markdown(f"<div style='{font_style}'><b>감독</b><br>{row.get('감독', '-')}</div>", unsafe_allow_html=True)
    maker = str(row.get('제작사', '')).split(',')[0]
    info_cols[2].markdown(f"<div style='{font_style}'><b>제작사</b><br>{maker}</div>", unsafe_allow_html=True)
    info_cols[3].markdown(f"<div style='{font_style}'><b>누적관객</b><br>{format_number_display(row.get('누적 관객수'))}명</div>", unsafe_allow_html=True)
    info_cols[4].markdown(f"<div style='{font_style}'><b>시청자 수</b><br>{format_number_display(row.get('매력도'))}</div>", unsafe_allow_html=True)
    gradient_style = "background-image: linear-gradient(to right, #FF8C00, #9400D3);-webkit-background-clip: text;background-clip: text;color: transparent;font-weight: bold;"
    info_cols[5].markdown(f"<div style='{font_style}'><b>AI 키워드</b><br><span style='{gradient_style}'>{row.get('Gemini 키워드', '-')}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### 유사작")
        similar_raw = row.get('유사작', '')
        similar_list = [x.strip() for x in similar_raw.replace('[','').replace(']','').split(',') if x.strip()] if isinstance(similar_raw, str) else []
        if similar_list:
            similar_df = full_df[full_df['영화명'].isin(similar_list)][['영화명', 'Gemini 키워드', '장르']].rename(columns={'영화명': '영화 제목', 'Gemini 키워드': '키워드'})
            st.dataframe(similar_df, use_container_width=True, hide_index=True)
        else:
            st.info("유사작 정보가 없습니다.")

    with col4:
        st.markdown("#### 경쟁작")
        competitor_raw = row.get('경쟁작', '')
        competitor_list = [x.strip() for x in competitor_raw.replace('[','').replace(']','').split(',') if x.strip()] if isinstance(competitor_raw, str) else []
        if competitor_list:
            comp_df = full_df[full_df['영화명'].isin(competitor_list)].copy()
            bins = [-float("inf"), 50000, 100000, 500000, 1000000, float("inf")]
            labels = ["5만 미만", "5만 이상", "10만 이상", "50만 이상", "100만 이상"]
            comp_df['매력도'] = pd.cut(pd.to_numeric(comp_df['예측 매력도'], errors='coerce'), bins=bins, labels=labels, right=False)
            
            # ✅ 수정된 부분: '시청자' 컬럼도 헬퍼 함수를 통해 안전하게 처리
            comp_df['시청자'] = comp_df['매력도'].apply(format_number_display)
            
            display_comp_df = comp_df[['영화명', 'Gemini 키워드', '매력도', '시청자']].rename(columns={'영화명': '영화 제목', 'Gemini 키워드': '키워드'})
            st.dataframe(display_comp_df, use_container_width=True, hide_index=True)
        else:
            st.info("경쟁작 정보가 없습니다.")


def display_movies_list(results_df, full_df):
    """
    전체 3열 그리드 안에 각 영화 정보를
    [포스터, 상세내용]의 2열 레이아웃으로 표시하는 함수
    """
    
    # 1. 전체 레이아웃을 위한 3열 그리드를 먼저 생성합니다.
    main_cols = st.columns(3)
    
    # 2. 검색된 영화 목록을 순회합니다.
    for i, (_, row) in enumerate(results_df.iterrows()):
        # 3. i를 3으로 나눈 나머지(0, 1, 2)를 이용해 영화를 각 main_cols에 순서대로 배분합니다.
        with main_cols[i % 3]:
            
            # 4. ⭐ 각 영화 아이템 내부를 위한 2열 레이아웃을 '중첩'하여 생성합니다.
            inner_col1, inner_col2 = st.columns([1, 2]) # [포스터, 정보] 비율

            # --- 내부 왼쪽 열 (inner_col1): 포스터 ---
            with inner_col1:
                poster_url = str(row.get('url', '')).strip()
                if poster_url and poster_url.startswith("http"):
                    st.image(poster_url, use_container_width=True)
                else:
                    st.markdown("<div style='height:200px; border:1px solid #eee; display:flex; align-items:center; justify-content:center; color:#aaa;'>No Image</div>", unsafe_allow_html=True)

            # --- 내부 오른쪽 열 (inner_col2): 영화 정보 ---
            with inner_col2:
                # 공간이 좁으므로 제목 폰트 크기를 약간 작게 조절합니다.
                st.markdown(f"**{row['영화명']}**")
                
                # 장르와 키워드 텍스트도 작은 폰트로 표시합니다.
                genre = row.get('장르', '정보 없음')
                st.markdown(f"<small>🎬 장르: {genre}</small>", unsafe_allow_html=True)

                ai_keywords = row.get('Gemini 키워드', '정보 없음')
                st.markdown(f"<small>✨ AI키워드: {ai_keywords}</small>", unsafe_allow_html=True)

                viewer_predict = row.get('예측 매력도', '정보 없음')
                st.markdown(f"<small>✨ AI매력도: {int(viewer_predict)}</small>", unsafe_allow_html=True)
                
                if st.button("상세보기", key=f"detail_{row.name}"):
                    st.session_state.selected_movie_idx = row.name
                    st.rerun()
            
            # 각 영화 아이템 아래에 구분선을 추가하여 가독성을 높입니다.
            st.markdown("---")




