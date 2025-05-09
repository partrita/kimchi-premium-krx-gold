import pandas as pd
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("ECOS_API_KEY")

# 결과값의 파일 형식 - xml, json
# 결과값의 언어 - kr(국문), en(영문)

request_begin = 1  # 전체 결과값 중 시작 번호
request_end = 10000  # 전체 결과값 중 끝 번호
code = "731Y001"  # 원/달러 환율
sub_code1 = "0000001"  # 매매기준율
perid = "D"  # 주기(년:A, 반년:S, 분기:Q, 월:M, 반월:SM, 일: D)
begin = "20230101"  # 검색시작일자(주기에 맞는 형식으로 입력: 2020, 2020Q1, 202001, 20200101 등)
end = "20250508"  # 검색종료일자(주기에 맞는 형식으로 입력: 2020, 2020Q1, 202001, 20200101 등)

URL = f"http://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/{request_begin}/{request_end}/{code}/{perid}/{begin}/{end}/{sub_code1}/"

print("URL:", URL)

# API 요청
response = requests.get(URL)
if response.status_code == 200:
    data = response.json()
    # StatisticSearch의 row만 DataFrame으로 변환
    rows = data.get("StatisticSearch", {}).get("row", [])
    if not rows:
        print("데이터가 없습니다.")
    else:
        df = pd.DataFrame(rows)
        # 필요한 컬럼만 추출 (컬럼명이 없을 경우 KeyError 발생 가능, 확인 필요)
        df_selected = df[["ITEM_NAME1", "TIME", "DATA_VALUE"]]
        # 컬럼명 변경
        df_selected.columns = ["Name", "Date", "Value"]
        df_selected.to_csv("ecos_환율_data.csv", index=False)
        print("CSV 저장 완료!")
else:
    print(f"API 요청 실패: {response.status_code}")
