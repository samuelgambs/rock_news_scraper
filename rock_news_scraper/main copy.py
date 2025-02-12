import os
from src.scrapers.blabbermouth_scraper import BlabbermouthScraper
from src.scrapers.bravewords_scraper import BraveWordsScraper
from src.scrapers.metalinjection_scraper import MetalInjectionScraper
from src.scrapers.loudwire_scraper import LoudwireScraper
from src.scrapers.metaltalk_scraper import MetalTalkScraper
from src.scrapers.metalsucks_scraper import MetalSucksScraper
from src.utils.news_storage import NewsStorage
from src.utils.extract_named_entities import process_news_entities
from src.utils.translator import translate_news
from src.utils.wordpress_publisher import postar_no_wordpress


# 🔥 Defina o limite de notícias por site
LIMIT_PER_SITE = 1

def main():
    """Fluxo principal do script"""
    
    # 🗑️ Exclui o arquivo de armazenamento antes de começar
    if os.path.exists("news_storage.json"):
        os.remove("news_storage.json")
        print("🗑️ Arquivo news_storage.json excluído antes da execução.")

    # 📦 Inicializa o armazenamento
    storage = NewsStorage()

    # 📰 Lista de scrapers
    scrapers = [
        BlabbermouthScraper(storage),
        BraveWordsScraper(storage),
        # MetalInjectionScraper(storage),
        # LoudwireScraper(storage),
        # MetalTalkScraper(storage),
        # MetalSucksScraper(storage),
    ]

    # 1️⃣ Coletar notícias
    for scraper in scrapers:
        print(f"🔍 Coletando notícias de {scraper.__class__.__name__}...")
        scraper.fetch_articles(limit=LIMIT_PER_SITE)

    print("✅ Todas as notícias foram coletadas com sucesso!")

    # 2️⃣ Traduzir antes de processar as entidades
    print("🌎 Traduzindo notícias para Português...")
    translate_news(storage)

    # 3️⃣ Processar entidades no texto traduzido
    print("🧠 Processando entidades nomeadas nas notícias traduzidas...")
    process_news_entities(storage)

    # 4️⃣ Publicar no WordPress
    print("📝 Publicando notícias no WordPress...")
    import pdb; pdb.set_trace()
    postar_no_wordpress(storage)

    print("✅ Processo finalizado!")
if __name__ == "__main__":
    main()
