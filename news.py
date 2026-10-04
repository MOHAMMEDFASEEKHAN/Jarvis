import os
import requests
from dotenv import load_dotenv

load_dotenv()

newsapi = os.getenv("NEWS_API_KEY")


def get_news():
    r = requests.get(
        f"https://newsapi.org/v2/top-headlines?country=us&category=general&apiKey={newsapi}"
    )

    if r.status_code == 200:
        data = r.json()
        articles = data.get("articles", [])

        return [article["title"] for article in articles[:5]]

    return []