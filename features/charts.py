import discord
import yfinance as yf
import matplotlib.pyplot as plt
import os


def get_data(symbol, period="6mo"):

    data = yf.download(
        symbol.upper(),
        period=period,
        interval="1d",
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        return None

    if hasattr(data.columns, "levels"):

        try:
            data.columns = (
                data.columns
                .get_level_values(0)
            )
        except:
            pass

    return data


def create_chart(
    symbol,
    period="6mo"
):

    data = get_data(
        symbol,
        period
    )

    if data is None:
        return None

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

    data["BB_Middle"] = (
        data["Close"]
        .rolling(20)
        .mean()
    )

    std = (
        data["Close"]
        .rolling(20)
        .std()
    )

    data["BB_Upper"] = (
        data["BB_Middle"]
        + std * 2
    )

    data["BB_Lower"] = (
        data["BB_Middle"]
        - std * 2
    )

    data["RSI"] = calculate_rsi(
        data["Close"]
    )

    data["MACD"] = calculate_macd(
        data["Close"]
    )

    filename = (
        f"{symbol.upper()}_chart.png"
    )

    plt.figure(
        figsize=(14, 8)
    )

    plt.plot(
        data.index,
        data["Close"],
        label="Price"
    )

    plt.plot(
        data.index,
        data["SMA20"],
        label="SMA 20"
    )

    plt.plot(
        data.index,
        data["SMA50"],
        label="SMA 50"
    )

    plt.plot(
        data.index,
        data["BB_Upper"],
        linestyle="--",
        label="BB Upper"
    )

    plt.plot(
        data.index,
        data["BB_Lower"],
        linestyle="--",
        label="BB Lower"
    )

    plt.title(
        f"{symbol.upper()} Stock Chart"
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

    plt.savefig(
        filename
    )

    plt.close()

    return filename


def calculate_rsi(
    prices,
    period=14
):

    delta = prices.diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    average_gain = (
        gain
        .rolling(period)
        .mean()
    )

    average_loss = (
        loss
        .rolling(period)
        .mean()
    )

    rs = (
        average_gain /
        average_loss
    )

    return (
        100 -
        (
            100 /
            (1 + rs)
        )
    )


def calculate_macd(
    prices
):

    ema12 = (
        prices
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        prices
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    return ema12 - ema26


def setup(bot):


    @bot.command()
    async def chart(
        ctx,
        symbol: str
    ):

        symbol = symbol.upper()

        message = await ctx.send(
            f"⏳ יוצר גרף "
            f"עבור {symbol}..."
        )

        try:

            filename = create_chart(
                symbol
            )

            if filename is None:

                await message.edit(
                    content=(
                        "❌ לא מצאתי את המניה."
                    )
                )

                return

            await message.delete()

            await ctx.send(

                f"📈 **גרף {symbol}**",

                file=discord.File(
                    filename
                )

            )

            if os.path.exists(
                filename
            ):

                os.remove(
                    filename
                )

        except Exception as error:

            print(error)

            await message.edit(

                content=(
                    "❌ שגיאה ביצירת הגרף."
                )

            )
