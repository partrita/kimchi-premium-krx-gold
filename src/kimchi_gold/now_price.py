import re
from typing import Dict, Tuple
import requests
from bs4 import BeautifulSoup

HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://m.stock.naver.com/",
}


def get_price_from_naver(
    url: str, error_msg: str, regex: str = r"[\d,]+(?:\.\d+)?"
) -> float:
    """
    네이버 금융에서 가격 정보를 추출하는 공통 함수
    """
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    price_tag = soup.find("strong", class_="DetailInfo_price__I_VJn")
    if price_tag:
        text = price_tag.get_text()
        price = re.search(regex, text)
        if price:
            return float(price.group().replace(",", ""))
    raise ValueError(error_msg)


def get_domestic_gold_price() -> float:
    url = "https://m.stock.naver.com/marketindex/metals/M04020000"
    return get_price_from_naver(url, "국내 금 가격 정보를 찾을 수 없습니다.")


def get_international_gold_price() -> float:
    url = "https://m.stock.naver.com/marketindex/metals/GCcv1"
    return get_price_from_naver(url, "국제 금 가격 정보를 찾을 수 없습니다.")


def get_usd_krw() -> float:
    url = "https://m.stock.naver.com/marketindex/exchange/FX_USDKRW"
    return get_price_from_naver(url, "환율 정보를 찾을 수 없습니다.")


def calc_kimchi_premium() -> Tuple[float, float, float, float, float, float]:
    domestic = get_domestic_gold_price()
    international = get_international_gold_price()
    usdkrw = get_usd_krw()
    international_krw_per_g = (international * usdkrw) / 31.1035
    difference = domestic - international_krw_per_g
    premium_percent = (difference / international_krw_per_g) * 100
    return (
        domestic,
        international,
        international_krw_per_g,
        usdkrw,
        difference,
        premium_percent,
    )


if __name__ == "__main__":
    (
        domestic,
        international,
        international_krw_per_g,
        usdkrw,
        difference,
        premium_percent,
    ) = calc_kimchi_premium()
    print(f"국내 금가격         : {domestic:>12,.2f} 원/g")
    print(f"국제 금 1g 원화환산 : {international_krw_per_g:>12,.2f} 원/g")
    print(f"김치프리미엄        : {difference:>12,.2f} 원/g ({premium_percent:+.2f}%)")
