from src.scrapers.base_scraper import BaseScraper
from src.utils.news_storage import NewsStorage
import feedparser
from bs4 import BeautifulSoup

class MetalInjectionScraper(BaseScraper):
    """
    Scraper para coletar notícias do site Metal Injection via RSS.
    """
    def __init__(self):
        super().__init__("https://metalinjection.net")
        self.source = "Metal Injection"
        self.storage = NewsStorage()

    def fetch_articles(self, limit=10):
        """Busca as últimas notícias do feed RSS e armazena as novas."""
        feed_url = "https://metalinjection.net/feed"
        news_list = []
        
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            print("❌ Nenhuma entrada encontrada no feed RSS.")
            return []

        for entry in feed.entries[:limit]:
            title = entry.title
            link = entry.link
            date = entry.published if hasattr(entry, "published") else "Data não disponível"
            image_url = self.fetch_article_image(link)
            video_urls = self.fetch_article_videos(link)
            
            if not self.storage.news_exists(title):
                content = self.fetch_article_content(link)
                self.storage.add_news(title, link, date, content, image_url, video_urls)
                news_list.append({
                    "title": title,
                    "link": link,
                    "date": date,
                    "image_url": image_url,
                    "video_urls": video_urls,
                    "content": content
                })
            else:
                print(f"⚠️ Notícia já armazenada: {title}")

        return news_list

    def fetch_article_content(self, url):
        """Extrai o conteúdo completo de uma notícia do site e formata corretamente."""
        html = self.get_html(url)
        if not html:
            return "No content available"

        soup = self.parse_html(html)
        content_div = soup.find('div', class_='zox-post-body')  # Ajuste para Metal Injection
        
        if content_div:
            paragraphs = content_div.find_all(['p', 'h2', 'h3', 'blockquote'])
            formatted_content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
            return formatted_content
        
        return "No content available"
    
    def fetch_article_image(self, url):
        """Extrai a URL da imagem principal da matéria."""
        html = self.get_html(url)
        if not html:
            return None
        
        soup = self.parse_html(html)
        image_div = soup.find('div', class_='zox-post-img-wrap')
        if image_div:
            img_tag = image_div.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag['src']
        
        return None
    
    def fetch_article_videos(self, url):
        """Extrai todas as URLs de vídeos incorporados na matéria."""
        html = self.get_html(url)
        if not html:
            return []
        
        soup = self.parse_html(html)
        video_iframes = soup.find_all('iframe')
        video_urls = [iframe.get('src') for iframe in video_iframes if iframe.get('src') and 'youtube.com' in iframe.get('src')]
        
        return video_urls
