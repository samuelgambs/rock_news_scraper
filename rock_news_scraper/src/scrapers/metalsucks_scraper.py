import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from src.utils.news_storage import NewsStorage
from src.scrapers.base_scraper import BaseScraper

class MetalSucksScraper(BaseScraper):
    def __init__(self, storage):
        super().__init__(
            base_url="https://feeds.feedburner.com/Metalsucks",
            article_selector="item",
            title_selector="title",
            link_selector="link",
            date_selector="pubDate",
            content_selector="div.post-body",
            image_selector="meta[property='og:image']",
            video_selector="iframe",
            storage=storage
        )

    def fetch_articles(self, limit=1):
        """Coleta e armazena artigos """
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
        
        print(f"✅ Notícias coletadas com sucesso de Metal Sucks!")

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
