import discord
import yfinance as yf
import asyncio
from datetime import datetime


# =====================================
# קבלת מידע על מניה
# =====================================

def get_stock(symbol):

    try:

        ticker = yf.Ticker(
            symbol.upper()
        )

        info = ticker.info

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )

        previous = info.get(
            "previousClose"
        )

        if price is None:

            return None

        change = 0

        if previous:

            change = (
                (price - previous)
                / previous
            ) * 100

        return {

            "symbol": symbol.upper(),

            "price": price,

            "change": change,

            "name": info.get(
                "longName",
                symbol.upper()
            )

        }

    except Exception as error:

        print(error)

        return None


# =====================================
# פקודות
# =====================================

def setup(bot):


    @bot.command()
    async def market(
        ctx,
        *symbols
    ):

        if not symbols:

            symbols = (
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "TSLA"
            )

        embed = discord.Embed(

            title="🌍 סיכום השוק",

            description=(
                "📊 מצב המניות שבחרת:"
            ),

            color=discord.Color.blue()

        )

        for symbol in symbols[:10]:

            stock = get_stock(
                symbol
            )

            if stock is None:

                continue

            emoji = (

                "📈"
                if stock["change"] >= 0
                else "📉"

            )

            embed.add_field(

                name=(
                    f"{emoji} "
                    f"{stock['symbol']}"
                ),

                value=(

                    f"💰 "
                    f"${stock['price']:,.2f}\n"
                    f"📊 "
                    f"{stock['change']:+.2f}%"

                ),

                inline=True

            )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def movers(ctx):

        symbols = [

            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "NFLX",
            "AMD",
            "INTC"

        ]

        stocks = []

        for symbol in symbols:

            stock = get_stock(
                symbol
            )

            if stock:

                stocks.append(
                    stock
                )

        stocks.sort(

            key=lambda x: x["change"],

            reverse=True

        )

        text = ""

        for index, stock in enumerate(

            stocks[:10],

            start=1

        ):

            emoji = (

                "🟢"
                if stock["change"] >= 0
                else "🔴"

            )

            text += (

                f"**{index}. "
                f"{stock['symbol']}** "
                f"{emoji} "
                f"{stock['change']:+.2f}%\n"

            )

        embed = discord.Embed(

            title="🚀 המניות הבולטות",

            description=text,

            color=discord.Color.green()

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def markettime(ctx):

        now = datetime.now()

        await ctx.send(

            f"🕒 זמן המערכת:\n"
            f"**{now.strftime('%H:%M:%S')}**"

        )


    @bot.command()
    async def scan(
        ctx,
        *symbols
    ):

        if not symbols:

            symbols = (

                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "TSLA",
                "NVDA"

            )

        message = await ctx.send(

            "🔍 סורק מניות..."

        )

        results = []

        for symbol in symbols[:20]:

            stock = get_stock(
                symbol
            )

            if stock is None:

                continue

            if stock["change"] >= 2:

                signal = "🚀 חזקה"

            elif stock["change"] <= -2:

                signal = "📉 חלשה"

            else:

                signal = "➡️ יציבה"

            results.append(

                f"**{stock['symbol']}** "
                f"{signal} "
                f"({stock['change']:+.2f}%)"

            )

        if not results:

            await message.edit(

                content=(
                    "❌ לא נמצאו נתונים."
                )

            )

            return

        embed = discord.Embed(

            title="🔍 תוצאות סריקה",

            description="\n".join(
                results
            ),

            color=discord.Color.purple()

        )

        await message.edit(

            content="",

            embed=embed

        )


    # =================================
    # סיכום אוטומטי כל שעה
    # =================================

    async def automatic_market_update():

        await bot.wait_until_ready()

        while not bot.is_closed():

            print(

                "📊 בדיקת שוק אוטומטית..."

            )

            stocks = [

                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "TSLA"

            ]

            for symbol in stocks:

                stock = get_stock(
                    symbol
                )

                if stock:

                    print(

                        f"{symbol}: "
                        f"{stock['change']:+.2f}%"

                    )

            await asyncio.sleep(
                3600
            )


    if not hasattr(

        bot,
        "market_task_started"

    ):

        bot.market_task_started = True

        bot.loop.create_task(

            automatic_market_update()

        )
