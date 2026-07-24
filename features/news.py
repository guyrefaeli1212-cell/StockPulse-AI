import yfinance as yf
import discord


def get_stock_news(symbol, limit=5):

    symbol = symbol.upper()

    try:

        ticker = yf.Ticker(symbol)
        news = ticker.news

        if not news:
            return []

        results = []

        for item in news[:limit]:

            content = item.get("content", {})

            title = content.get(
                "title",
                "ללא כותרת"
            )

            provider = content.get(
                "provider",
                {}
            )

            publisher = provider.get(
                "displayName",
                "מקור לא ידוע"
            )

            click_url = content.get(
                "clickThroughUrl",
                {}
            )

            url = click_url.get(
                "url",
                ""
            )

            results.append({
                "title": title,
                "publisher": publisher,
                "url": url
            })

        return results

    except Exception as error:

        print(f"News Error: {error}")

        return []


def setup(bot):

    @bot.command()
    async def news(ctx, symbol: str):

        symbol = symbol.upper()

        await ctx.send(
            f"⏳ מחפש חדשות על {symbol}..."
        )

        articles = get_stock_news(
            symbol,
            limit=5
        )

        if not articles:

            await ctx.send(
                f"❌ לא נמצאו חדשות עבור {symbol}"
            )

            return

        embed = discord.Embed(
            title=f"📰 חדשות — {symbol}",
            color=discord.Color.blue()
        )

        for index, article in enumerate(
            articles,
            start=1
        ):

            title = article["title"]
            publisher = article["publisher"]
            url = article["url"]

            if url:

                value = (
                    f"📰 {publisher}\n"
                    f"🔗 [לקריאת הכתבה]({url})"
                )

            else:

                value = f"📰 {publisher}"

            embed.add_field(
                name=f"{index}. {title}",
                value=value,
                inline=False
            )

        await ctx.send(
            embed=embed
        )
