import csv
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
from now_price import calc_kimchi_premium

CURRENT_DIR: Path = Path(__file__).resolve().parent
ROOT_DIR: Path = CURRENT_DIR.parent.parent  # 루트 폴더
DATA_DIR: Path = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE: Path = DATA_DIR / "kimchi_gold_price_log.csv"


def is_today_logged(filename: Path) -> bool:
    """오늘 날짜(YYYY-MM-DD)가 이미 파일에 기록되어 있으면 True 반환"""
    if not filename.exists():
        return False
    today_str: str = datetime.now().strftime("%Y-%m-%d")
    with filename.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # 헤더 스킵
        for row in reader:
            if row and row[0].startswith(today_str):
                return True
    return False


def write_to_csv(row: List[str], filename: Path = DATA_FILE) -> None:
    file_exists: bool = filename.exists()
    with filename.open(mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            # 헤더 작성
            writer.writerow(
                [
                    "날짜",
                    "국내금(원/g)",
                    "국제금(달러/온스)",
                    "환율(원/달러)",
                    "김치프리미엄(원/g)",
                    "김치프리미엄(%)",
                ]
            )
        writer.writerow(row)


def collect_data() -> None:
    if is_today_logged(DATA_FILE):
        print("오늘 데이터가 이미 존재합니다. 수집을 중단합니다.")
        return
    try:
        result: Tuple[float, float, float, float, float] = calc_kimchi_premium()
        domestic, international, usdkrw, diff, premium = result
        today: str = datetime.now().strftime("%Y-%m-%d")
        row: List[str] = [
            today,
            f"{domestic:.2f}",
            f"{international:.2f}",
            f"{usdkrw:.2f}",
            f"{diff:.2f}",
            f"{premium:.2f}",
        ]
        write_to_csv(row)
        print(f"수집 완료: {row}")
    except Exception as e:
        print(f"수집 실패: {e}")


if __name__ == "__main__":
    collect_data()
