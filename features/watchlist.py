import discord
import json
import os
import yfinance as yf


WATCHLIST_FILE = "watchlists.json"


def load_watchlists():

    if not os.path.exists(WATCHLIST_FILE):
        return {}

    try:

        with open(
            WATCHLIST_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return {}


def save_watchlists(data):

    with open(
        WATCHLIST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_stock_data(symbol):

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

            "price": price,

            "change": change,

            "market_cap": info.get(
                "marketCap"
            ),

            "pe": info.get(
                "trailingPE"
            ),

            "sector": info.get(
                "sector",
                "לא ידוע"
            )

        }

    except Exception as error:

        print(error)

        return None


def setup(bot):


    @bot.command()
    async def watch(
        ctx,
        symbol: str
    ):

        symbol = symbol.upper()

        data = load_watchlists()

        user_id = str(
            ctx.author.id
        )

        if user_id not in data:

            data[user_id] = []

        if symbol in data[user_id]:

            await ctx.send(
                f"⚠️ {symbol} כבר ברשימה."
            )

            return

        stock_data = get_stock_data(
            symbol
        )

        if stock_data is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        data[user_id].append(
            symbol
        )

        save_watchlists(
            data
        )

        await ctx.send(

            f"⭐ **{symbol} נוסף לרשימת המעקב שלך!**\n"
            f"💰 מחיר: "
            f"${stock_data['price']:,.2f}"

        )


    @bot.command()
    async def unwatch(
        ctx,
        symbol: str
    ):

        symbol = symbol.upper()

        data = load_watchlists()

        user_id = str(
            ctx.author.id
        )

        if user_id not in data:

            await ctx.send(
                "📭 רשימת המעקב ריקה."
            )

            return

        if symbol not in data[user_id]:

            await ctx.send(
                f"❌ {symbol} לא ברשימה."
            )

            return

        data[user_id].remove(
            symbol
        )

        save_watchlists(
            data
        )

        await ctx.send(

            f"🗑️ **{symbol} הוסר "
            f"מרשימת המעקב.**"

        )


    @bot.command()
    async def watchlist(ctx):

        data = load_watchlists()

        user_id = str(
            ctx.author.id
        )

        symbols = data.get(
            user_id,
            []
        )

        if not symbols:

            await ctx.send(
                "📭 רשימת המעקב שלך ריקה."
            )

            return

        embed = discord.Embed(

            title="⭐ רשימת המעקב שלך",

            color=discord.Color.gold()

        )

        text = ""

        for symbol in symbols:

            stock = get_stock_data(
                symbol
            )

            if stock is None:

                text += (
                    f"❌ {symbol} — אין נתונים\n"
                )

                continue

            emoji = (
                "📈"
                if stock["change"] >= 0
                else "📉"
            )

            text += (

                f"{emoji} **{symbol}**\n"
                f"💰 ${stock['price']:,.2f}\n"
                f"📊 "
                f"{stock['change']:+.2f}%\n\n"

            )

        embed.description = text[
            :4000
        ]

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def comparefull(
        ctx,
        symbol1: str,
        symbol2: str
    ):

        first = get_stock_data(
            symbol1
        )

        second = get_stock_data(
            symbol2
        )

        if first is None or second is None:

            await ctx.send(
                "❌ לא הצלחתי למצוא אחת מהמניות."
            )

            return

        symbol1 = symbol1.upper()
        symbol2 = symbol2.upper()

        embed = discord.Embed(

            title=(
                f"⚔️ {symbol1} VS {symbol2}"
            ),

            color=discord.Color.blue()

        )

        embed.add_field(

            name=f"📊 {symbol1}",

            value=(

                f"💰 מחיר: "
                f"${first['price']:,.2f}\n"
                f"📈 שינוי: "
                f"{first['change']:+.2f}%\n"
                f"📊 P/E: "
                f"{first['pe']}\n"
                f"🏭 Sector: "
                f"{first['sector']}"

            ),

            inline=True

        )

        embed.add_field(

            name=f"📊 {symbol2}",

            value=(

                f"💰 מחיר: "
                f"${second['price']:,.2f}\n"
                f"📈 שינוי: "
                f"{second['change']:+.2f}%\n"
                f"📊 P/E: "
                f"{second['pe']}\n"
                f"🏭 Sector: "
                f"{second['sector']}"

            ),

            inline=True

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def watchcount(ctx):

        data = load_watchlists()

        user_id = str(
            ctx.author.id
        )

        amount = len(
            data.get(
                user_id,
                []
            )
        )

        await ctx.send(

            f"⭐ יש לך "
            f"**{amount}** "
            f"מניות ברשימת המעקב."

        )
