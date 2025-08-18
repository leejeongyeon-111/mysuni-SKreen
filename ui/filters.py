import streamlit as st

def sidebar_filters(df):
    genre_options = sorted({g.strip() for genres in df['장르'].dropna() for g in str(genres).split(',')})
    year_options = sorted({str(y)[:4] for y in df['개봉일'].dropna()}, reverse=True)
    country_options = sorted({c.strip() for countries in df['국가'].dropna() for c in str(countries).split(',')})
    keyword_options = sorted({kw.strip() for kws in df['Gemini 키워드'].dropna() for kw in str(kws).split(',')})

    with st.sidebar:
        st.markdown("## 🎛️ 조건 설정")
        selected_genres = st.multiselect("장르", genre_options)
        selected_years = st.multiselect("개봉연도", year_options)
        selected_countries = st.multiselect("국가", country_options)
        selected_keyword = st.multiselect("키워드", keyword_options)
        limit = st.slider("영화 개수", 1, 30, 10)

    return {
        "장르": selected_genres,
        "개봉연도": selected_years,
        "국가": selected_countries,
        "키워드": selected_keyword,
        "limit": limit
    }