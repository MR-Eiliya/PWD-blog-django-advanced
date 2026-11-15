
import requests

from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin

from django.core.cache import cache


NEWS_CACHE_KEY = "technology_news"
NEWS_CACHE_TIMEOUT = 20 * 60

HACKER_NEWS_API = "https://hacker-news.firebaseio.com/v0"


class ArticleImageParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.image_url = None

    def handle_starttag(self, tag, attrs):
        if tag != "meta" or self.image_url:
            return

        attrs = dict(attrs)
        property_name = attrs.get("property", "").lower()
        name = attrs.get("name", "").lower()

        if property_name == "og:image" or name == "twitter:image":
            self.image_url = attrs.get("content")


def get_article_image(url):
    if not url:
        return None

    try:
        response = requests.get(
            url,
            timeout=5,
            headers={
                "User-Agent": "Mozilla/5.0"
            },
        )
        response.raise_for_status()

        parser = ArticleImageParser()
        parser.feed(response.text)

        if parser.image_url:
            return urljoin(response.url, parser.image_url)

    except requests.RequestException:
        pass

    return None


def get_technology_news():
    cached_news = cache.get(NEWS_CACHE_KEY)

    if cached_news is not None:
        return cached_news

    try:
        response = requests.get(
            f"{HACKER_NEWS_API}/topstories.json",
            timeout=10,
        )
        response.raise_for_status()

        story_ids = response.json()[:6]
        news = []

        for story_id in story_ids:
            story_response = requests.get(
                f"{HACKER_NEWS_API}/item/{story_id}.json",
                timeout=10,
            )
            story_response.raise_for_status()

            story = story_response.json()

            if story and story.get("type") == "story":
                article_url = story.get("url")
                timestamp = story.get("time")

                news.append({
                    "id": story.get("id"),
                    "title": story.get("title"),
                    "url": article_url,
                    "image": get_article_image(article_url),
                    "score": story.get("score"),
                    "by": story.get("by"),
                    "time": timestamp,
                    "published_at": (
                        datetime.fromtimestamp(timestamp, tz=timezone.utc)
                        if timestamp else None
                    ),
                })

        cache.set(
            NEWS_CACHE_KEY,
            news,
            NEWS_CACHE_TIMEOUT,
        )

        return news

    except requests.RequestException:
        return []
