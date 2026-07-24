import yfinance as yf
from datetime import datetime


# =====================================
# קבלת חדשות למניה
# =====================================

def get_stock_news(symbol, limit=10):

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

            summary = content.get(
                "summary",
                "אין תקציר"
            )

            provider = content.get(
                "provider", {}
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
                "summary": summary,
                "publisher": publisher,
                "url": url
            })

        return results

    except Exception as error:

        print(
            f"News Error: {error}"
        )

        return []


# =====================================
# סינון חדשות
# =====================================

def search_news(
    symbol,
    keyword=None,
    limit=10
):

    news = get_stock_news(
        symbol,
        limit=20
    )

    if keyword is None:

        return news[:limit]

    keyword = keyword.lower()

    filtered_news = []

    for article in news:

        title = article["title"].lower()

        summary = article["summary"].lower()

        if (
            keyword in title
            or keyword in summary
        ):

            filtered_news.append(
                article
            )

    return filtered_news[:limit]


# =====================================
# פורמט חדשות לדיסקורד
# =====================================

def format_news(
    symbol,
    limit=5
):

    news = get_stock_news(
        symbol,
        limit
    )

    if not news:

        return (
            f"❌ לא נמצאו חדשות "
            f"עבור {symbol.upper()}"
        )

    text = (
        f"📰 **חדשות אחרונות "
        f"עבור {symbol.upper()}**\n\n"
    )

    for index, article in enumerate(
        news,
        start=1
    ):

        title = article["title"]

        publisher = article[
            "publisher"
        ]

        url = article["url"]

        text += (
            f"**{index}. {title}**\n"
            f"📰 מקור: {publisher}\n"
        )

        if url:

            text += (
                f"🔗 {url}\n"
            )

        text += "\n"

    return text
