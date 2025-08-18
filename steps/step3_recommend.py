from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

def find_similars(df, top_k=5, tiebreak_col='매력도'):
    
    
    df_copy = df.dropna(subset=['Gemini 키워드']).copy()
    df_copy['Gemini 키워드'] = df_copy['Gemini 키워드'].apply(
        lambda x: x.split(',') if isinstance(x, str)
        else (x if isinstance(x, list) else [])
    )
    df_copy['Gemini문장'] = df_copy['Gemini 키워드'].apply(
        lambda x: ' '.join([t.strip() for t in x])
    )

    if df_copy.empty:
        return [""] * len(df)

    
    tfidf = TfidfVectorizer(ngram_range=(1, 2))
    tfidf_matrix = tfidf.fit_transform(df_copy['Gemini문장'])
    sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    
    copy_to_global = df_copy.index.to_numpy()                 # df 인덱스
    global_to_pos  = {g:i for i,g in enumerate(df.index)}     # 원본 순서 유지용(최후 tie)

  
    if tiebreak_col in df_copy.columns:
        tb_viewers = pd.to_numeric(df_copy[tiebreak_col], errors='coerce').fillna(-np.inf).to_numpy()
    else:
        
        tb_viewers = np.full(len(df_copy), -np.inf)

    results_map = {}
    for local_idx in range(len(df_copy)):
        sims = sim[local_idx].copy()
        sims[local_idx] = -np.inf  

        
        cand = pd.DataFrame({
            'local_idx': np.arange(len(df_copy)),
            'sim': sims,
            'viewers': tb_viewers
        })
        cand = cand[cand['local_idx'] != local_idx].copy()

        
        cand['orig_pos'] = cand['local_idx'].map(lambda li: global_to_pos[copy_to_global[li]])

        
        cand = cand.sort_values(
            by=['sim', 'viewers', 'orig_pos'],
            ascending=[False, False, True],
            kind='mergesort'  
        )

        top_local  = cand['local_idx'].to_numpy()[:top_k]
        top_global = copy_to_global[top_local]
        titles     = df.loc[top_global, '영화명'].tolist()

        me_global = copy_to_global[local_idx]
        results_map[me_global] = titles

    
    out = []
    for ridx in df.index:
        out.append(", ".join(results_map.get(ridx, [])))
    return out


# 경쟁작 추천 함수
def find_competitors(df):
    df['개봉날짜'] = pd.to_datetime(df['개봉일'], format='%Y%m%d', errors='coerce')
    competitors_list = []
    for idx, row in df.iterrows():
        movie_name = row['영화명']
        release_date = row['개봉날짜']
        if pd.isna(release_date):
            competitors_list.append("")
            continue
        start_date = release_date - pd.Timedelta(days=7)
        end_date = release_date + pd.Timedelta(days=7)
        competitors_df = df[
            (df['개봉날짜'] >= start_date) &
            (df['개봉날짜'] <= end_date) &
            (df['영화명'] != movie_name)
        ].copy()
        competitors_df = competitors_df.sort_values(by='개봉날짜').head(5)
        competitors_titles = competitors_df['영화명'].tolist()
        competitors_list.append(", ".join(competitors_titles))
    df.drop('개봉날짜', axis=1, inplace=True)
    return competitors_list

