import discord
import json
import os
import yfinance as yf
from datetime import datetime


DATA_FILE = "portfolios.json"
STARTING_CASH = 100_000


def load_data():

    if not os.path.exists(DATA_FILE):

        return {}

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except:

        return {}


def save_data(data):

    with open(
        DATA_FILE,
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

    data = load_data()

    user_id = str(user_id)

    if user_id not in data:

        data[user_id] = {

            "cash": STARTING_CASH,

            "stocks": {},

            "transactions": [],

            "created_at":
                datetime.now().isoformat()

        }

        save_data(data)

    return data[user_id]


def get_user(user_id):

    data = load_data()

    user_id = str(user_id)

    if user_id not in data:

        create_user(user_id)

        data = load_data()

    return data[user_id]


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


def portfolio_value(user_id):

    user = get_user(user_id)

    total = user["cash"]

    for symbol, stock in user[
        "stocks"
    ].items():

        price = get_price(symbol)

        if price:

            total += (
                price *
                stock["amount"]
            )

    return total


def stock_value(user_id):

    user = get_user(user_id)

    total = 0

    for symbol, stock in user[
        "stocks"
    ].items():

        price = get_price(symbol)

        if price:

            total += (
                price *
                stock["amount"]
            )

    return total


def buy_stock(
    user_id,
    symbol,
    amount,
    price
):

    data = load_data()

    user_id = str(user_id)

    user = get_user(user_id)

    total_cost = (
        amount *
        price
    )

    if user["cash"] < total_cost:

        return False, (
            "❌ אין לך מספיק כסף."
        )

    user["cash"] -= total_cost

    if symbol not in user["stocks"]:

        user["stocks"][symbol] = {

            "amount": 0,

            "average_price": 0

        }

    stock = user[
        "stocks"
    ][symbol]

    old_amount = stock[
        "amount"
    ]

    old_average = stock[
        "average_price"
    ]

    new_amount = (
        old_amount +
        amount
    )

    new_average = (

        (
            old_amount *
            old_average
        )
        +
        (
            amount *
            price
        )

    ) / new_amount

    stock["amount"] = new_amount

    stock[
        "average_price"
    ] = new_average

    user[
        "transactions"
    ].append({

        "action": "BUY",

        "symbol": symbol,

        "amount": amount,

        "price": price,

        "total": total_cost,

        "date":
            datetime.now().isoformat()

    })

    save_data(data)

    return True, (
        f"✅ קנית {amount} "
        f"מניות של {symbol}"
    )


def sell_stock(
    user_id,
    symbol,
    amount,
    price
):

    data = load_data()

    user_id = str(user_id)

    user = get_user(user_id)

    if symbol not in user[
        "stocks"
    ]:

        return False, (
            "❌ אין לך את המניה."
        )

    stock = user[
        "stocks"
    ][symbol]

    if stock[
        "amount"
    ] < amount:

        return False, (
            "❌ אין לך מספיק מניות."
        )

    total_income = (
        amount *
        price
    )

    average_price = stock[
        "average_price"
    ]

    profit = (

        price -
        average_price

    ) * amount

    user["cash"] += total_income

    stock[
        "amount"
    ] -= amount

    if stock[
        "amount"
    ] == 0:

        del user[
            "stocks"
        ][symbol]

    user[
        "transactions"
    ].append({

        "action": "SELL",

        "symbol": symbol,

        "amount": amount,

        "price": price,

        "total": total_income,

        "profit": profit,

        "date":
            datetime.now().isoformat()

    })

    save_data(data)

    return True, (

        f"✅ מכרת {amount} "
        f"מניות של {symbol}\n"
        f"💰 רווח/הפסד: "
        f"${profit:+,.2f}"

    )


def setup(bot):


    @bot.command()
    async def portfolio(ctx):

        user = get_user(
            ctx.author.id
        )

        total_value = (
            portfolio_value(
                ctx.author.id
            )
        )

        stocks_total = (
            stock_value(
                ctx.author.id
            )
        )

        embed = discord.Embed(

            title=(
                f"💼 התיק של "
                f"{ctx.author.display_name}"
            ),

            color=discord.Color.gold()

        )

        embed.add_field(

            name="💵 מזומן",

            value=(
                f"${user['cash']:,.2f}"
            ),

            inline=True

        )

        embed.add_field(

            name="📈 שווי מניות",

            value=(
                f"${stocks_total:,.2f}"
            ),

            inline=True

        )

        embed.add_field(

            name="💰 שווי תיק כולל",

            value=(
                f"${total_value:,.2f}"
            ),

            inline=True

        )

        stocks_text = ""

        for symbol, stock in user[
            "stocks"
        ].items():

            price = get_price(
                symbol
            )

            amount = stock[
                "amount"
            ]

            average = stock[
                "average_price"
            ]

            if price:

                current_value = (
                    price *
                    amount
                )

                profit = (

                    price -
                    average

                ) * amount

                stocks_text += (

                    f"**{symbol}**\n"
                    f"📦 כמות: {amount}\n"
                    f"💰 מחיר ממוצע: "
                    f"${average:,.2f}\n"
                    f"📊 מחיר נוכחי: "
                    f"${price:,.2f}\n"
                    f"📈 רווח/הפסד: "
                    f"${profit:+,.2f}\n\n"

                )

        if stocks_text:

            embed.add_field(

                name="📊 האחזקות שלך",

                value=stocks_text[
                    :1024
                ],

                inline=False

            )

        else:

            embed.add_field(

                name="📊 האחזקות שלך",

                value=(
                    "אין לך מניות כרגע."
                ),

                inline=False

            )

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def balance(ctx):

        user = get_user(
            ctx.author.id
        )

        await ctx.send(

            f"💵 היתרה שלך:\n"
            f"## ${user['cash']:,.2f}"

        )


    @bot.command()
    async def buy(
        ctx,
        symbol: str,
        amount: int
    ):

        if amount <= 0:

            await ctx.send(
                "❌ הכמות חייבת להיות חיובית."
            )

            return

        symbol = symbol.upper()

        price = get_price(
            symbol
        )

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

        if success:

            await ctx.send(

                f"{message}\n"
                f"💰 מחיר: "
                f"${price:,.2f}\n"
                f"💵 סך הכול: "
                f"${price * amount:,.2f}"

            )

        else:

            await ctx.send(
                message
            )


    @bot.command()
    async def sell(
        ctx,
        symbol: str,
        amount: int
    ):

        if amount <= 0:

            await ctx.send(
                "❌ הכמות חייבת להיות חיובית."
            )

            return

        symbol = symbol.upper()

        price = get_price(
            symbol
        )

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

        await ctx.send(
            message
        )


    @bot.command()
    async def transactions(ctx):

        user = get_user(
            ctx.author.id
        )

        transactions = user[
            "transactions"
        ]

        if not transactions:

            await ctx.send(
                "🧾 אין עסקאות."
            )

            return

        embed = discord.Embed(

            title="🧾 היסטוריית עסקאות",

            color=discord.Color.blue()

        )

        text = ""

        for transaction in transactions[
            -10:
        ]:

            action = transaction[
                "action"
            ]

            emoji = (
                "🟢"
                if action == "BUY"
                else "🔴"
            )

            text += (

                f"{emoji} "
                f"{action} "
                f"{transaction['amount']}x "
                f"{transaction['symbol']}\n"
                f"💰 "
                f"${transaction['price']:,.2f}\n\n"

            )

        embed.description = text

        await ctx.send(
            embed=embed
        )


    @bot.command()
    async def resetportfolio(ctx):

        data = load_data()

        data[
            str(ctx.author.id)
        ] = {

            "cash": STARTING_CASH,

            "stocks": {},

            "transactions": [],

            "created_at":
                datetime.now().isoformat()

        }

        save_data(data)

        await ctx.send(

            "🔄 התיק אופס!\n"
            "💰 קיבלת מחדש "
            f"${STARTING_CASH:,.2f}"

        )
