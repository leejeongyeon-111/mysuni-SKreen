import pandas as pd
import joblib

def convert_audience_to_int(audience_str):
    if isinstance(audience_str, str):
        audience_str = audience_str.replace(',', '')
        if '만' in audience_str:
            try:
                return int(float(audience_str.replace('만', '')) * 10000)
            except ValueError:
                return 0
    return 0

def predict_attractiveness(df, encoder_path, model_path):
    # 모델 로드
    model = joblib.load(model_path)

    # 예측에 사용할 feature 컬럼 지정 (예시: 필요에 따라 수정)
    x = df.copy()
    x = x.fillna(0)  # 결측치 0으로 대체

    x['장르'] = x['장르'].str.split(',', expand=True)[0]
    x['배우'] = x['배우'].str.split(',', expand=True)[0]
    x['제작사'] = x['제작사'].str.split(',', expand=True)[0]
    x['상영시간'] = x['상영시간'].astype(int)

    keywords_split = x['Gemini 키워드'].str.split(',', expand=True)
    keywords_split.columns = ['톤', '시대/배경', '주제']
    x = pd.concat([x, keywords_split], axis=1)
    x = x.drop('Gemini 키워드', axis=1)

    x['국가'] = x['국가'].str.split(',', expand=True)[0]

    x['관객수_int'] = x['누적 관객수'].apply(convert_audience_to_int)
    bins = [0, 100000, 500000, 1000000, 5000000, 10000000, float('inf')]
    labels = ['10만 미만', '10만 이상', '50만 이상', '100만 이상', '500만 이상', '1000만 이상']
    x['관객수_categorical'] = pd.cut(x['관객수_int'], bins=bins, labels=labels, right=False)
    
    x['개봉일'] = pd.to_datetime(x['개봉일'], format = '%Y%m%d', errors='coerce')
    x['개봉연도'] = x['개봉일'].dt.year
    x['개봉월'] = x['개봉일'].dt.month
    x['개봉연도'] = x['개봉연도'].fillna(0).astype(int) # 결측값 0으로 채우고 int형으로 자료형 변경
    x['개봉월'] = x['개봉월'].fillna(0).astype(int)
    x = x.drop('개봉일', axis = 1)
    

    x = x[['장르', '감독', '제작사','실관람객 평점', '네티즌 평점', '네이버 관심도(찜)', '톤', '시대/배경', '주제', '개봉연도', '개봉월', '관객수_int']]
    categorical_cols = ['장르', '감독', '제작사', '톤', '시대/배경', '주제']
    ord = joblib.load(encoder_path)
    x[categorical_cols] = ord.transform(x[categorical_cols])

    attractivenss_pred = model.predict(x)
    return attractivenss_pred
