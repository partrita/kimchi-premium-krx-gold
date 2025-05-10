from unittest.mock import patch
from datetime import datetime
import csv
from kimchi_gold.collect_price import collect_data, is_today_logged, write_to_csv

# 테스트 데이터
MOCK_DOMESTIC_PRICE = 150000.00
MOCK_INTERNATIONAL_PRICE = 3345.00
MOCK_USD_KRW = 1399.00
MOCK_INTERNATIONAL_KRW_PER_G = (MOCK_INTERNATIONAL_PRICE * MOCK_USD_KRW) / 31.1035
MOCK_DIFFERENCE = MOCK_DOMESTIC_PRICE - MOCK_INTERNATIONAL_KRW_PER_G
MOCK_PREMIUM_PERCENT = (MOCK_DIFFERENCE / MOCK_INTERNATIONAL_KRW_PER_G) * 100
MOCK_TODAY_STR = datetime.now().strftime("%Y-%m-%d")
MOCK_CSV_HEADER = [
    "날짜",
    "국내금(원/g)",
    "국제금(달러/온스)",
    "환율(원/달러)",
    "김치프리미엄(원/g)",
    "김치프리미엄(%)",
]
MOCK_CSV_ROW = [
    MOCK_TODAY_STR,
    f"{MOCK_DOMESTIC_PRICE:.2f}",
    f"{MOCK_INTERNATIONAL_PRICE:.2f}",
    f"{MOCK_USD_KRW:.2f}",
    f"{MOCK_DIFFERENCE:.2f}",
    f"{MOCK_PREMIUM_PERCENT:.2f}",
]


def test_is_today_logged_new_file(tmp_path):
    filepath = tmp_path / "test.csv"
    assert not is_today_logged(filepath)


def test_is_today_logged_not_logged(tmp_path):
    filepath = tmp_path / "test.csv"
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["날짜", "값"])
        writer.writerow(["2025-05-09", "100"])
    assert not is_today_logged(filepath)


def test_is_today_logged_logged(tmp_path):
    filepath = tmp_path / "test.csv"
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["날짜", "값"])
        writer.writerow([MOCK_TODAY_STR, "200"])
    assert is_today_logged(filepath)


def test_write_to_csv_new_file(tmp_path):
    filepath = tmp_path / "new_test.csv"
    write_to_csv(MOCK_CSV_ROW, filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        data = next(reader)
        assert header == MOCK_CSV_HEADER
        assert data == MOCK_CSV_ROW


def test_write_to_csv_existing_file(tmp_path):
    filepath = tmp_path / "existing_test.csv"
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(MOCK_CSV_HEADER)
        writer.writerow(
            ["2025-05-09", "100.00", "1900.00", "1340.00", "10000.00", "1.00"]
        )

    write_to_csv(MOCK_CSV_ROW, filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        next(reader)  # 기존 row1, 사용하지 않으므로 그냥 넘김
        row2 = next(reader)
        assert header == MOCK_CSV_HEADER
        assert row2 == MOCK_CSV_ROW


@patch("kimchi_gold.collect_price.is_today_logged", return_value=True)
def test_collect_data_already_logged(mock_logged, capsys):
    collect_data()
    captured = capsys.readouterr()
    assert "오늘 데이터가 이미 존재합니다. 수집을 중단합니다." in captured.out
    mock_logged.assert_called_once()


@patch(
    "kimchi_gold.collect_price.calc_kimchi_premium", side_effect=ValueError("API Error")
)
@patch("kimchi_gold.collect_price.is_today_logged", return_value=False)
def test_collect_data_failure(mock_logged, mock_premium, capsys):
    collect_data()
    captured = capsys.readouterr()
    assert "수집 실패: API Error" in captured.out
    mock_logged.assert_called_once()
    mock_premium.assert_called_once()
