import yfinance as yf
import pandas as pd


# =====================================
# קבלת נתוני מניה
# =====================================

def get_stock_data(symbol, period="6mo"):

    symbol = symbol.upper()

    ticker = yf.Ticker(symbol)

    data = ticker.history(period=period)

    if data.empty:
        return None

    return data


# =====================================
# ממוצעים נעים
# =====================================

def moving_averages(data):

    data["SMA20"] = data["Close"].rolling(
        window=20
    ).mean()

    data["SMA50"] = data["Close"].rolling(
        window=50
    ).mean()

    return data


# =====================================
# RSI
# =====================================

def calculate_rsi(data, period=14):

    delta = data["Close"].diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    average_gain = gain.rolling(
        period
    ).mean()

    average_loss = loss.rolling(
        period
    ).mean()

    relative_strength = (
        average_gain /
        average_loss
    )

    rsi = 100 - (
        100 /
        (1 + relative_strength)
    )

    data["RSI"] = rsi

    return data


# =====================================
# MACD
# =====================================

def calculate_macd(data):

    ema12 = data["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema26 = data["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    data["MACD"] = ema12 - ema26

    data["Signal"] = data["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    data["MACD_Histogram"] = (
        data["MACD"] -
        data["Signal"]
    )

    return data


# =====================================
# Bollinger Bands
# =====================================

def calculate_bollinger(data):

    middle_band = data["Close"].rolling(
        window=20
    ).mean()

    standard_deviation = data["Close"].rolling(
        window=20
    ).std()

    data["BB_Middle"] = middle_band

    data["BB_Upper"] = (
        middle_band +
        (standard_deviation * 2)
    )

    data["BB_Lower"] = (
        middle_band -
        (standard_deviation * 2)
    )

    return data


# =====================================
# זיהוי מגמה
# =====================================

def detect_trend(data):

    latest = data.iloc[-1]

    if (
        latest["SMA20"] >
        latest["SMA50"]
    ):

        return "📈 מגמת עלייה"

    elif (
        latest["SMA20"] <
        latest["SMA50"]
    ):

        return "📉 מגמת ירידה"

    else:

        return "➡️ מגמה צדדית"


# =====================================
# איתות RSI
# =====================================

def rsi_signal(rsi):

    if rsi < 30:

        return "🟢 ייתכן שהמניה נמכרת ביתר"

    elif rsi > 70:

        return "🔴 ייתכן שהמניה נקנית ביתר"

    else:

        return "⚪ RSI ניטרלי"


# =====================================
# איתות MACD
# =====================================

def macd_signal(macd, signal):

    if macd > signal:

        return "🟢 MACD חיובי"

    elif macd < signal:

        return "🔴 MACD שלילי"

    else:

        return "⚪ MACD ניטרלי"


# =====================================
# איתות משולב
# =====================================

def generate_signal(data):

    latest = data.iloc[-1]

    score = 0

    # RSI
    if latest["RSI"] < 30:

        score += 2

    elif latest["RSI"] > 70:

        score -= 2

    # ממוצעים נעים
    if latest["SMA20"] > latest["SMA50"]:

        score += 1

    else:

        score -= 1

    # MACD
    if latest["MACD"] > latest["Signal"]:

        score += 1

    else:

        score -= 1

    # Bollinger
    if latest["Close"] < latest["BB_Lower"]:

        score += 1

    elif latest["Close"] > latest["BB_Upper"]:

        score -= 1

    # תוצאה
    if score >= 3:

        return "🟢 BUY", score

    elif score <= -3:

        return "🔴 SELL", score

    else:

        return "⚪ HOLD", score


# =====================================
# ניתוח מלא
# =====================================

def full_analysis(symbol):

    data = get_stock_data(symbol)

    if data is None:

        return None

    data = moving_averages(data)

    data = calculate_rsi(data)

    data = calculate_macd(data)

    data = calculate_bollinger(data)

    latest = data.iloc[-1]

    signal, score = generate_signal(
        data
    )

    return {

        "symbol": symbol.upper(),

        "price": latest["Close"],

        "sma20": latest["SMA20"],

        "sma50": latest["SMA50"],

        "rsi": latest["RSI"],

        "macd": latest["MACD"],

        "macd_signal": latest["Signal"],

        "trend": detect_trend(data),

        "rsi_signal": rsi_signal(
            latest["RSI"]
        ),

        "macd_signal_text": macd_signal(
            latest["MACD"],
            latest["Signal"]
        ),

        "signal": signal,

        "score": score,

        "data": data

    }
