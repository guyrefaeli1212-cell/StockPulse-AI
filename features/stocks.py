import discord
import yfinance as yf


def get_info(symbol):

    symbol = symbol.upper()

    try:

        ticker = yf.Ticker(symbol)
        info = ticker.info

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )

        if price is None:

            return None

        return {

            "symbol": symbol,

            "name": info.get(
                "longName",
                symbol
            ),

            "price": price,

            "previous_close": info.get(
                "previousClose"
            ),

            "open": info.get(
                "open"
            ),

            "day_high": info.get(
                "dayHigh"
            ),

            "day_low": info.get(
                "dayLow"
            ),

            "52_week_high": info.get(
                "fiftyTwoWeekHigh"
            ),

            "52_week_low": info.get(
                "fiftyTwoWeekLow"
            ),

            "market_cap": info.get(
                "marketCap"
            ),

            "volume": info.get(
                "volume"
            ),

            "average_volume": info.get(
                "averageVolume"
            ),

            "pe_ratio": info.get(
                "trailingPE"
            ),

            "forward_pe": info.get(
                "forwardPE"
            ),

            "eps": info.get(
                "trailingEps"
            ),

            "dividend": info.get(
                "dividendYield"
            ),

            "sector": info.get(
                "sector",
                "לא ידוע"
            ),

            "industry": info.get(
                "industry",
                "לא ידוע"
            ),

            "country": info.get(
                "country",
                "לא ידוע"
            ),

            "website": info.get(
                "website",
                "לא ידוע"
            )

        }

    except Exception as error:

        print(
            f"Stock Error: {error}"
        )

        return None


def format_money(value):

    if value is None:

        return "לא זמין"

    if value >= 1_000_000_000_000:

        return f"${value / 1_000_000_000_000:.2f}T"

    if value >= 1_000_000_000:

        return f"${value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:

        return f"${value / 1_000_000:.2f}M"

    return f"${value:,.2f}"


def setup(bot):


    @bot.command()
    async def stock(ctx, symbol: str):

        data = get_info(symbol)

        if data is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        price = data["price"]
        previous = data["previous_close"]

        if previous:

            change = price - previous

            change_percent = (
                change / previous
            ) * 100

        else:

            change = 0
            change_percent = 0

        if change >= 0:

            emoji = "📈"

        else:

            emoji = "📉"

        embed = discord.Embed(

            title=(
                f"📊 {data['name']}"
            ),

            description=(
                f"סימול: `{data['symbol']}`"
            ),

            color=(
                discord.Color.green()
                if change >= 0
                else discord.Color.red()
            )

        )

        embed.add_field(

            name="💰 מחיר",

            value=(
                f"${price:,.2f}\n"
                f"{emoji} "
                f"{change:+,.2f} "
                f"({change_percent:+.2f}%)"
            ),

            inline=True

        )

        embed.add_field(

            name="📅 היום",

            value=(
                f"פתיחה: "
                f"${data['open']:,.2f}\n"
                f"גבוה: "
                f"${data['day_high']:,.2f}\n"
                f"נמוך: "
                f"${data['day_low']:,.2f}"
            ),

            inline=True

        )

        embed.add_field(

            name="📆 52 שבועות",

            value=(
                f"גבוה: "
                f"${data['52_week_high']:,.2f}\n"
                f"נמוך: "
                f"${data['52_week_low']:,.2f}"
            ),

            inline=True

        )

        embed.add_field(

            name="🏢 חברה",

            value=(
                f"Sector: "
                f"{data['sector']}\n"
                f"Industry: "
                f"{data['industry']}\n"
                f"Country: "
                f"{data['country']}"
            ),

            inline=True

        )

        embed.add_field(

            name="💼 נתונים פיננסיים",

            value=(
                f"Market Cap: "
                f"{format_money(data['market_cap'])}\n"
                f"P/E: "
                f"{data['pe_ratio']}\n"
                f"EPS: "
                f"{data['eps']}"
            ),

            inline=True

        )

        embed.add_field(

            name="📦 מסחר",

            value=(
                f"Volume: "
                f"{data['volume']:,}\n"
                f"Average Volume: "
                f"{data['average_volume']:,}"
            ),

            inline=True

        )

        if data["website"]:

            embed.add_field(

                name="🌐 אתר",

                value=data["website"],

                inline=False

            )

        embed.set_footer(

            text=(
                "Stock Bot • "
                "מידע פיננסי אינו המלצה להשקעה"
            )

        )

        await ctx.send(

            embed=embed

        )


    @bot.command()
    async def price(ctx, symbol: str):

        data = get_info(symbol)

        if data is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        await ctx.send(

            f"💰 מחיר **{symbol.upper()}**:\n"
            f"## ${data['price']:,.2f}"

        )


    @bot.command()
    async def compare(
        ctx,
        symbol1: str,
        symbol2: str
    ):

        first = get_info(symbol1)
        second = get_info(symbol2)

        if first is None or second is None:

            await ctx.send(
                "❌ אחת המניות לא נמצאה."
            )

            return

        first_change = (

            (
                first["price"]
                - first["previous_close"]
            )
            /
            first["previous_close"]
            * 100

        )

        second_change = (

            (
                second["price"]
                - second["previous_close"]
            )
            /
            second["previous_close"]
            * 100

        )

        embed = discord.Embed(

            title=(
                f"⚔️ {symbol1.upper()} "
                f"VS {symbol2.upper()}"
            ),

            color=discord.Color.blue()

        )

        embed.add_field(

            name=f"📊 {symbol1.upper()}",

            value=(
                f"💰 מחיר: "
                f"${first['price']:,.2f}\n"
                f"📈 שינוי: "
                f"{first_change:+.2f}%\n"
                f"🏢 שווי: "
                f"{format_money(first['market_cap'])}\n"
                f"📊 P/E: "
                f"{first['pe_ratio']}"
            ),

            inline=True

        )

        embed.add_field(

            name=f"📊 {symbol2.upper()}",

            value=(
                f"💰 מחיר: "
                f"${second['price']:,.2f}\n"
                f"📈 שינוי: "
                f"{second_change:+.2f}%\n"
                f"🏢 שווי: "
                f"{format_money(second['market_cap'])}\n"
                f"📊 P/E: "
                f"{second['pe_ratio']}"
            ),

            inline=True

        )

        await ctx.send(

            embed=embed

        )
