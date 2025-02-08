from src.scrapers.base_scraper import BaseScraper
from src.utils.news_storage import NewsStorage
import feedparser
from bs4 import BeautifulSoup

class MetalSucksScraper(BaseScraper):
    """
    Scraper para coletar notícias do site MetalSucks via RSS.
    """
    def __init__(self):
        super().__init__("https://www.metalsucks.net")
        self.source = "Metal Hammer"
        self.storage = NewsStorage()



    def fetch_articles(self, limit=10):
        """Busca as últimas notícias do feed RSS."""
        feed_url = "https://feeds.feedburner.com/Metalsucks"
        news_list = []
        
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            print("❌ Nenhuma entrada encontrada no feed RSS.")
            return []

        for entry in feed.entries[:limit]:
            title = entry.title
            link = entry.link
            date = entry.published if hasattr(entry, "published") else "Data não disponível"
            
            news_list.append({
                "title": title,
                "link": link,
                "date": date
            })

        return news_list

    def fetch_article_content(self, url):
        """Extrai o conteúdo completo de uma notícia do site."""
        html = self.get_html(url)
        if not html:
            return "No content available"

        soup = self.parse_html(html)
        content_div = soup.find('div', class_='post-body')  # Ajuste a classe conforme necessário
        
        if content_div:
            paragraphs = content_div.find_all(['p', 'h2', 'h3', 'blockquote'])
            formatted_content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
            return formatted_content
        
        return "No content available"
