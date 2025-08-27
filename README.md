# SKreen

VoD 콘텐츠 정보를 빠르고 정확하게 탐색하고 추천하는 자동화 솔루션

## 폴더 구조
- `data/` : 영화 데이터 CSV 파일
- `steps/` : 데이터 수집 및 처리  
  - `step1_make 흐름도.blueprint.json` : 영화 기본 정보 탐색  
  - `step2_naverinfo.py` : 영화 추가 정보 탐색  
  - `step3_recommend.py` : 유사작/경쟁작 선정  
  - `step4_attractiveness.py` : 매력도 예측
- `ui/` : Streamlit 기반 웹 UI 코드

## 주요 기능
- 영화 데이터 크롤링 및 전처리
- 유사작/경쟁작 추천
- ML 모델을 통한 매력도(온라인 판매 실적) 예측
- 웹 UI에서 영화 검색 및 상세 정보 제공

## 실행 방법
1. 필요한 패키지 설치  
   ```
   pip install -r ui/requirements.txt
   ```
2. 웹 앱 실행  
   ```
   streamlit run ui/app.py
   ```

## 데이터
- `data/DB(사전학습용).csv` : 모델 학습용 영화 데이터
- `data/영화DB(임시).csv` : 유사작/경쟁작 및 매력도가 추가된 데이터

## 참고
- 모델 학습 코드는 [steps/ML.ipynb](VoD_recommend/steps/ML.ipynb) 참고

## 데모
실행해보기 : https://mysuni-skreen-dzyhglebrs723hy2zodqzd.streamlit.app/
