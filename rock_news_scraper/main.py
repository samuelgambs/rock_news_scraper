from src.scrapers.blabbermouth_scraper import BlabbermouthScraper
from src.scrapers.bravewords_scraper import BraveWordsScraper
from src.scrapers.metalinjection_scraper import MetalInjectionScraper
from src.scrapers.loudwire_scraper import LoudwireScraper
from src.scrapers.metaltalk_scraper import MetalTalkScraper
from src.scrapers.metalsucks_scraper import MetalSucksScraper
from src.scrapers.metalhammer_scraper import MetalHammerScraper
from src.utils.news_storage import NewsStorage
from src.utils.ner_extractor import process_news_articles

def main():
    """Executa o pipeline completo: scraping, armazenamento e processamento NER."""
    scrapers = [
        BlabbermouthScraper(),
        BraveWordsScraper(),
        MetalInjectionScraper(),
        LoudwireScraper(),
        MetalTalkScraper(),
        MetalSucksScraper(),
        MetalHammerScraper(),
    ]
    
    storage = NewsStorage()
    all_news = []
    
    for scraper in scrapers:
        print(f"🔍 Coletando notícias de {scraper.source}")
        news = scraper.fetch_articles()
        all_news.extend(news)
    
    storage.save_news()
    print("✅ Notícias salvas com sucesso!")
    
    # Processa as entidades nomeadas nas notícias
    print("🧠 Processando entidades nomeadas nas notícias...")
    process_news_articles()
    print("✅ Processamento concluído!")

if __name__ == "__main__":
    main()
