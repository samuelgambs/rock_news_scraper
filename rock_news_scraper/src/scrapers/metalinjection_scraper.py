import requests
from bs4 import BeautifulSoup
from src.scrapers.base_scraper import BaseScraper
import logging

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
        """Coleta e armazena artigos de Metal Injection."""
        try:
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar {self.base_url}: {e}", exc_info=True)
            return []

        soup = BeautifulSoup(response.content, "xml")
        articles = soup.find_all(self.article_selector)[:limit]

        for article in articles:
            try:
                title = article.find(self.title_selector).text.strip()
                link = article.find(self.link_selector).text.strip()
                date = self.format_date(article.find(self.date_selector).text.strip())
                content, image_url, video_urls = self.fetch_article_details(link)

                self.storage.add_news(title, link, date, content, image_url, video_urls)
            except Exception as e:
                logging.error(f"Erro ao processar artigo {link}: {e}", exc_info=True)

        logging.info(f"Notícias coletadas com sucesso de Metal Injection!")

    def fetch_article_details(self, url):
        """Extrai detalhes do artigo (conteúdo, imagem e vídeos)."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar {url}: {e}", exc_info=True)
            return "", "", []

        soup = BeautifulSoup(response.content, "html.parser")

        try:
            content_section = soup.select_one(self.content_selector)
            content = content_section.get_text(separator="\n").strip() if content_section else ""

            image_tag = soup.select_one(self.image_selector)
            image_url = image_tag["content"] if image_tag else ""

            video_urls = self.fetch_article_videos(url)
            return content, image_url, video_urls
        except Exception as e:
            logging.error(f"Erro ao extrair detalhes de {url}: {e}", exc_info=True)
            return "", "", []

    def format_date(self, date_str):
        """Formata a data do artigo no formato ISO 8601."""
        from datetime import datetime
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").isoformat()
        except ValueError:
            logging.warning(f"Formato de data inválido: {date_str}")
            return date_str