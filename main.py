from steps.step3_recommend import find_similars, find_competitors
from steps.step4_attractiveness import predict_attractiveness
import pandas as pd

def main():

    file_path = "./data/영화DB(임시).csv"

    # step 1

    # step 2

    # step 3
    for enc in ("utf-8-sig", "cp949", "utf-8"):
    try:
        df = pd.read_csv("영화DB(임시).csv", encoding=enc)
        break
    except UnicodeDecodeError:
        continue
    df['유사작'] = find_similars(df)
    df['경쟁작'] = find_competitors(df)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

    # step 4
    for enc in ("utf-8-sig", "cp949", "utf-8"):
    try:
        df = pd.read_csv("영화DB(임시).csv", encoding=enc)
        break
    except UnicodeDecodeError:
        continue
    df['예측 매력도'] = predict_attractiveness(df, encoder_path = './steps/ordinal_encoder.pkl', model_path = './steps/rf_weighted_model.pkl')
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

if __name__ == "__main__":

    main()
