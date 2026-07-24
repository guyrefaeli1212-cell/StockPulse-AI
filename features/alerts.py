import discord
import yfinance as yf
import asyncio
import json
import os


ALERTS_FILE = "alerts.json"


def load_alerts():

    if not os.path.exists(ALERTS_FILE):

        return {}

    try:

        with open(
            ALERTS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return {}


def save_alerts(alerts):

    with open(
        ALERTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            alerts,
            file,
            indent=4,
            ensure_ascii=False
        )


def get_price(symbol):

    try:

        ticker = yf.Ticker(
            symbol.upper()
        )

        data = ticker.history(
            period="1d"
        )

        if data.empty:

            return None

        return float(
            data["Close"].iloc[-1]
        )

    except:

        return None


def setup(bot):


    @bot.command()
    async def alert(
        ctx,
        symbol: str,
        target_price: float
    ):

        symbol = symbol.upper()

        current_price = get_price(
            symbol
        )

        if current_price is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        alerts = load_alerts()

        user_id = str(
            ctx.author.id
        )

        if user_id not in alerts:

            alerts[user_id] = []

        alerts[user_id].append({

            "symbol": symbol,

            "target": target_price,

            "created_price":
                current_price

        })

        save_alerts(
            alerts
        )

        await ctx.send(

            f"🚨 התראה נוצרה!\n"
            f"📊 מניה: **{symbol}**\n"
            f"💰 מחיר נוכחי: "
            f"${current_price:,.2f}\n"
            f"🎯 מחיר יעד: "
            f"${target_price:,.2f}"

        )


    @bot.command()
    async def myalerts(ctx):

        alerts = load_alerts()

        user_id = str(
            ctx.author.id
        )

        user_alerts = alerts.get(
            user_id,
            []
        )

        if not user_alerts:

            await ctx.send(
                "📭 אין לך התראות פעילות."
            )

            return

        embed = discord.Embed(

            title="🚨 ההתראות שלי",

            color=discord.Color.orange()

        )

        text = ""

        for index, item in enumerate(

            user_alerts,
            start=1

        ):

            current_price = get_price(
                item["symbol"]
            )

            if current_price:

                difference = (

                    current_price -
                    item["target"]

                )

                status = (

                    "🟢 הגיע ליעד"
                    if difference >= 0
                    else "⏳ ממתין"

                )

                text += (

                    f"**{index}. "
                    f"{item['symbol']}**\n"
                    f"💰 עכשיו: "
                    f"${current_price:,.2f}\n"
                    f"🎯 יעד: "
                    f"${item['target']:,.2f}\n"
                    f"{status}\n\n"

                )

        embed.description = text[
            :4000
        ]

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def removealert(
        ctx,
        alert_number: int
    ):

        alerts = load_alerts()

        user_id = str(
            ctx.author.id
        )

        user_alerts = alerts.get(
            user_id,
            []
        )

        if (
            alert_number < 1
            or alert_number > len(
                user_alerts
            )
        ):

            await ctx.send(
                "❌ מספר התראה לא תקין."
            )

            return

        removed = user_alerts.pop(
            alert_number - 1
        )

        alerts[user_id] = (
            user_alerts
        )

        save_alerts(
            alerts
        )

        await ctx.send(

            f"🗑️ ההתראה נמחקה:\n"
            f"**{removed['symbol']}** "
            f"— יעד "
            f"${removed['target']:,.2f}"

        )


    @bot.command()
    async def clearalerts(ctx):

        alerts = load_alerts()

        user_id = str(
            ctx.author.id
        )

        alerts[user_id] = []

        save_alerts(
            alerts
        )

        await ctx.send(
            "🧹 כל ההתראות נמחקו."
        )


    async def check_alerts():

        await bot.wait_until_ready()

        while not bot.is_closed():

            alerts = load_alerts()

            changed = False

            for user_id in list(
                alerts.keys()
            ):

                user_alerts = alerts[
                    user_id
                ]

                remaining = []

                for item in user_alerts:

                    current_price = (
                        get_price(
                            item["symbol"]
                        )
                    )

                    if current_price is None:

                        remaining.append(
                            item
                        )

                        continue

                    if (
                        current_price >=
                        item["target"]
                    ):

                        try:

                            user = await bot.fetch_user(
                                int(user_id)
                            )

                            await user.send(

                                f"🚨 **התראה!**\n"
                                f"📊 "
                                f"{item['symbol']}\n"
                                f"💰 המחיר הגיע ל־"
                                f"${current_price:,.2f}\n"
                                f"🎯 יעד: "
                                f"${item['target']:,.2f}"

                            )

                            changed = True

                        except Exception as error:

                            print(
                                f"Alert Error: {error}"
                            )

                            remaining.append(
                                item
                            )

                    else:

                        remaining.append(
                            item
                        )

                alerts[user_id] = remaining

            if changed:

                save_alerts(
                    alerts
                )

            await asyncio.sleep(
                300
            )


    if not hasattr(
        bot,
        "alerts_task_started"
    ):

        bot.alerts_task_started = True

        bot.loop.create_task(
            check_alerts()
        )
