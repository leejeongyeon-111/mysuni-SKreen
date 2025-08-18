import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote
import numpy as np

# --- 설정 ---
input_csv_file = '영화 정보 탐색 - Database.csv'
output_csv_file = '영화 정보 탐색 - Database_updated.csv'
title_column = '영화명'
netizen_rating_column = '네티즌 평점'
interest_column = '네이버 관심도(찜)'
audience_column = '누적 관객수'
# -----------

# --- 셀레니움 드라이버 자동 설정 ---
driver = None
try:
    options = webdriver.ChromeOptions()
    options.add_argument('headless')  # 브라우저 창을 띄우지 않고 백그라운드에서 실행
    options.add_argument('window-size=1920x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--log-level=3") # 콘솔의 불필요한 로그 최소화

    # 이 한 줄이 자동으로 chromedriver를 다운로드하고 설정합니다.
    driver = webdriver.Chrome(options=options)
    print("✅ 웹 드라이버가 성공적으로 시작되었습니다. (자동 설정 완료)")

except Exception as e:
    print(f"❌ [오류] 크롬 드라이버 자동 설정에 실패했습니다. 다음을 확인해주세요:")
    print("1. 인터넷 연결 상태를 확인해주세요.")
    print("2. 크롬 브라우저가 최신 버전인지 확인해주세요.")
    print(f"3. 오류 메시지: {e}")
# ------------------------------------

def parse_audience_count(text):
    """'만', '억' 등의 문자를 숫자로 변환하는 함수"""
    if not isinstance(text, str): return 'N/A'
    text = text.replace(',', '').lower()
    num = 0
    if '억' in text:
        try: num += float(re.search(r'([\d]+\.?\d*)억', text).group(1)) * 100000000
        except: pass
    if '만' in text:
        try: num += float(re.search(r'([\d]+\.?\d*)만', text).group(1)) * 10000
        except: pass
    if num > 0: return str(int(num))
    try:
        return str(int(re.search(r'(\d+)', text).group(1)))
    except:
        return 'N/A'

def get_movie_data_with_selenium(movie_title):
    """
    셀레니움을 사용하여 네이버 통합 검색 결과에서 영화 정보를 크롤링합니다.
    """
    search_url = f"https://search.naver.com/search.naver?query={quote(movie_title + ' 영화')}"
    try:
        driver.get(search_url)
        # 영화 정보 섹션이 화면에 나타날 때까지 최대 5초간 기다립니다.
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc_new.cs_common_module"))
        )
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        movie_section = soup.select_one("div.sc_new.cs_common_module._au_movie_content_wrap")
        if not movie_section:
            return 'Not Found', 'Not Found', 'Not Found'

        rating, interest, audience_count = 'N/A', 'N/A', 'N/A'

        # 각 정보 추출 시, 요소가 없는 경우를 대비해 try-except로 안전하게 처리
        try:
            # 실관람객 평점 우선
            rating_element = movie_section.select_one("a.lego_rating_box_see .area_star_number")
            if rating_element:
                rating = re.search(r'(\d+\.?\d*)', rating_element.get_text(strip=True)).group(1)
            else: # 없으면 네티즌 평점
                rating_dt = movie_section.find('dt', string='평점')
                if rating_dt and rating_dt.find_next_sibling('dd'):
                    rating = rating_dt.find_next_sibling('dd').get_text(strip=True)
        except Exception:
            pass # 평점 정보가 없으면 'N/A' 유지

        try:
            interest_element = movie_section.select_one("span._like_count")
            if interest_element:
                interest = interest_element.get_text(strip=True).replace(',', '')
        except Exception:
            pass # 관심도 정보가 없으면 'N/A' 유지

        try:
            audience_dt = movie_section.find('dt', string='관객수')
            if audience_dt and audience_dt.find_next_sibling('dd'):
                audience_text = audience_dt.find_next_sibling('dd').get_text(strip=True)
                audience_count = parse_audience_count(audience_text)
        except Exception:
            pass # 관객수 정보가 없으면 'N/A' 유지

        return rating, interest, audience_count

    except Exception as e:
        print(f"  [오류] '{movie_title}' 처리 중 페이지 로딩 또는 요소 찾기 실패: {e}")
        return 'Error', 'Error', 'Error'

# --- 메인 코드 실행 ---
if driver:
    try:
        df = pd.read_csv(input_csv_file)
        print(f"✅ '{input_csv_file}' 파일을 성공적으로 불러왔습니다.")

        for col in [netizen_rating_column, interest_column, audience_column]:
            if col not in df.columns: df[col] = np.nan
            df[col] = df[col].astype(object)

        print("\n🚀 셀레니움을 이용한 크롤링을 시작합니다.")
        for index, row in df.iterrows():
            # CSV 파일에 평점 정보가 없는 영화만 새로 크롤링
            if pd.isna(row[netizen_rating_column]):
                title = row[title_column]
                print(f"({index + 1}/{len(df)}) '{title}' 정보 수집 중...", end="")

                rating, interest, audience = get_movie_data_with_selenium(title)

                df.at[index, netizen_rating_column] = rating
                df.at[index, interest_column] = interest
                df.at[index, audience_column] = audience

                print(f" -> 평점: {rating}, 관심도: {interest}, 관객수: {audience}")

                time.sleep(0.5) # 서버 부하를 줄이기 위한 짧은 대기
            else:
                print(f"({index + 1}/{len(df)}) '{row[title_column]}' 정보는 이미 있어 건너뜁니다.")

        df.to_csv(output_csv_file, index=False, encoding='utf-8-sig')
        print(f"\n✨ 모든 작업이 완료되었습니다. 결과가 '{output_csv_file}' 파일에 저장되었습니다.")

    except FileNotFoundError:
        print(f"❌ [오류] '{input_csv_file}' 파일을 찾을 수 없습니다. 파일 이름과 경로를 확인해주세요.")
    except Exception as e:
        print(f"❌ 작업 중 예기치 않은 오류가 발생했습니다: {e}")
    finally:
        driver.quit() # 작업이 끝나면 반드시 브라우저 종료
        print("✅ 웹 드라이버가 종료되었습니다.")