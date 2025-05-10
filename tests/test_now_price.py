import pytest
from unittest.mock import patch
from kimchi_gold import now_price

MOCK_DOMESTIC_PRICE_TEXT = "80,123.45"
MOCK_INTERNATIONAL_PRICE_TEXT = "1,999.99"
MOCK_USD_KRW_TEXT = "1,355.67"


def test_get_price_from_naver_success():
    url = "http://example.com"
    error_msg = "테스트 에러 메시지"

    with (
        patch("requests.get") as mock_get,
        patch("kimchi_gold.now_price.BeautifulSoup") as mock_bs,
    ):
        mock_get.return_value.content = f"""
            <html>
                <body>
                    <strong class="DetailInfo_price__I_VJn">{MOCK_DOMESTIC_PRICE_TEXT}</strong>
                </body>
            </html>
        """.encode("utf-8")
        mock_soup_instance = mock_bs.return_value
        mock_soup_instance.find.return_value.get_text.return_value = (
            MOCK_DOMESTIC_PRICE_TEXT
        )

        price = now_price.get_price_from_naver(url, error_msg)
        assert price == float(MOCK_DOMESTIC_PRICE_TEXT.replace(",", ""))
        mock_get.assert_called_once_with(url, headers=now_price.HEADERS)
        mock_bs.assert_called_once_with(mock_get.return_value.content, "html.parser")
        mock_soup_instance.find.assert_called_once_with(
            "strong", class_="DetailInfo_price__I_VJn"
        )


def test_get_price_from_naver_no_price_tag():
    url = "http://example.com"
    error_msg = "테스트 에러 메시지"

    with (
        patch("requests.get") as mock_get,
        patch("kimchi_gold.now_price.BeautifulSoup") as mock_bs,
    ):
        mock_get.return_value.content = """
            <html>
                <body>
                    <div>No price here</div>
                </body>
            </html>
        """.encode("utf-8")
        mock_soup_instance = mock_bs.return_value
        mock_soup_instance.find.return_value = None

        with pytest.raises(ValueError) as excinfo:
            now_price.get_price_from_naver(url, error_msg)
        assert str(excinfo.value) == error_msg
        mock_get.assert_called_once_with(url, headers=now_price.HEADERS)
        mock_bs.assert_called_once_with(mock_get.return_value.content, "html.parser")
        mock_soup_instance.find.assert_called_once_with(
            "strong", class_="DetailInfo_price__I_VJn"
        )


def test_get_price_from_naver_no_price_in_text():
    url = "http://example.com"
    error_msg = "테스트 에러 메시지"

    with (
        patch("requests.get") as mock_get,
        patch("kimchi_gold.now_price.BeautifulSoup") as mock_bs,
    ):
        mock_get.return_value.content = """
            <html>
                <body>
                    <strong class="DetailInfo_price__I_VJn">문자열</strong>
                </body>
            </html>
        """.encode("utf-8")
        mock_soup_instance = mock_bs.return_value
        mock_soup_instance.find.return_value.get_text.return_value = "문자열"

        with pytest.raises(ValueError) as excinfo:
            now_price.get_price_from_naver(url, error_msg)
        assert str(excinfo.value) == error_msg
        mock_get.assert_called_once_with(url, headers=now_price.HEADERS)
        mock_bs.assert_called_once_with(mock_get.return_value.content, "html.parser")
        mock_soup_instance.find.assert_called_once_with(
            "strong", class_="DetailInfo_price__I_VJn"
        )


@patch("kimchi_gold.now_price.get_price_from_naver")
def test_get_domestic_gold_price_success(mock_get_price):
    mock_get_price.return_value = float(MOCK_DOMESTIC_PRICE_TEXT.replace(",", ""))
    price = now_price.get_domestic_gold_price()
    assert price == float(MOCK_DOMESTIC_PRICE_TEXT.replace(",", ""))
    mock_get_price.assert_called_once_with(
        "https://m.stock.naver.com/marketindex/metals/M04020000",
        "국내 금 가격 정보를 찾을 수 없습니다.",
    )


@patch("kimchi_gold.now_price.get_price_from_naver")
def test_get_international_gold_price_success(mock_get_price):
    mock_get_price.return_value = float(MOCK_INTERNATIONAL_PRICE_TEXT.replace(",", ""))
    price = now_price.get_international_gold_price()
    assert price == float(MOCK_INTERNATIONAL_PRICE_TEXT.replace(",", ""))
    mock_get_price.assert_called_once_with(
        "https://m.stock.naver.com/marketindex/metals/GCcv1",
        "국제 금 가격 정보를 찾을 수 없습니다.",
    )


@patch("kimchi_gold.now_price.get_price_from_naver")
def test_get_usd_krw_success(mock_get_price):
    mock_get_price.return_value = float(MOCK_USD_KRW_TEXT.replace(",", ""))
    price = now_price.get_usd_krw()
    assert price == float(MOCK_USD_KRW_TEXT.replace(",", ""))
    mock_get_price.assert_called_once_with(
        "https://m.stock.naver.com/marketindex/exchange/FX_USDKRW",
        "환율 정보를 찾을 수 없습니다.",
    )
