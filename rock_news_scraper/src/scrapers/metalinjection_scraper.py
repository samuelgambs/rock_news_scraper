import requests
from bs4 import BeautifulSoup
from datetime import datetime
from src.utils.news_storage import NewsStorage
from src.scrapers.base_scraper import BaseScraper

class MetalInjectionScraper(BaseScraper):
    def __init__(self, storage):
        super().__init__(
            base_url="https://metalinjection.net/feed/",
            article_selector="item",
            title_selector="title",
            link_selector="link",
            date_selector="pubDate",
            content_selector="div.zox-post-body",
            image_selector="meta[property='og:image']",
            video_selector="iframe",
            storage=storage
        )

    def fetch_articles(self, limit=2):
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
        video_urls = [iframe["src"] for iframe in soup.find_all(self.video_selector) if "src" in iframe.attrs]

        return content, image_url, video_urls

    def format_date(self, date_str):
        """Formata a data do artigo no formato ISO 8601."""
        from datetime import datetime
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").isoformat()
        except ValueError:
            return date_str



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
