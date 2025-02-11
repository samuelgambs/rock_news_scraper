import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from src.utils.news_storage import NewsStorage
from src.scrapers.base_scraper import BaseScraper

class MetalSucksScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://feeds.feedburner.com/Metalsucks/", "Metal Sucks")
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


# import requests
# from src.scrapers.base_scraper import BaseScraper
# from src.utils.news_storage import NewsStorage
# import feedparser
# from bs4 import BeautifulSoup

# class MetalSucksScraper(BaseScraper):
#     """
#     Scraper para coletar notícias do site MetalSucks via RSS.
#     """
    
#     def __init__(self):
#         super().__init__("https://feeds.feedburner.com/Metalsucks/", "MetalSucks")
    
#     def fetch_article_content(self, url):
#         response = requests.get(url, headers=self.headers)
#         if response.status_code != 200:
#             return "", "", []

#         soup = BeautifulSoup(response.content, "html.parser")
#         article_body = soup.find("div", class_="post-body")
#         if not article_body:
#             return "", "", []

#         paragraphs = article_body.find_all("p")
#         content = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())

#         image = soup.find("meta", property="og:image")
#         image_url = image["content"] if image else ""

#         videos = soup.find_all("iframe")
#         video_urls = [vid["src"] for vid in videos if "youtube" in vid["src"]]

#         return content, image_url, video_urls    
#         # def __init__(self):
#     #     super().__init__("https://www.metalsucks.net")
#     #     self.source = "Metal Hammer"
#     #     self.storage = NewsStorage()



#     # def fetch_articles(self, limit=10):
#     #     """Busca as últimas notícias do feed RSS."""
#     #     feed_url = "https://feeds.feedburner.com/Metalsucks"
#     #     news_list = []
        
#     #     feed = feedparser.parse(feed_url)
#     #     if not feed.entries:
#     #         print("❌ Nenhuma entrada encontrada no feed RSS.")
#     #         return []

#     #     for entry in feed.entries[:limit]:
#     #         title = entry.title
#     #         link = entry.link
#     #         date = entry.published if hasattr(entry, "published") else "Data não disponível"
            
#     #         news_list.append({
#     #             "title": title,
#     #             "link": link,
#     #             "date": date
#     #         })

#     #     return news_list

#     # def fetch_article_content(self, url):
#     #     """Extrai o conteúdo completo de uma notícia do site."""
#     #     html = self.get_html(url)
#     #     if not html:
#     #         return "No content available"

#     #     soup = self.parse_html(html)
#     #     content_div = soup.find('div', class_='post-body')  # Ajuste a classe conforme necessário
        
#     #     if content_div:
#     #         paragraphs = content_div.find_all(['p', 'h2', 'h3', 'blockquote'])
#     #         formatted_content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
#     #         return formatted_content
        
#     #     return "No content available"
