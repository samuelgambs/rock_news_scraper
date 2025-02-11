import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.utils.news_storage import NewsStorage
from src.scrapers.base_scraper import BaseScraper

class MetalInjectionScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://metalinjection.net/feed", "Metal Injection")
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

            # Extração de imagem
            media_content = item.find("media:content")
            if media_content and media_content.get("url"):
                image_url = media_content["url"]

            # Extração de vídeos do conteúdo principal
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

    # def __init__(self):
    #     super().__init__("https://metalinjection.net")
    #     self.source = "Metal Injection"
    #     self.storage = NewsStorage()

    # def fetch_articles(self, limit=10):
    #     """Busca as últimas notícias do feed RSS e armazena as novas."""
    #     feed_url = "https://metalinjection.net/feed"
    #     news_list = []
        
    #     feed = feedparser.parse(feed_url)
    #     if not feed.entries:
    #         print("❌ Nenhuma entrada encontrada no feed RSS.")
    #         return []

    #     for entry in feed.entries[:limit]:
    #         title = entry.title
    #         link = entry.link
    #         date = entry.published if hasattr(entry, "published") else "Data não disponível"
    #         image_url = self.fetch_article_image(link)
    #         video_urls = self.fetch_article_videos(link)
            
    #         if not self.storage.news_exists(title):
    #             content = self.fetch_article_content(link)
    #             self.storage.add_news(title, link, date, content, image_url, video_urls)
    #             news_list.append({
    #                 "title": title,
    #                 "link": link,
    #                 "date": date,
    #                 "image_url": image_url,
    #                 "video_urls": video_urls,
    #                 "content": content
    #             })
    #         else:
    #             print(f"⚠️ Notícia já armazenada: {title}")

    #     return news_list

    # def fetch_article_content(self, url):
    #     """Extrai o conteúdo completo de uma notícia do site e formata corretamente."""
    #     html = self.get_html(url)
    #     if not html:
    #         return "No content available"

    #     soup = self.parse_html(html)
    #     content_div = soup.find('div', class_='zox-post-body')  # Ajuste para Metal Injection
        
    #     if content_div:
    #         paragraphs = content_div.find_all(['p', 'h2', 'h3', 'blockquote'])
    #         formatted_content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
    #         return formatted_content
        
    #     return "No content available"
    
    # def fetch_article_image(self, url):
    #     """Extrai a URL da imagem principal da matéria."""
    #     html = self.get_html(url)
    #     if not html:
    #         return None
        
    #     soup = self.parse_html(html)
    #     image_div = soup.find('div', class_='zox-post-img-wrap')
    #     if image_div:
    #         img_tag = image_div.find('img')
    #         if img_tag and img_tag.get('src'):
    #             return img_tag['src']
        
    #     return None
    
    # def fetch_article_videos(self, url):
    #     """Extrai todas as URLs de vídeos incorporados na matéria."""
    #     html = self.get_html(url)
    #     if not html:
    #         return []
        
    #     soup = self.parse_html(html)
    #     video_iframes = soup.find_all('iframe')
    #     video_urls = [iframe.get('src') for iframe in video_iframes if iframe.get('src') and 'youtube.com' in iframe.get('src')]
        
    #     return video_urls
