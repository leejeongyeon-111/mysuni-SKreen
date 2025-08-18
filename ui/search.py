import pandas as pd

def search_movies(query, filters, df):
    filtered = df.copy()
    if query:
        filtered = filtered[filtered['영화명'].str.contains(query, case=False, na=False)]
    if filters["장르"]:
        filtered = filtered[filtered['장르'].apply(
            lambda x: any(g in [genre.strip() for genre in str(x).split(',')] for g in filters["장르"]) if pd.notna(x) else False
        )]
    if filters["개봉연도"]:
        filtered = filtered[
            filtered['개봉일'].apply(
                lambda x: str(x)[:4] in filters["개봉연도"]
            )
        ]
    if filters["국가"]:
        filtered = filtered[
            filtered['국가'].apply(
                lambda x: any(country == c.strip() for c in str(x).split(',') for country in filters["국가"]) if pd.notna(x) else False
            )
        ]
    if filters["키워드"]:
        filtered = filtered[
            filtered['Gemini 키워드'].apply(
                lambda x: any(kw == k.strip() for k in str(x).split(',') for kw in filters["키워드"]) if pd.notna(x) else False
            )
        ]
    return filtered.head(filters["limit"])