import discord
from discord.ext import commands
import yfinance as yf
import os

# =========================
# הגדרות הבוט
# =========================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# =========================
# כשהבוט מתחבר
# =========================

@bot.event
async def on_ready():
    print(f"✅ הבוט מחובר בתור {bot.user}")
    print("📊 Stock Bot is online!")
    print("🚀 Ready for 100+ features!")

# =========================
# פקודת עזרה
# =========================

@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="📊 Stock Bot",
        description="בוט מניות עם 100+ פיצ'רים",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📈 מניות",
        value="`!stock AAPL` - מידע על מניה\n"
              "`!price AAPL` - מחיר מניה",
        inline=False
    )

    embed.add_field(
        name="💰 בקרוב",
        value="תיקים וירטואליים, קנייה, מכירה, גרפים, ניתוח טכני ועוד!",
        inline=False
    )

    await ctx.send(embed=embed)

# =========================
# מידע על מניה
# =========================

@bot.command()
async def stock(ctx, symbol: str):
    symbol = symbol.upper()

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose")
        market_cap = info.get("marketCap")
        company_name = info.get("longName", symbol)

        if price is None:
            await ctx.send("❌ לא מצאתי את המניה הזאת.")
            return

        change = None
        change_percent = None

        if previous_close:
            change = price - previous_close
            change_percent = (change / previous_close) * 100

        embed = discord.Embed(
            title=f"📊 {company_name}",
            description=f"סימול: `{symbol}`",
            color=discord.Color.green() if change and change >= 0 else discord.Color.red()
        )

        embed.add_field(
            name="💰 מחיר",
            value=f"${price:,.2f}",
            inline=True
        )

        if change is not None:
            embed.add_field(
                name="📈 שינוי",
                value=f"${change:+,.2f} ({change_percent:+.2f}%)",
                inline=True
            )

        if market_cap:
            embed.add_field(
                name="🏢 שווי שוק",
                value=f"${market_cap:,.0f}",
                inline=True
            )

        embed.set_footer(text="Stock Bot 📊")

        await ctx.send(embed=embed)

    except Exception as error:
        print(error)
        await ctx.send(
            "❌ לא הצלחתי למצוא את המניה.\n"
            "נסה לדוגמה: `!stock AAPL`"
        )

# =========================
# פקודת מחיר מהירה
# =========================

@bot.command()
async def price(ctx, symbol: str):
    symbol = symbol.upper()

    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")

        if data.empty:
            await ctx.send("❌ לא מצאתי את המניה.")
            return

        price = data["Close"].iloc[-1]

        await ctx.send(
            f"💰 המחיר הנוכחי של **{symbol}** הוא:\n"
            f"## ${price:,.2f}"
        )

    except:
        await ctx.send("❌ אירעה שגיאה.")

# =========================
# הפעלת הבוט
# =========================

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    print("❌ לא נמצא DISCORD_TOKEN")
else:
    bot.run(TOKEN)
