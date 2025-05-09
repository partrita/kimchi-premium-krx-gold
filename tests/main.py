import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import click
import csv

# .env 파일에서 환경 변수 로드
load_dotenv()
API_KEY = os.getenv("ECOS_API_KEY")

# API 키가 없는 경우 오류 처리
if not API_KEY:
    print("오류: .env 파일에서 ECOS_API_KEY를 찾을 수 없습니다.")
    exit()

# 데이터 종류별 통계코드 및 주기
data_codes = {
    "국제 금 가격 (런던, US$/온스)": {
        "통계표코드": "036Y003",
        "항목코드1": "0101000",
        "주기": "D",
    },
    "국내 금 가격 (KRW/g)": {
        "통계표코드": "036Y003",
        "항목코드1": "0103000",
        "주기": "D",
    },
    "원/달러 환율 (종가)": {"통계표코드": "039Y001", "항목코드1": "001", "주기": "D"},
}


def fetch_ecos_data(api_key, 통계표코드, 항목코드1, 주기, 시작일, 종료일):
    """ECOS API를 사용하여 데이터를 가져오는 함수"""
    url = f"http://ecos.bok.or.kr/api/StatisticSearch/{api_key}/json/kr/1/{통계표코드}/{주기}/{시작일}/{종료일}/{항목코드1}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외를 발생시킴
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {e}")
        return None


def parse_ecos_data(data):
    """ECOS API 응답에서 필요한 데이터를 추출하는 함수"""
    results = {}
    if data and "StatisticSearch" in data and "row" in data["StatisticSearch"]:
        for item in data["StatisticSearch"]["row"]:
            날짜 = item.get("TIME", "N/A")
            값 = item.get("DATA_VALUE", "N/A")
            if 날짜 not in results:
                results[날짜] = {}
            # 통계표코드에 따라 데이터 종류를 구분하여 저장
            통계표코드 = data["StatisticSearch"]["list"]["STAT_CODE"]
            if 통계표코드 == "036Y003":
                항목코드1 = item.get("ITEM_CODE1")
                if 항목코드1 == "0101000":
                    results[날짜]["국제 금 가격 (US$/온스)"] = 값
                elif 항목코드1 == "0103000":
                    results[날짜]["국내 금 가격 (KRW/g)"] = 값
            elif 통계표코드 == "039Y001":
                results[날짜]["원/달러 환율 (종가)"] = 값
    return results


def save_to_csv(data, filename):
    """추출된 데이터를 CSV 파일로 저장하는 함수"""
    if not data:
        print("저장할 데이터가 없습니다.")
        return

    fieldnames = [
        "날짜",
        "국제 금 가격 (US$/온스)",
        "국내 금 가격 (KRW/g)",
        "원/달러 환율 (종가)",
    ]

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for 날짜, values in sorted(data.items()):
                row = {"날짜": 날짜, **values}
                writer.writerow(row)
        print(f"결과가 '{filename}'으로 저장되었습니다.")
    except Exception as e:
        print(f"CSV 파일 저장 오류: {e}")


@click.command()
@click.option("--start_date", required=True, help="조회 시작 날짜 (YYYYMMDD 형식)")
@click.option(
    "--end_date",
    default=datetime.now().strftime("%Y%m%d"),
    help="조회 종료 날짜 (YYYYMMDD 형식, 기본값: 오늘)",
)
@click.option(
    "--output_dir", default=".", help="CSV 파일 저장 위치 (기본값: 현재 디렉토리)"
)
def main(start_date, end_date, output_dir):
    """ECOS API에서 국제 금 가격, 국내 금 가격, 환율 데이터를 조회하고 CSV 파일로 저장합니다."""
    try:
        datetime.strptime(start_date, "%Y%m%d")
        datetime.strptime(end_date, "%Y%m%d")
    except ValueError:
        print("오류: 날짜 형식이 올바르지 않습니다. (YYYYMMDD 형식)")
        return

    all_data = {}
    for name, codes in data_codes.items():
        fetched_data = fetch_ecos_data(
            API_KEY,
            codes["통계표코드"],
            codes["항목코드1"],
            codes["주기"],
            start_date,
            end_date,
        )
        parsed_data = parse_ecos_data(fetched_data)
        # 모든 데이터를 날짜를 키로 하여 통합
        for 날짜, values in parsed_data.items():
            if 날짜 not in all_data:
                all_data[날짜] = {}
            all_data[날짜].update(values)

    today = datetime.now().strftime("%Y%m%d")
    filename = f"kimchi_premium_KRX_gold_data_{today}.csv"
    output_path = os.path.join(output_dir, filename)
    save_to_csv(all_data, output_path)


if __name__ == "__main__":
    main()
