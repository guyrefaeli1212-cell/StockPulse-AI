import os
import discord

from discord.ext import commands


# =========================
# הגדרות הבוט
# =========================

intents = discord.Intents.default()

intents.message_content = True

bot = commands.Bot(

    command_prefix="!",

    intents=intents

)


# =========================
# טעינת כל הפיצ'רים
# =========================

FEATURES = [

    "news",
    "stocks",
    "portfolio",
    "technical",
    "charts",
    "alerts",
    "watchlist",
    "economy",
    "admin",
    "commands",
    "automation"

]


for feature in FEATURES:

    try:

        module = __import__(
            f"features.{feature}",
            fromlist=["setup"]
        )

        module.setup(bot)

        print(
            f"✅ Loaded: {feature}"
        )

    except Exception as error:

        print(
            f"❌ Failed: {feature}"
        )

        print(error)


# =========================
# כשהבוט מוכן
# =========================

@bot.event
async def on_ready():

    print(
        f"🤖 Logged in as "
        f"{bot.user}"
    )

    print(
        f"🏠 Servers: "
        f"{len(bot.guilds)}"
    )

    print(
        "🚀 Stock Bot is online!"
    )


# =========================
# הפעלת הבוט
# =========================

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

if not TOKEN:

    print(
        "❌ DISCORD_TOKEN לא נמצא!"
    )

else:

    bot.run(
        TOKEN
    )
