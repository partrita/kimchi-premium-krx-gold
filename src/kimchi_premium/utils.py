import pandas as pd
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("ECOS_API_KEY")


def get_exchangerate(start_date: str, end_date: str) -> pd.DataFrame:
    """
    한국은행 ECOS API를 이용하여 원/달러 환율 데이터를 조회하고 Pandas DataFrame으로 반환합니다.

    Args:
        start_date (str): 검색 시작 일자 (YYYYMMDD 형식).
        end_date (str): 검색 종료 일자 (YYYYMMDD 형식).

    Returns:
        pd.DataFrame: 'Name', 'Date', 'Value' 컬럼을 가진 DataFrame.
                     API 요청 실패 또는 데이터가 없을 경우 빈 DataFrame을 반환합니다.
    """
    API_KEY = "YOUR_API_KEY"  # 실제 API 키로 변경해야 합니다.
    request_begin = 1
    request_end = 100000  # 충분히 큰 값으로 설정하여 대부분의 데이터를 포함하도록 함
    code = "731Y001"  # 원/달러 환율
    sub_code = "0000001"  # 매매기준율
    perid = "D"  # 일별 데이터

    URL = f"http://ecos.bok.or.kr/api/StatisticSearch/{API_KEY}/json/kr/{request_begin}/{request_end}/{code}/{perid}/{start_date}/{end_date}/{sub_code}/"

    try:
        response = requests.get(URL)
        response.raise_for_status()  # HTTPError 발생 시 예외를 발생시킴
        data = response.json()
        rows = data.get("StatisticSearch", {}).get("row", [])
        if not rows:
            print("해당 기간에 대한 환율 데이터가 없습니다.")
            return pd.DataFrame()
        else:
            df = pd.DataFrame(rows)
            df_selected = df[["ITEM_NAME1", "TIME", "DATA_VALUE"]].copy()
            df_selected.columns = ["Name", "Date", "Value"]
            return df_selected
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"JSON 디코딩 오류: {e}")
        return pd.DataFrame()
    except KeyError as e:
        print(f"데이터 처리 중 KeyError 발생: {e}")
        return pd.DataFrame()


# 사용 예시
if __name__ == "__main__":
    start_date = "20240505"
    end_date = "20250505"
    exchange_rate_df = get_exchangerate(start_date, end_date)
    if not exchange_rate_df.empty:
        print(exchange_rate_df)
