import discord
from discord.ext import commands


def setup(bot):

    @bot.command()
    async def commands(ctx):

        embed = discord.Embed(

            title="📚 כל פקודות Stock Bot",

            description=(
                "השתמש בפקודה "
                "`!category <שם>` "
                "כדי לראות קטגוריה מסוימת."
            ),

            color=discord.Color.blue()

        )

        embed.add_field(

            name="📊 מניות",

            value=(
                "`!stock AAPL`\n"
                "`!price AAPL`\n"
                "`!compare AAPL MSFT`\n"
                "`!analyze AAPL`\n"
                "`!chart AAPL`"
            ),

            inline=False

        )

        embed.add_field(

            name="💼 תיק השקעות",

            value=(
                "`!portfolio`\n"
                "`!buy AAPL 10`\n"
                "`!sell AAPL 10`\n"
                "`!balance`\n"
                "`!transactions`"
            ),

            inline=False

        )

        embed.add_field(

            name="⭐ מעקב",

            value=(
                "`!watch AAPL`\n"
                "`!unwatch AAPL`\n"
                "`!watchlist`\n"
                "`!comparefull AAPL MSFT`"
            ),

            inline=False

        )

        embed.add_field(

            name="🚨 התראות",

            value=(
                "`!alert AAPL 250`\n"
                "`!myalerts`\n"
                "`!removealert 1`\n"
                "`!clearalerts`"
            ),

            inline=False

        )

        embed.add_field(

            name="🎮 כלכלה",

            value=(
                "`!economy`\n"
                "`!daily`\n"
                "`!work`\n"
                "`!achievement`\n"
                "`!leaderboard`"
            ),

            inline=False

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def category(
        ctx,
        category_name: str
    ):

        category_name = (
            category_name.lower()
        )

        categories = {

            "stocks": (
                "📊 **מניות**\n\n"
                "`!stock AAPL` — מידע מלא\n"
                "`!price AAPL` — מחיר\n"
                "`!compare AAPL MSFT` — השוואה\n"
                "`!analyze AAPL` — ניתוח טכני\n"
                "`!chart AAPL` — גרף"
            ),

            "מניות": (
                "📊 **מניות**\n\n"
                "`!stock AAPL`\n"
                "`!price AAPL`\n"
                "`!compare AAPL MSFT`\n"
                "`!analyze AAPL`\n"
                "`!chart AAPL`"
            ),

            "portfolio": (
                "💼 **תיק השקעות**\n\n"
                "`!portfolio`\n"
                "`!buy AAPL 10`\n"
                "`!sell AAPL 10`\n"
                "`!balance`\n"
                "`!transactions`"
            ),

            "תיק": (
                "💼 **תיק השקעות**\n\n"
                "`!portfolio`\n"
                "`!buy AAPL 10`\n"
                "`!sell AAPL 10`\n"
                "`!balance`\n"
                "`!transactions`"
            ),

            "alerts": (
                "🚨 **התראות**\n\n"
                "`!alert AAPL 250`\n"
                "`!myalerts`\n"
                "`!removealert 1`\n"
                "`!clearalerts`"
            ),

            "watchlist": (
                "⭐ **רשימת מעקב**\n\n"
                "`!watch AAPL`\n"
                "`!unwatch AAPL`\n"
                "`!watchlist`\n"
                "`!watchcount`"
            ),

            "economy": (
                "🎮 **כלכלה**\n\n"
                "`!economy`\n"
                "`!daily`\n"
                "`!work`\n"
                "`!achievement`\n"
                "`!leaderboard`"
            )

        }

        if category_name not in categories:

            await ctx.send(

                "❌ קטגוריה לא נמצאה.\n"
                "נסה: `stocks`, `portfolio`, "
                "`alerts`, `watchlist`, `economy`"

            )

            return

        embed = discord.Embed(

            title="📚 קטגוריית פקודות",

            description=categories[
                category_name
            ],

            color=discord.Color.blue()

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def ping(ctx):

        latency = round(
            bot.latency * 1000
        )

        await ctx.send(

            f"🏓 Pong!\n"
            f"📡 Latency: "
            f"**{latency}ms**"

        )


    @bot.command()
    async def botinfo(ctx):

        embed = discord.Embed(

            title="🤖 Stock Bot",

            description=(

                "בוט מניות וירטואלי "
                "עם מערכת פיצ'רים מודולרית."

            ),

            color=discord.Color.green()

        )

        embed.add_field(

            name="📊 תחום",

            value="מניות ושוק ההון",

            inline=True

        )

        embed.add_field(

            name="🚀 מערכת",

            value="Plugin System",

            inline=True

        )

        embed.add_field(

            name="📈 פיצ'רים",

            value="10+ מערכות",

            inline=True

        )

        embed.set_footer(

            text=(
                "מידע פיננסי בלבד — "
                "לא המלצה להשקעה"
            )

        )

        await ctx.send(
            embed=embed
        )
