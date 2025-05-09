import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime, timedelta
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# --- 기간 설정 (몇 개월치 데이터를 볼지 지정) ---
MONTHS = 12  # 원하는 개월 수로 변경하세요 (예: 6, 12, 24 등)

# --- File Path Configuration ---
CURRENT_DIR: Path = Path(__file__).resolve().parent
ROOT_DIR: Path = CURRENT_DIR.parent.parent  # Root folder
DATA_DIR: Path = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE: Path = DATA_DIR / "kimchi_gold_price_log.csv"
OUTPUT_FILE: Path = DATA_DIR / f"kimchi_gold_price_recent_{MONTHS}months.png"

# --- Data Loading and Preparation ---
try:
    df: pd.DataFrame = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    print(f"Error: {DATA_FILE} not found.")
    exit()

df["날짜"] = pd.to_datetime(df["날짜"]).dt.date
df = df.set_index("날짜")

# --- Date Filtering ---
today: datetime.date = datetime.now().date()
months_ago: datetime.date = today - timedelta(days=MONTHS * 30)  # Approximate N months
df_period: pd.DataFrame = df[df.index >= months_ago]

if df_period.empty:
    print(f"No data available for the last {MONTHS} months.")
    exit()

# --- Plotting ---
plt.style.use("seaborn-v0_8-whitegrid")
fig: Figure
axes: list[Axes]
fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 15))
plt.subplots_adjust(hspace=0.5)

# --- Plot 1: Kimchi Premium (%) ---
ax_kimchi: Axes = axes[0]
ax_kimchi.plot(
    df_period.index,
    df_period["김치프리미엄(%)"],
    label="Kimchi Premium (%)",
    color="red",
    linestyle="--",
    marker="d",
)
ax_kimchi.set_ylabel("Kimchi Premium (%)")
ax_kimchi.set_title(f"Recent {MONTHS} Months: Kimchi Premium (%)")
ax_kimchi.legend(loc="upper left")
ax_kimchi.tick_params(axis="x", rotation=45)
ax_kimchi.xaxis.set_major_locator(mdates.AutoDateLocator())
ax_kimchi.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax_kimchi.grid(True)

# --- Plot 2: Domestic vs International Gold Price ---
ax_gold: Axes = axes[1]
ax_gold.plot(
    df_period.index,
    df_period["국내금(원/g)"],
    label="Domestic Gold (KRW/g)",
    marker="o",
)
ax_gold.plot(
    df_period.index,
    df_period["국제금(달러/온스)"] * (1 / 31.1035) * df_period["환율(원/달러)"],
    label="International Gold (KRW/g, FX adjusted)",
    marker="x",
)
ax_gold.set_ylabel("Price (KRW/g)")
ax_gold.set_title(f"Recent {MONTHS} Months: Domestic vs International Gold Price")
ax_gold.legend()
ax_gold.tick_params(axis="x", rotation=45)
ax_gold.xaxis.set_major_locator(mdates.AutoDateLocator())
ax_gold.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax_gold.grid(True)

# --- Plot 3: Exchange Rate Trend ---
ax_exchange: Axes = axes[2]
ax_exchange.plot(
    df_period.index,
    df_period["환율(원/달러)"],
    label="Exchange Rate (KRW/USD)",
    color="purple",
    marker="^",
)
ax_exchange.set_ylabel("Exchange Rate (KRW/USD)")
ax_exchange.set_title(f"Recent {MONTHS} Months: Exchange Rate Trend")
ax_exchange.legend()
ax_exchange.tick_params(axis="x", rotation=45)
ax_exchange.xaxis.set_major_locator(mdates.AutoDateLocator())
ax_exchange.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax_exchange.grid(True)

plt.tight_layout()
plt.savefig(OUTPUT_FILE)
plt.show()

print(f"Visualization of the recent {MONTHS} months data saved to {OUTPUT_FILE}")
