import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.utils.news_storage import NewsStorage
from src.scrapers.base_scraper import BaseScraper

class BraveWordsScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://bravewords.com/feed", "Brave Words")
        self.storage = NewsStorage()  # Inicializando o storage internamente

    def fetch_articles(self, limit=5):
        response = requests.get(self.base_url, headers=self.headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")[:limit]

        news_list = []
        for item in items:
            title = item.find("title").text
            link = item.find("link").text
            date = datetime.strptime(item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z").isoformat()
            content = item.find("description").text if item.find("description") else ""
            image_url = ""
            video_urls = []

            if not self.storage.news_exists(title):
                self.storage.add_news(title, link, date, content, image_url, video_urls)

            news_list.append({
                "title": title,
                "link": link,
                "date": date,
                "content": content,
                "image_url": image_url,
                "video_urls": video_urls,
                "source": self.source
            })

        return news_list
