import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time


class BaseScraper:
    def __init__(self, base_url, article_selector, title_selector, link_selector, date_selector, content_selector, image_selector, video_selector, storage):
        self.base_url = base_url
        self.article_selector = article_selector
        self.title_selector = title_selector
        self.link_selector = link_selector
        self.date_selector = date_selector
        self.content_selector = content_selector
        self.image_selector = image_selector
        self.video_selector = video_selector
        self.storage = storage
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_html(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"⚠️ Erro ao acessar {url}: {e}")
            return None

    def parse_html(self, html):
        return BeautifulSoup(html, "html.parser")

    def fetch_articles(self, limit=1):
        html = self.get_html(self.base_url)
        if not html:
            return []

        soup = self.parse_html(html)
        items = soup.find_all("item", limit=limit)
        
        for item in items:
            title = item.find("title").text.strip()
            link = item.find("link").text.strip()
            date = item.find("pubDate").text.strip()
            date = self.format_date(date)
            
            content, image_url = self.fetch_article_content(link)
            video_urls = self.fetch_article_videos(link)

            self.storage.add_news(title, link, date, content, image_url, video_urls)
            time.sleep(1)  # Evita sobrecarga no servidor

    def fetch_article_content(self, url):
        html = self.get_html(url)
        if not html:
            return "", ""

        soup = self.parse_html(html)
        article_body = soup.find("div", class_=self.article_content_class)
        content = article_body.get_text(separator="\n").strip() if article_body else ""
        image_url = self.fetch_main_image(soup)

        return content, image_url

    def fetch_main_image(self, soup):
        image = soup.find("meta", property="og:image")
        return image["content"] if image else ""
    

    def fetch_article_videos(self, url):
        """Extrai todas as URLs de vídeos incorporados na matéria, apenas do YouTube."""
        html = self.get_html(url)
        if not html:
            return []
        
        soup = self.parse_html(html)
        video_iframes = soup.find_all('iframe')

        # Filtra apenas URLs que contenham 'youtube.com' ou 'youtu.be'
        video_urls = [
            iframe.get('src') for iframe in video_iframes 
            if iframe.get('src') and ('youtube.com' in iframe.get('src') or 'youtu.be' in iframe.get('src'))
        ]

        return video_urls


    def format_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z").isoformat()
        except ValueError:
            print(f"⚠️ Erro ao processar data: {date_str}")
            return date_str


# import requests
# import time
# import random
# import logging
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent



# class BaseScraper:
#     def __init__(self, base_url, storage, max_retries=3, delay_range=(1, 3), use_proxies=False, content_class=None):
#         self.base_url = base_url
#         self.storage = storage
#         self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
#         self.max_retries = max_retries
#         self.session = requests.Session()
#         self.user_agent = UserAgent()
#         self.delay_range = delay_range
#         self.use_proxies = use_proxies

#         self.content_class = content_class  # Permitir que cada scraper defina a classe correta

#     def get_headers(self):
#         """Gera cabeçalhos HTTP aleatórios."""
#         return {
#             "User-Agent": self.user_agent.random,
#             "Accept-Language": "en-US,en;q=0.5"
#         }    
    
#     def fetch_articles(self, limit=5):
#         response = requests.get(self.base_url, headers={"User-Agent": "Mozilla/5.0"})
#         soup = BeautifulSoup(response.content, "html.parser")
#         articles = soup.find_all("item", limit=limit)

#         for item in articles:
#             title = item.find("title").text.strip()
#             link = item.find("link").text.strip()
#             date = item.find("pubDate").text.strip()
            
#             content, image_url, video_urls = self.fetch_article_details(link)

#             self.storage.add_news(title, link, date, content, image_url, video_urls)

#     def fetch_article_videos(self, url):
#         """Extrai todas as URLs de vídeos incorporados na matéria."""
#         html = self.get_html(url)
#         if not html:
#             return []
        
#         soup = self.parse_html(html)
#         video_iframes = soup.find_all('iframe')
#         video_urls = [iframe.get('src') for iframe in video_iframes if iframe.get('src') and 'youtube.com' in iframe.get('src')]
        
#         return video_urls
    

#     def fetch_article_details(self, url):
#         """ Captura o conteúdo do artigo, buscando a div correta dinamicamente """
#         response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#         soup = BeautifulSoup(response.content, "html.parser")

#         # Se a classe foi definida pelo scraper específico, usa ela
#         article_body = soup.find("div", class_=self.content_class) if self.content_class else None
        
#         if not article_body:  # Se não encontrou a classe específica, tenta alternativas
#             possible_classes = ["article-content", "post-content", "entry-content", "content-body"]
#             for possible_class in possible_classes:
#                 article_body = soup.find("div", class_=possible_class)
#                 if article_body:
#                     break

#         content = article_body.get_text(strip=True) if article_body else "⚠️ Conteúdo não encontrado."
#         image_url = soup.find("meta", property="og:image")
#         image_url = image_url["content"] if image_url else ""
       

#         # video_urls = [video["src"] for video in soup.find_all("iframe") if "src" in video.attrs]
#         # videos = soup.find_all("iframe")

#         # video_urls = [vid["src"] for vid in videos if "youtube" in vid["src"]]

#         return content
        
#     def get_html(self, url):
#         """
#         Obtém o HTML da página, tratando falhas e bloqueios.
#         """
#         retries = 0
#         while retries < self.max_retries:
#             try:
#                 logging.info(f"📡 Acessando {url} (Tentativa {retries + 1})")
                
#                 response = self.session.get(url, headers=self.get_headers(), timeout=10)
                
#                 if response.status_code == 200:
#                     return response.text
#                 elif response.status_code == 403:
#                     logging.warning("🚨 Acesso negado (403). Pode ser necessário um proxy ou rotação de User-Agent.")
#                 elif response.status_code == 404:
#                     logging.error("❌ Página não encontrada (404).")
#                     return None
                
#                 retries += 1
#                 time.sleep(random.uniform(*self.delay_range))

#             except requests.RequestException as e:
#                 logging.error(f"⚠️ Erro ao acessar {url}: {e}")
#                 retries += 1
#                 time.sleep(random.uniform(*self.delay_range))

#         logging.error(f"❌ Falha ao obter HTML após {self.max_retries} tentativas: {url}")
#         return None
    
#     def parse_html(self, html):
#         """
#         Converte HTML bruto em um objeto BeautifulSoup.
#         """
#         return BeautifulSoup(html, "html.parser")

#     def normalize_url(self, url):
#         """
#         Normaliza URLs para evitar problemas de redirecionamento.
#         """
#         if not url.startswith("http"):
#             return f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
#         return url
