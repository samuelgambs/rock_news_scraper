import requests
import time
import random
import logging
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

class BaseScraper:
    """
    Classe base para scrapers de notícias.
    """
    def __init__(self, base_url, max_retries=3, delay_range=(1, 3), use_proxies=False):
        self.base_url = base_url
        self.max_retries = max_retries
        self.delay_range = delay_range
        self.use_proxies = use_proxies
        self.session = requests.Session()
        self.user_agent = UserAgent()

        # Configuração de logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def get_headers(self):
        """Gera cabeçalhos HTTP aleatórios."""
        return {
            "User-Agent": self.user_agent.random,
            "Accept-Language": "en-US,en;q=0.5"
        }

    def get_html(self, url):
        """
        Obtém o HTML da página, tratando falhas e bloqueios.
        """
        retries = 0
        while retries < self.max_retries:
            try:
                logging.info(f"📡 Acessando {url} (Tentativa {retries + 1})")
                
                response = self.session.get(url, headers=self.get_headers(), timeout=10)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 403:
                    logging.warning("🚨 Acesso negado (403). Pode ser necessário um proxy ou rotação de User-Agent.")
                elif response.status_code == 404:
                    logging.error("❌ Página não encontrada (404).")
                    return None
                
                retries += 1
                time.sleep(random.uniform(*self.delay_range))

            except requests.RequestException as e:
                logging.error(f"⚠️ Erro ao acessar {url}: {e}")
                retries += 1
                time.sleep(random.uniform(*self.delay_range))

        logging.error(f"❌ Falha ao obter HTML após {self.max_retries} tentativas: {url}")
        return None

    def parse_html(self, html):
        """
        Converte HTML bruto em um objeto BeautifulSoup.
        """
        return BeautifulSoup(html, "html.parser")

    def normalize_url(self, url):
        """
        Normaliza URLs para evitar problemas de redirecionamento.
        """
        if not url.startswith("http"):
            return f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        return url

# Exemplo de uso
if __name__ == "__main__":
    scraper = BaseScraper("https://example.com")
    html = scraper.get_html("https://example.com/news")
    if html:
        soup = scraper.parse_html(html)
        print(soup.title.text)
