from src.scrapers.blabbermouth_scraper import BlabbermouthScraper
from src.scrapers.bravewords_scraper import BraveWordsScraper
from src.scrapers.metalinjection_scraper import MetalInjectionScraper
from src.scrapers.loudwire_scraper import LoudwireScraper
from src.scrapers.metaltalk_scraper import MetalTalkScraper
from src.scrapers.metalsucks_scraper import MetalSucksScraper
from src.scrapers.metalhammer_scraper import MetalHammerScraper

def test_scraper(scraper_class, name, limit=2):
    print(f"\n🔍 Testando scraper: {name}...")
    
    scraper = scraper_class()
    articles = scraper.fetch_articles(limit=limit)
    
    if not articles:
        print(f"❌ Nenhuma notícia encontrada para {name}!")
        return

    for idx, article in enumerate(articles):
        print(f"\n📰 {name} - Notícia {idx + 1}:")
        print(f"📌 Título: {article['title']}")
        print(f"🔗 Link: {article['link']}")
        print(f"📅 Data: {article['date']}")
        
        print("📖 Buscando conteúdo completo...")
        content = scraper.fetch_article_content(article['link'])
        print(f"📝 Conteúdo (500 caracteres): {content[:500]}...")

if __name__ == "__main__":
    scrapers = [
        (BlabbermouthScraper, "Blabbermouth"),
        (BraveWordsScraper, "Brave Words"),
        (MetalInjectionScraper, "Metal Injection"),
        (LoudwireScraper, "Loudwire"),
        (MetalTalkScraper, "Metal Talk"),
        (MetalSucksScraper, "Metal Sucks"),
        (MetalHammerScraper, "Metal Hammer")
    ]

    for scraper_class, name in scrapers:
        test_scraper(scraper_class, name)
