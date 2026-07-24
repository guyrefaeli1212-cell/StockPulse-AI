import discord
import yfinance as yf
import pandas as pd


# =====================================
# הורדת נתוני מניה
# =====================================

def get_data(symbol, period="6mo"):

    try:

        data = yf.download(
            symbol.upper(),
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if data.empty:

            return None

        # טיפול בעמודות מיוחדות של yfinance
        if isinstance(
            data.columns,
            pd.MultiIndex
        ):

            data.columns = (
                data.columns
                .get_level_values(0)
            )

        return data

    except Exception as error:

        print(error)

        return None


# =====================================
# SMA
# =====================================

def calculate_sma(data):

    data["SMA20"] = (
        data["Close"]
        .rolling(20)
        .mean()
    )

    data["SMA50"] = (
        data["Close"]
        .rolling(50)
        .mean()
    )

    data["SMA200"] = (
        data["Close"]
        .rolling(200)
        .mean()
    )

    return data


# =====================================
# EMA
# =====================================

def calculate_ema(data):

    data["EMA12"] = (
        data["Close"]
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    data["EMA26"] = (
        data["Close"]
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    return data


# =====================================
# RSI
# =====================================

def calculate_rsi(data):

    change = (
        data["Close"]
        .diff()
    )

    gain = change.where(
        change > 0,
        0
    )

    loss = -change.where(
        change < 0,
        0
    )

    average_gain = (
        gain.rolling(14)
        .mean()
    )

    average_loss = (
        loss.rolling(14)
        .mean()
    )

    rs = (
        average_gain /
        average_loss
    )

    data["RSI"] = (
        100 -
        (
            100 /
            (1 + rs)
        )
    )

    return data


# =====================================
# MACD
# =====================================

def calculate_macd(data):

    ema12 = (
        data["Close"]
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        data["Close"]
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    data["MACD"] = (
        ema12 -
        ema26
    )

    data["MACD_Signal"] = (
        data["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )

    data["MACD_Histogram"] = (
        data["MACD"] -
        data["MACD_Signal"]
    )

    return data


# =====================================
# Bollinger Bands
# =====================================

def calculate_bollinger(data):

    middle = (
        data["Close"]
        .rolling(20)
        .mean()
    )

    deviation = (
        data["Close"]
        .rolling(20)
        .std()
    )

    data["BB_Middle"] = middle

    data["BB_Upper"] = (
        middle +
        (deviation * 2)
    )

    data["BB_Lower"] = (
        middle -
        (deviation * 2)
    )

    return data


# =====================================
# Stochastic Oscillator
# =====================================

def calculate_stochastic(data):

    lowest = (
        data["Low"]
        .rolling(14)
        .min()
    )

    highest = (
        data["High"]
        .rolling(14)
        .max()
    )

    data["%K"] = (

        (
            data["Close"] -
            lowest
        )
        /
        (
            highest -
            lowest
        )
        * 100

    )

    data["%D"] = (
        data["%K"]
        .rolling(3)
        .mean()
    )

    return data


# =====================================
# ATR — תנודתיות
# =====================================

def calculate_atr(data):

    high_low = (
        data["High"] -
        data["Low"]
    )

    high_close = abs(

        data["High"] -
        data["Close"].shift()

    )

    low_close = abs(

        data["Low"] -
        data["Close"].shift()

    )

    true_range = pd.concat(

        [
            high_low,
            high_close,
            low_close
        ],

        axis=1

    ).max(axis=1)

    data["ATR"] = (
        true_range
        .rolling(14)
        .mean()
    )

    return data


# =====================================
# זיהוי מגמה
# =====================================

def detect_trend(data):

    latest = data.iloc[-1]

    if (

        latest["SMA20"] >
        latest["SMA50"] >
        latest["SMA200"]

    ):

        return "🚀 מגמת עלייה חזקה"

    if (

        latest["SMA20"] <
        latest["SMA50"] <
        latest["SMA200"]

    ):

        return "📉 מגמת ירידה חזקה"

    if (

        latest["SMA20"] >
        latest["SMA50"]

    ):

        return "📈 מגמת עלייה"

    if (

        latest["SMA20"] <
        latest["SMA50"]

    ):

        return "📉 מגמת ירידה"

    return "➡️ מגמה צדדית"


# =====================================
# מערכת ניקוד
# =====================================

def calculate_score(data):

    latest = data.iloc[-1]

    score = 0

    reasons = []

    # RSI
    if latest["RSI"] < 30:

        score += 2

        reasons.append(
            "RSI נמוך — אפשרות למכירת יתר"
        )

    elif latest["RSI"] > 70:

        score -= 2

        reasons.append(
            "RSI גבוה — אפשרות לקניית יתר"
        )

    # SMA
    if latest["SMA20"] > latest["SMA50"]:

        score += 1

        reasons.append(
            "SMA20 מעל SMA50"
        )

    else:

        score -= 1

        reasons.append(
            "SMA20 מתחת SMA50"
        )

    # MACD
    if (
        latest["MACD"] >
        latest["MACD_Signal"]
    ):

        score += 1

        reasons.append(
            "MACD חיובי"
        )

    else:

        score -= 1

        reasons.append(
            "MACD שלילי"
        )

    # Stochastic
    if latest["%K"] < 20:

        score += 1

        reasons.append(
            "Stochastic נמוך"
        )

    elif latest["%K"] > 80:

        score -= 1

        reasons.append(
            "Stochastic גבוה"
        )

    # מחיר מול Bollinger
    if (
        latest["Close"] <
        latest["BB_Lower"]
    ):

        score += 1

        reasons.append(
            "המחיר מתחת ל-Bollinger Lower"
        )

    elif (
        latest["Close"] >
        latest["BB_Upper"]
    ):

        score -= 1

        reasons.append(
            "המחיר מעל Bollinger Upper"
        )

    if score >= 3:

        signal = "🟢 BUY"

    elif score <= -3:

        signal = "🔴 SELL"

    else:

        signal = "⚪ HOLD"

    return signal, score, reasons


# =====================================
# ניתוח מלא
# =====================================

def analyze_stock(symbol):

    data = get_data(symbol)

    if data is None:

        return None

    data = calculate_sma(data)

    data = calculate_ema(data)

    data = calculate_rsi(data)

    data = calculate_macd(data)

    data = calculate_bollinger(data)

    data = calculate_stochastic(data)

    data = calculate_atr(data)

    data = data.dropna()

    latest = data.iloc[-1]

    signal, score, reasons = (
        calculate_score(data)
    )

    return {

        "price": latest["Close"],

        "sma20": latest["SMA20"],

        "sma50": latest["SMA50"],

        "sma200": latest["SMA200"],

        "ema12": latest["EMA12"],

        "ema26": latest["EMA26"],

        "rsi": latest["RSI"],

        "macd": latest["MACD"],

        "macd_signal":
            latest["MACD_Signal"],

        "stochastic":
            latest["%K"],

        "atr": latest["ATR"],

        "trend":
            detect_trend(data),

        "signal": signal,

        "score": score,

        "reasons": reasons

    }


# =====================================
# פקודות Discord
# =====================================

def setup(bot):


    @bot.command()
    async def analyze(
        ctx,
        symbol: str
    ):

        symbol = symbol.upper()

        await ctx.send(
            f"⏳ מנתח את {symbol}..."
        )

        result = analyze_stock(
            symbol
        )

        if result is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        embed = discord.Embed(

            title=(
                f"📊 ניתוח טכני — "
                f"{symbol}"
            ),

            description=(

                f"💰 מחיר: "
                f"${result['price']:,.2f}\n"
                f"🎯 איתות: "
                f"{result['signal']}\n"
                f"⭐ ציון: "
                f"{result['score']}\n"
                f"📈 מגמה: "
                f"{result['trend']}"

            ),

            color=discord.Color.blue()

        )

        embed.add_field(

            name="📏 ממוצעים",

            value=(

                f"SMA20: "
                f"${result['sma20']:,.2f}\n"
                f"SMA50: "
                f"${result['sma50']:,.2f}\n"
                f"SMA200: "
                f"${result['sma200']:,.2f}\n"
                f"EMA12: "
                f"${result['ema12']:,.2f}\n"
                f"EMA26: "
                f"${result['ema26']:,.2f}"

            ),

            inline=True

        )

        embed.add_field(

            name="📊 אינדיקטורים",

            value=(

                f"RSI: "
                f"{result['rsi']:.2f}\n"
                f"MACD: "
                f"{result['macd']:.2f}\n"
                f"Signal: "
                f"{result['macd_signal']:.2f}\n"
                f"Stochastic: "
                f"{result['stochastic']:.2f}\n"
                f"ATR: "
                f"{result['atr']:.2f}"

            ),

            inline=True

        )

        reasons_text = ""

        for reason in result[
            "reasons"
        ]:

            reasons_text += (
                f"• {reason}\n"
            )

        embed.add_field(

            name="🧠 הסיבות לניקוד",

            value=reasons_text[
                :1024
            ],

            inline=False

        )

        embed.set_footer(

            text=(

                "⚠️ הניתוח הוא מידע בלבד "
                "ולא המלצה פיננסית"

            )

        )

        await ctx.send(

            embed=embed

        )
