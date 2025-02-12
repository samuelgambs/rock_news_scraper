import requests
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import BaseScraper

class BlabbermouthScraper(BaseScraper):
    def __init__(self, storage):
        super().__init__(
            base_url="https://www.blabbermouth.net/feed/",
            article_selector="item",
            title_selector="title",
            link_selector="link",
            date_selector="pubDate",
            content_selector="div.news-content",
            image_selector="meta[property='og:image']",
            video_selector="iframe",
            storage=storage
        )

    def fetch_articles(self, limit=1):
        """Coleta e armazena artigos de Blabbermouth."""
        response = requests.get(self.base_url, headers=self.headers)
        if response.status_code != 200:
            print(f"⚠️ Erro ao acessar {self.base_url}: {response.status_code}")
            return []

        soup = BeautifulSoup(response.content, "xml")
        articles = soup.find_all(self.article_selector)[:limit]
        
        for article in articles:
            title = article.find(self.title_selector).text.strip()
            link = article.find(self.link_selector).text.strip()
            date = self.format_date(article.find(self.date_selector).text.strip())
            content, image_url, video_urls = self.fetch_article_details(link)
            
            self.storage.add_news(title, link, date, content, image_url, video_urls)
        
        print(f"✅ Notícias coletadas com sucesso de Blabbermouth!")

    def fetch_article_details(self, url):
        """Extrai detalhes do artigo (conteúdo, imagem e vídeos)."""
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            print(f"⚠️ Erro ao acessar {url}: {response.status_code}")
            return "", "", []

        soup = BeautifulSoup(response.content, "html.parser")
        
        # Captura o conteúdo principal
        content_section = soup.select_one(self.content_selector)
        content = content_section.get_text(separator="\n").strip() if content_section else ""

        # Captura imagem
        image_tag = soup.select_one(self.image_selector)
        image_url = image_tag["content"] if image_tag else ""

        # Captura vídeos
        video_urls = self.fetch_article_videos(url)

        return content, image_url, video_urls

    def format_date(self, date_str):
        """Formata a data do artigo no formato ISO 8601."""
        from datetime import datetime
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").isoformat()
        except ValueError:
            return date_str

# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# from src.utils.news_storage import NewsStorage
# from src.scrapers.base_scraper import BaseScraper

# class BlabbermouthScraper(BaseScraper):
#     def __init__(self, storage):
#         super().__init__("https://www.blabbermouth.net/feed/", storage, article_content_class="news-content")
#         self.storage = storage

#     def fetch_article_details(self, url):
#         content, image_url = super().fetch_article_details(url)
#         return content, image_url

#     def fetch_article_videos(self, url):
#         return super().fetch_article_videos(url)


#     def fetch_articles(self, limit=5):
#         response = requests.get(self.base_url, headers=self.headers)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.content, "xml")
#         items = soup.find_all("item")[:limit]

#         news_list = []
#         for item in items:
#             title = item.find("title").text
#             link = item.find("link").text
#             date = datetime.strptime(item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z").isoformat()
#             details = self.fetch_article_details(link)
#             video_urls = self.fetch_article_videos(link)
#             news_list.append({
#                     "title": title,
#                     "link": link,
#                     "date": date,
#                     "image_url": details,
#                     "video_urls": video_urls,
#                     "content": details
#                 })

#         return news_list
