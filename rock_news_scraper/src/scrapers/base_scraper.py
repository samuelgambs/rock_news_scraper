import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.utils.news_storage import NewsStorage
from dateutil import parser

class BaseScraper:
    def __init__(self, base_url, source):
        self.base_url = base_url
        self.source = source
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        self.storage = NewsStorage()

    def fetch_articles(self, limit=1):
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code != 200:
            print(f"❌ Erro ao acessar {self.source}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")[:limit]
        all_articles = []

        for item in items:
            title = item.find("title").text.strip()
            link = item.find("link").text.strip()
            date = item.find("pubDate").text.strip()
            try:
                date = parser.parse(date).isoformat()
            except ValueError as e:
                print(f"⚠️ Erro ao processar a data: {date}. Usando 'Unknown'.")
                date = "Unknown"
            content, image_url, video_urls = self.fetch_article_content(link)
            
            if not content:
                print(f"⚠️ Conteúdo vazio para {title}. Parando a execução.")
                exit(1)

            self.storage.add_news(title, link, date, content, image_url, video_urls)
            all_articles.append({
                "title": title,
                "link": link,
                "date": date,
                "content": content,
                "image_url": image_url,
                "video_urls": video_urls,
                "source": self.source
            })

        return all_articles

    def fetch_article_content(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return "", "", []

        soup = BeautifulSoup(response.content, "html.parser")
        article_body = soup.find("div", class_="news-content")
        if not article_body:
            return "", "", []

        paragraphs = article_body.find_all("p")
        content = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())

        image = soup.find("meta", property="og:image")
        image_url = image["content"] if image else ""

        videos = soup.find_all("iframe")
        video_urls = [vid["src"] for vid in videos if "youtube" in vid["src"]]

        return content, image_url, video_urls