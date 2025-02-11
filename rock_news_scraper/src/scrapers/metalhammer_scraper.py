import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from src.utils.news_storage import NewsStorage
from src.scrapers.base_scraper import BaseScraper

class MetalHammerScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://www.metal-hammer.de/feed/", "Metal Hammer")
        self.storage = NewsStorage()  # Inicializa o sistema de armazenamento

    def fetch_articles(self, limit=5):
        response = requests.get(self.base_url, headers=self.headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")[:limit]

        news_list = []
        for item in items:
            title = item.find("title").text
            link = item.find("link").text
            date_raw = item.find("pubDate").text if item.find("pubDate") else ""

            # 📌 Conversão automática da data
            try:
                date = parser.parse(date_raw).isoformat()
            except ValueError:
                date = None  # Define como None caso falhe

            content = item.find("description").text if item.find("description") else ""
            image_url = ""
            video_urls = []

            # Extração de imagem do feed RSS
            media_thumbnail = item.find("media:thumbnail")
            if media_thumbnail and media_thumbnail.get("url"):
                image_url = media_thumbnail["url"]

            # Extração do conteúdo completo da notícia
            article_response = requests.get(link, headers=self.headers)
            article_soup = BeautifulSoup(article_response.content, "html.parser")

            # Procura vídeos dentro da matéria
            video_tags = article_soup.find_all("iframe")
            video_urls = [tag["src"] for tag in video_tags if "src" in tag.attrs]

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
