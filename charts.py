import matplotlib.pyplot as plt
import yfinance as yf
import os


# =====================================
# יצירת גרף מניה
# =====================================

def create_stock_chart(symbol):

    symbol = symbol.upper()

    # הורדת נתונים
    data = yf.download(
        symbol,
        period="6mo",
        interval="1d",
        auto_adjust=False
    )

    if data.empty:
        return None

    # במקרה של עמודות MultiIndex
    if hasattr(data.columns, "levels"):

        try:
            data.columns = data.columns.get_level_values(0)
        except:
            pass

    # חישוב ממוצעים נעים
    data["SMA20"] = data["Close"].rolling(
        window=20
    ).mean()

    data["SMA50"] = data["Close"].rolling(
        window=50
    ).mean()

    # Bollinger Bands
    data["BB_Middle"] = data["Close"].rolling(
        window=20
    ).mean()

    data["BB_Upper"] = (
        data["BB_Middle"]
        + data["Close"].rolling(20).std() * 2
    )

    data["BB_Lower"] = (
        data["BB_Middle"]
        - data["Close"].rolling(20).std() * 2
    )

    # יצירת גרף
    plt.figure(
        figsize=(12, 7)
    )

    # מחיר
    plt.plot(
        data.index,
        data["Close"],
        label="Price"
    )

    # SMA 20
    plt.plot(
        data.index,
        data["SMA20"],
        label="SMA 20"
    )

    # SMA 50
    plt.plot(
        data.index,
        data["SMA50"],
        label="SMA 50"
    )

    # Bollinger Upper
    plt.plot(
        data.index,
        data["BB_Upper"],
        linestyle="--",
        label="Bollinger Upper"
    )

    # Bollinger Lower
    plt.plot(
        data.index,
        data["BB_Lower"],
        linestyle="--",
        label="Bollinger Lower"
    )

    plt.title(
        f"{symbol} Stock Chart"
    )

    plt.xlabel(
        "Date"
    )

    plt.ylabel(
        "Price"
    )

    plt.legend()

    plt.grid(
        True
    )

    plt.tight_layout()

    # שמירת הגרף
    filename = f"{symbol}_chart.png"

    plt.savefig(
        filename
    )

    plt.close()

    return filename
