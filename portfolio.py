import json
import os
from datetime import datetime

# =====================================
# הגדרות
# =====================================

DATA_FILE = "portfolios.json"
STARTING_BALANCE = 100_000


# =====================================
# טעינת נתונים
# =====================================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


# =====================================
# שמירת נתונים
# =====================================

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# =====================================
# יצירת משתמש
# =====================================

def create_user(user_id):
    data = load_data()

    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "cash": STARTING_BALANCE,
            "stocks": {},
            "transactions": [],
            "created_at": datetime.now().isoformat()
        }

        save_data(data)

    return data[user_id]


# =====================================
# קבלת תיק משתמש
# =====================================

def get_user(user_id):
    data = load_data()
    user_id = str(user_id)

    if user_id not in data:
        return None

    return data[user_id]


# =====================================
# הוספת עסקה
# =====================================

def add_transaction(
    user_id,
    action,
    symbol,
    amount,
    price
):
    data = load_data()
    user_id = str(user_id)

    create_user(user_id)

    data = load_data()

    transaction = {
        "action": action,
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "total": amount * price,
        "date": datetime.now().isoformat()
    }

    data[user_id]["transactions"].append(transaction)

    save_data(data)


# =====================================
# קניית מניה
# =====================================

def buy_stock(user_id, symbol, amount, price):
    data = load_data()
    user_id = str(user_id)

    create_user(user_id)

    data = load_data()

    total_cost = amount * price

    if data[user_id]["cash"] < total_cost:
        return False, "❌ אין לך מספיק כסף."

    data[user_id]["cash"] -= total_cost

    if symbol not in data[user_id]["stocks"]:
        data[user_id]["stocks"][symbol] = {
            "amount": 0,
            "average_price": 0
        }

    old_amount = data[user_id]["stocks"][symbol]["amount"]
    old_average_price = data[user_id]["stocks"][symbol]["average_price"]

    new_amount = old_amount + amount

    if new_amount > 0:
        new_average_price = (
            (old_amount * old_average_price) +
            (amount * price)
        ) / new_amount
    else:
        new_average_price = price

    data[user_id]["stocks"][symbol]["amount"] = new_amount
    data[user_id]["stocks"][symbol]["average_price"] = new_average_price

    data[user_id]["transactions"].append({
        "action": "BUY",
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "total": total_cost,
        "date": datetime.now().isoformat()
    })

    save_data(data)

    return True, f"✅ קנית {amount} מניות של {symbol}"


# =====================================
# מכירת מניה
# =====================================

def sell_stock(user_id, symbol, amount, price):
    data = load_data()
    user_id = str(user_id)

    create_user(user_id)

    data = load_data()

    if symbol not in data[user_id]["stocks"]:
        return False, "❌ אין לך את המניה הזאת."

    current_amount = data[user_id]["stocks"][symbol]["amount"]

    if current_amount < amount:
        return False, "❌ אין לך מספיק מניות למכור."

    total_income = amount * price

    data[user_id]["cash"] += total_income

    data[user_id]["stocks"][symbol]["amount"] -= amount

    if data[user_id]["stocks"][symbol]["amount"] == 0:
        del data[user_id]["stocks"][symbol]

    data[user_id]["transactions"].append({
        "action": "SELL",
        "symbol": symbol,
        "amount": amount,
        "price": price,
        "total": total_income,
        "date": datetime.now().isoformat()
    })

    save_data(data)

    return True, f"✅ מכרת {amount} מניות של {symbol}"


# =====================================
# איפוס תיק
# =====================================

def reset_portfolio(user_id):
    data = load_data()
    user_id = str(user_id)

    data[user_id] = {
        "cash": STARTING_BALANCE,
        "stocks": {},
        "transactions": [],
        "created_at": datetime.now().isoformat()
    }

    save_data(data)


# =====================================
# היסטוריית עסקאות
# =====================================

def get_transactions(user_id):
    user = get_user(user_id)

    if not user:
        return []

    return user["transactions"]


# =====================================
# חישוב כסף שהושקע
# =====================================

def get_invested_money(user_id):
    user = get_user(user_id)

    if not user:
        return 0

    total = 0

    for stock in user["stocks"].values():
        total += (
            stock["amount"] *
            stock["average_price"]
        )

    return total
