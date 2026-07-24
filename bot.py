import discord
from discord.ext import commands
import yfinance as yf
import os

from portfolio import (
    create_user,
    get_user,
    buy_stock,
    sell_stock,
    reset_portfolio,
    get_transactions
from analysis import full_analysis
)

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
    print(f"✅ מחובר בתור {bot.user}")
    print("📊 Stock Bot Online!")
    print("🚀 Portfolio System Loaded!")

# =====================================
# פונקציית קבלת מחיר
# =====================================

def get_stock_price(symbol):
    symbol = symbol.upper()

    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        return None

    return float(data["Close"].iloc[-1])

# =====================================
# HELP
# =====================================

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📊 Stock Bot",
        description="בוט מניות וירטואלי עם מערכת השקעות",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="📈 מניות",
        value=(
            "`!stock AAPL` - מידע על מניה\n"
            "`!price AAPL` - מחיר מניה"
        ),
        inline=False
    )

    embed.add_field(
        name="💰 תיק השקעות",
        value=(
            "`!portfolio` - הצגת התיק\n"
            "`!balance` - יתרת כסף\n"
            "`!buy AAPL 10` - קניית מניות\n"
            "`!sell AAPL 10` - מכירת מניות"
        ),
        inline=False
    )

    embed.add_field(
        name="🧾 היסטוריה",
        value=(
            "`!transactions` - היסטוריית עסקאות\n"
            "`!resetportfolio` - איפוס תיק"
        ),
        inline=False
    )

    await ctx.send(embed=embed)

# =====================================
# מידע על מניה
# =====================================

@bot.command()
async def stock(ctx, symbol: str):

    symbol = symbol.upper()

    try:

        ticker = yf.Ticker(symbol)
        info = ticker.info

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )

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

            change_percent = (
                change / previous_close
            ) * 100

        embed = discord.Embed(
            title=f"📊 {company_name}",
            description=f"סימול: `{symbol}`",
            color=(
                discord.Color.green()
                if change and change >= 0
                else discord.Color.red()
            )
        )

        embed.add_field(
            name="💰 מחיר",
            value=f"${price:,.2f}",
            inline=True
        )

        if change is not None:

            embed.add_field(
                name="📈 שינוי",
                value=(
                    f"${change:+,.2f} "
                    f"({change_percent:+.2f}%)"
                ),
                inline=True
            )

        if market_cap:

            embed.add_field(
                name="🏢 שווי שוק",
                value=f"${market_cap:,.0f}",
                inline=True
            )

        await ctx.send(embed=embed)

    except Exception as error:

        print(error)

        await ctx.send(
            "❌ שגיאה. נסה לדוגמה:\n"
            "`!stock AAPL`"
        )

# =====================================
# מחיר מהיר
# =====================================

@bot.command()
async def price(ctx, symbol: str):

    symbol = symbol.upper()

    try:

        price = get_stock_price(symbol)

        if price is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        await ctx.send(
            f"💰 מחיר **{symbol}**:\n"
            f"## ${price:,.2f}"
        )

    except:

        await ctx.send(
            "❌ לא הצלחתי לקבל את המחיר."
        )

# =====================================
# הצגת תיק
# =====================================

@bot.command()
async def portfolio(ctx):

    user_id = ctx.author.id

    create_user(user_id)

    user = get_user(user_id)

    embed = discord.Embed(
        title=f"💼 התיק של {ctx.author.display_name}",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="💵 מזומן",
        value=f"${user['cash']:,.2f}",
        inline=False
    )

    if not user["stocks"]:

        embed.add_field(
            name="📦 מניות",
            value="אין לך כרגע מניות.",
            inline=False
        )

    else:

        stocks_text = ""

        for symbol, stock in user["stocks"].items():

            amount = stock["amount"]
            average_price = stock["average_price"]

            stocks_text += (
                f"**{symbol}**\n"
                f"📦 כמות: `{amount}`\n"
                f"💰 מחיר ממוצע: "
                f"${average_price:,.2f}\n\n"
            )

        embed.add_field(
            name="📈 המניות שלך",
            value=stocks_text,
            inline=False
        )

    await ctx.send(embed=embed)

# =====================================
# יתרה
# =====================================

@bot.command()
async def balance(ctx):

    user_id = ctx.author.id

    create_user(user_id)

    user = get_user(user_id)

    await ctx.send(
        f"💵 **היתרה שלך:**\n"
        f"## ${user['cash']:,.2f}"
    )

# =====================================
# קניית מניות
# =====================================

@bot.command()
async def buy(ctx, symbol: str, amount: int):

    symbol = symbol.upper()

    if amount <= 0:

        await ctx.send(
            "❌ הכמות חייבת להיות גדולה מ־0."
        )

        return

    try:

        price = get_stock_price(symbol)

        if price is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        success, message = buy_stock(
            ctx.author.id,
            symbol,
            amount,
            price
        )

        total = price * amount

        if success:

            await ctx.send(
                f"{message}\n\n"
                f"💰 מחיר למניה: "
                f"${price:,.2f}\n"
                f"💵 סך הכול: "
                f"${total:,.2f}"
            )

        else:

            await ctx.send(message)

    except Exception as error:

        print(error)

        await ctx.send(
            "❌ שגיאה בקנייה."
        )

# =====================================
# מכירת מניות
# =====================================

@bot.command()
async def sell(ctx, symbol: str, amount: int):

    symbol = symbol.upper()

    if amount <= 0:

        await ctx.send(
            "❌ הכמות חייבת להיות גדולה מ־0."
        )

        return

    try:

        price = get_stock_price(symbol)

        if price is None:

            await ctx.send(
                "❌ לא מצאתי את המניה."
            )

            return

        success, message = sell_stock(
            ctx.author.id,
            symbol,
            amount,
            price
        )

        total = price * amount

        if success:

            await ctx.send(
                f"{message}\n\n"
                f"💰 מחיר למניה: "
                f"${price:,.2f}\n"
                f"💵 קיבלת: "
                f"${total:,.2f}"
            )

        else:

            await ctx.send(message)

    except Exception as error:

        print(error)

        await ctx.send(
            "❌ שגיאה במכירה."
        )

# =====================================
# היסטוריית עסקאות
# =====================================

@bot.command()
async def transactions(ctx):

    transactions = get_transactions(
        ctx.author.id
    )

    if not transactions:

        await ctx.send(
            "🧾 אין עדיין עסקאות."
        )

        return

    text = ""

    for transaction in transactions[-10:]:

        action = transaction["action"]
        symbol = transaction["symbol"]
        amount = transaction["amount"]
        price = transaction["price"]

        emoji = (
            "🟢"
            if action == "BUY"
            else "🔴"
        )

        text += (
            f"{emoji} **{action}** "
            f"{amount}x {symbol}\n"
            f"💰 ${price:,.2f}\n\n"
        )

    embed = discord.Embed(
        title="🧾 10 העסקאות האחרונות",
        description=text,
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

# =====================================
# איפוס תיק
# =====================================

@bot.command()
async def resetportfolio(ctx):

    reset_portfolio(
        ctx.author.id
    )

    await ctx.send(
        "🔄 התיק שלך אופס!\n"
        "💰 קיבלת מחדש $100,000."
    )
# כאן נגמרות הפקודות הקודמות


# =====================================
# ניתוח טכני מלא
# =====================================

@bot.command()
async def analyze(ctx, symbol: str):

    # כל הקוד הארוך של analyze כאן


# =====================================
# הפעלת הבוט
# =====================================

TOKEN = os.getenv("DISCORD_TOKEN")
# =====================================
# הפעלת הבוט
# =====================================

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:

    print(
        "❌ לא נמצא DISCORD_TOKEN"
    )

else:

    bot.run(TOKEN)
