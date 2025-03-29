import os
import logging
from src.scrapers.blabbermouth_scraper import BlabbermouthScraper
from src.scrapers.bravewords_scraper import BraveWordsScraper
from src.scrapers.metalinjection_scraper import MetalInjectionScraper
from src.scrapers.loudwire_scraper import LoudwireScraper
from src.scrapers.metaltalk_scraper import MetalTalkScraper
from src.scrapers.metalsucks_scraper import MetalSucksScraper
from src.utils.news_storage import NewsStorage
from src.utils.wordpress_publisher import postar_no_wordpress
from dotenv import load_dotenv
# from src.utils.openai_utils import OpenAIUtils
from src.utils.gemini_utils import GeminiUtils
# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega as variáveis do arquivo .env.local
load_dotenv(".env.local")

# Agora você pode acessar as variáveis como se estivessem no ambiente do sistema
WORDPRESS_URL = os.getenv("WORDPRESS_URL")
WORDPRESS_USER = os.getenv("WORDPRESS_USER")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 🔥 Defina o limite de notícias por site
LIMIT_PER_SITE = 10

def main():
    """Fluxo principal do script"""
    
    # 🗑️ Exclui o arquivo de armazenamento antes de começar
    if os.path.exists("news_storage.json"):
        os.remove("news_storage.json")
        logging.info("Arquivo news_storage.json excluído antes da execução.")

    # 📦 Inicializa o armazenamento
    storage = NewsStorage()
    gemini_utils = GeminiUtils()
    # openai_utils = OpenAIUtils()


    # 📰 Lista de scrapers
    scrapers = [
        BlabbermouthScraper(storage),
        BraveWordsScraper(storage),
        MetalInjectionScraper(storage),
        LoudwireScraper(storage),
        MetalTalkScraper(storage),
        MetalSucksScraper(storage),
    ]


    # 1️⃣ Coletar notícias
    try:
        for scraper in scrapers:
            logging.info(f"Coletando notícias de {scraper.__class__.__name__}...")
            scraper.fetch_articles(limit=LIMIT_PER_SITE)
    except Exception as e:
        logging.error(f"Ocorreu um erro durante a execução: {e}", exc_info=True)

    print("✅ Todas as notícias foram coletadas com sucesso!")




    # 2️⃣ Traduzir antes de processar as entidades
    logging.info("Traduzindo notícias para Português...")
    # openai_utils.translate_news(storage)
    gemini_utils.translate_news(storage)

    

    # 4️⃣ Publicar no WordPress
    logging.info("Publicando notícias no WordPress...")
    postar_no_wordpress(storage)

    logging.info("Processo finalizado!")
if __name__ == "__main__":
    # test_openai_connection()
    # check_google_translate()
    main()
