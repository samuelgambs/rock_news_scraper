import os
from src.scrapers.blabbermouth_scraper import BlabbermouthScraper
from src.scrapers.bravewords_scraper import BraveWordsScraper
from src.scrapers.metalinjection_scraper import MetalInjectionScraper
from src.scrapers.loudwire_scraper import LoudwireScraper
from src.scrapers.metaltalk_scraper import MetalTalkScraper
from src.scrapers.metalsucks_scraper import MetalSucksScraper
from src.scrapers.metalhammer_scraper import MetalHammerScraper
from src.utils.news_storage import NewsStorage
from src.utils.extract_named_entities import process_news_entities
from src.utils.translator import translate_news

# 🔥 Defina o limite de notícias por site
LIMIT_PER_SITE = 5 

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
        # BraveWordsScraper(storage),
        # MetalInjectionScraper(storage),
        # LoudwireScraper(storage),
        # MetalTalkScraper(storage),
        # MetalSucksScraper(storage),
        # MetalHammerScraper(storage)
    ]

    # 🔍 Coleta notícias de cada site
    for scraper in scrapers:
        print(f"🔍 Coletando notícias de {scraper.source}...")
        scraper.fetch_articles(limit=LIMIT_PER_SITE)
        print(f"✅ Notícias coletadas com sucesso de {scraper.source}!")

    # 🧠 Processa entidades nomeadas
    print("🧠 Processando entidades nomeadas nas notícias...")
    process_news_entities(storage)
    print("✅ Entidades nomeadas extraídas e salvas com sucesso!")

    # 🌎 Traduz notícias para português
    print("🌎 Traduzindo notícias para Português...")
    translate_news(storage)
    print("✅ Tradução concluída e salva com sucesso!")

if __name__ == "__main__":
    main()
