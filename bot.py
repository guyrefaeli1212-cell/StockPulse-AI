import os
import importlib
import discord
from discord.ext import commands


# =====================================
# הגדרות הבוט
# =====================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# =====================================
# כשהבוט מתחבר
# =====================================

@bot.event
async def on_ready():

    print("=" * 40)
    print(f"✅ מחובר בתור: {bot.user}")
    print("📊 STOCK BOT ONLINE")
    print("🚀 FEATURES SYSTEM ACTIVE")
    print("=" * 40)


# =====================================
# טעינה אוטומטית של פיצ'רים
# =====================================

def load_features():

    features_folder = "features"

    if not os.path.exists(features_folder):

        print("❌ תיקיית features לא נמצאה")

        return

    for filename in os.listdir(features_folder):

        if not filename.endswith(".py"):

            continue

        if filename == "__init__.py":

            continue

        module_name = filename[:-3]

        try:

            module = importlib.import_module(
                f"features.{module_name}"
            )

            if hasattr(module, "setup"):

                module.setup(bot)

                print(
                    f"✅ נטען פיצ'ר: {module_name}"
                )

            else:

                print(
                    f"⚠️ דולג: {module_name} "
                    f"(אין setup)"
                )

        except Exception as error:

            print(
                f"❌ שגיאה בפיצ'ר "
                f"{module_name}:"
            )

            print(error)


# =====================================
# פקודת עזרה בסיסית
# =====================================

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📊 Stock Bot",
        description=(
            "בוט מניות עם מערכת פיצ'רים "
            "אוטומטית 🚀"
        ),
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📈 מניות",
        value=(
            "`!stock AAPL`\n"
            "`!price AAPL`\n"
            "`!analyze AAPL`\n"
            "`!chart AAPL`\n"
            "`!news AAPL`"
        ),
        inline=False
    )

    embed.add_field(
        name="💰 תיק השקעות",
        value=(
            "`!portfolio`\n"
            "`!balance`\n"
            "`!buy AAPL 10`\n"
            "`!sell AAPL 10`\n"
            "`!transactions`"
        ),
        inline=False
    )

    embed.add_field(
        name="🚀 מערכת",
        value=(
            "פיצ'רים חדשים נטענים "
            "אוטומטית מתיקיית `features`"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =====================================
# טעינת כל הפיצ'רים
# =====================================

load_features()


# =====================================
# הפעלת הבוט
# =====================================

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:

    print(
        "❌ DISCORD_TOKEN לא נמצא"
    )

else:

    bot.run(TOKEN)
