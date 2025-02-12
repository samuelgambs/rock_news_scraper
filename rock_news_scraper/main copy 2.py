import os
from src.scrapers.blabbermouth_scraper import BlabbermouthScraper
from src.utils.translator import Translator
from src.utils.wordpress_publisher import postar_no_wordpress, publish_to_wordpress
from src.utils.news_storage import NewsStorage

# CONFIGURAÇÕES
LIMIT_PER_SITE = 2
storage = NewsStorage()

def main():
    """Fluxo principal do sistema"""
    
    print("🔍 Coletando notícias...")
    
    scrapers = [
        BlabbermouthScraper(storage)
    ]

    for scraper in scrapers:
        scraper.fetch_articles(limit=LIMIT_PER_SITE)

    print("✅ Coleta concluída!")

    # Traduzir e Publicar
    translator = Translator()
    for news in storage.get_all_news():
        if news["title"] in storage.get_published_titles():
            continue  # Pula se já foi publicado

        print(f"🌎 Traduzindo: {news['title']}...")
        translated_title = translator.translate_text(news["title"])
        translated_content = translator.translate_text(news["content"])

        # Publicar no WordPress
        postar_no_wordpress(
            titulo=translated_title,
            conteudo=translated_content,
            image_url=news["image_url"],
            tags=news["entities"],
            # video_url=news["video_urls"][0] if news["video_urls"] else ""
        )

    print("✅ Todas as notícias foram processadas e publicadas!")

if __name__ == "__main__":
    main()
