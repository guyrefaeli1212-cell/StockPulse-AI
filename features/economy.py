import discord
import json
import os
from datetime import datetime, date


ECONOMY_FILE = "economy.json"

STARTING_BALANCE = 10_000
DAILY_REWARD = 1_000


def load_economy():

    if not os.path.exists(ECONOMY_FILE):
        return {}

    try:

        with open(
            ECONOMY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return {}


def save_economy(data):

    with open(
        ECONOMY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def create_user(user_id):

    data = load_economy()

    user_id = str(user_id)

    if user_id not in data:

        data[user_id] = {

            "balance": STARTING_BALANCE,

            "xp": 0,

            "level": 1,

            "daily_claimed": "",

            "achievements": [],

            "stats": {

                "commands": 0,

                "trades": 0,

                "profit": 0

            }

        }

        save_economy(data)

    return data[user_id]


def get_user(user_id):

    data = load_economy()

    user_id = str(user_id)

    if user_id not in data:

        create_user(user_id)

        data = load_economy()

    return data[user_id]


def add_xp(user_id, amount):

    data = load_economy()

    user_id = str(user_id)

    user = get_user(user_id)

    user["xp"] += amount

    required_xp = user["level"] * 1000

    level_up = False

    while user["xp"] >= required_xp:

        user["xp"] -= required_xp

        user["level"] += 1

        level_up = True

        required_xp = user["level"] * 1000

    save_data = data

    save_economy(save_data)

    return level_up, user["level"]


def setup(bot):


    @bot.command()
    async def economy(ctx):

        user = get_user(
            ctx.author.id
        )

        required_xp = (
            user["level"] * 1000
        )

        embed = discord.Embed(

            title=(
                f"🎮 כלכלה — "
                f"{ctx.author.display_name}"
            ),

            color=discord.Color.gold()

        )

        embed.add_field(

            name="💰 כסף",

            value=(
                f"₪{user['balance']:,.2f}"
            ),

            inline=True

        )

        embed.add_field(

            name="⭐ רמה",

            value=(
                f"{user['level']}"
            ),

            inline=True

        )

        embed.add_field(

            name="✨ XP",

            value=(

                f"{user['xp']:,} / "
                f"{required_xp:,}"

            ),

            inline=True

        )

        embed.add_field(

            name="📊 סטטיסטיקות",

            value=(

                f"פקודות: "
                f"{user['stats']['commands']}\n"
                f"עסקאות: "
                f"{user['stats']['trades']}\n"
                f"רווח: "
                f"₪{user['stats']['profit']:,.2f}"

            ),

            inline=False

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def daily(ctx):

        data = load_economy()

        user_id = str(
            ctx.author.id
        )

        user = get_user(
            user_id
        )

        today = str(
            date.today()
        )

        if user["daily_claimed"] == today:

            await ctx.send(

                "⏳ כבר לקחת את "
                "הפרס היומי שלך היום."

            )

            return

        user["balance"] += DAILY_REWARD

        user["daily_claimed"] = today

        level_up, level = add_xp(
            user_id,
            100
        )

        data = load_economy()

        save_economy(data)

        message = (

            f"🎁 קיבלת "
            f"₪{DAILY_REWARD:,.2f}!\n"
            f"✨ +100 XP"

        )

        if level_up:

            message += (

                f"\n🎉 עלית לרמה "
                f"**{level}**!"

            )

        await ctx.send(
            message
        )


    @bot.command()
    async def balance(ctx):

        user = get_user(
            ctx.author.id
        )

        await ctx.send(

            f"💰 היתרה שלך:\n"
            f"## ₪{user['balance']:,.2f}"

        )


    @bot.command()
    async def work(ctx):

        user = get_user(
            ctx.author.id
        )

        reward = 250

        user["balance"] += reward

        level_up, level = add_xp(
            ctx.author.id,
            50
        )

        data = load_economy()

        save_economy(data)

        message = (

            f"💼 עבדת וקיבלת "
            f"₪{reward:,.2f}!\n"
            f"✨ +50 XP"

        )

        if level_up:

            message += (

                f"\n🎉 עלית לרמה "
                f"**{level}**!"

            )

        await ctx.send(
            message
        )


    @bot.command()
    async def achievement(ctx):

        data = load_economy()

        user_id = str(
            ctx.author.id
        )

        user = get_user(
            user_id
        )

        achievements = []

        if user["level"] >= 5:

            achievements.append(
                "🏆 הגעת לרמה 5"
            )

        if user["stats"]["trades"] >= 10:

            achievements.append(
                "📈 ביצעת 10 עסקאות"
            )

        if user["stats"]["trades"] >= 50:

            achievements.append(
                "🔥 ביצעת 50 עסקאות"
            )

        if user["balance"] >= 100_000:

            achievements.append(
                "💰 הגעת ל־₪100,000"
            )

        if not achievements:

            await ctx.send(

                "🔒 עדיין אין לך הישגים.\n"
                "המשך להשתמש בבוט!"

            )

            return

        embed = discord.Embed(

            title="🏆 ההישגים שלך",

            description="\n".join(
                achievements
            ),

            color=discord.Color.gold()

        )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def addmoney(
        ctx,
        amount: float
    ):

        if not ctx.author.guild_permissions.administrator:

            await ctx.send(
                "❌ רק מנהל יכול להשתמש בפקודה."
            )

            return

        if amount <= 0:

            await ctx.send(
                "❌ הסכום חייב להיות חיובי."
            )

            return

        data = load_economy()

        user_id = str(
            ctx.author.id
        )

        user = get_user(
            user_id
        )

        user["balance"] += amount

        save_economy(data)

        await ctx.send(

            f"✅ נוספו "
            f"₪{amount:,.2f} "
            f"לחשבון שלך."

        )


    @bot.command()
    async def leaderboard(ctx):

        data = load_economy()

        if not data:

            await ctx.send(
                "📭 אין עדיין משתמשים."
            )

            return

        ranking = []

        for user_id, user in data.items():

            ranking.append(

                (
                    user_id,
                    user["balance"],
                    user["level"]
                )

            )

        ranking.sort(

            key=lambda x: x[1],

            reverse=True

        )

        text = ""

        for index, item in enumerate(

            ranking[:10],

            start=1

        ):

            user_id = item[0]

            try:

                user = await bot.fetch_user(
                    int(user_id)
                )

                name = user.display_name

            except:

                name = "משתמש"

            text += (

                f"**{index}. "
                f"{name}**\n"
                f"💰 "
                f"₪{item[1]:,.2f}\n"
                f"⭐ רמה "
                f"{item[2]}\n\n"

            )

        embed = discord.Embed(

            title="🏆 דירוג כלכלי",

            description=text,

            color=discord.Color.gold()

        )

        await ctx.send(
            embed=embed
        )
