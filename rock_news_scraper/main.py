import os
from src.scrapers.blabbermouth_scraper import BlabbermouthScraper
from src.scrapers.bravewords_scraper import BraveWordsScraper
from src.scrapers.metalinjection_scraper import MetalInjectionScraper
from src.scrapers.loudwire_scraper import LoudwireScraper
from src.scrapers.metaltalk_scraper import MetalTalkScraper
from src.scrapers.metalsucks_scraper import MetalSucksScraper
from src.utils.news_storage import NewsStorage
# from src.utils.extract_named_entities import process_news_entities
from src.utils.translator import translate_news
from src.utils.wordpress_publisher import postar_no_wordpress
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env.local
load_dotenv(".env.local")

# Agora você pode acessar as variáveis como se estivessem no ambiente do sistema
WORDPRESS_URL = os.getenv("WORDPRESS_URL")
WORDPRESS_USER = os.getenv("WORDPRESS_USER")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 🔥 Defina o limite de notícias por site
LIMIT_PER_SITE = 1

def main():
    """Fluxo principal do script"""
    
    # 🗑️ Exclui o arquivo de armazenamento antes de começar
    # if os.path.exists("news_storage.json"):
    #     os.remove("news_storage.json")
    #     print("🗑️ Arquivo news_storage.json excluído antes da execução.")

    # 📦 Inicializa o armazenamento
    storage = NewsStorage()
    # translate = Translator()


    # 📰 Lista de scrapers
    scrapers = [
        BlabbermouthScraper(storage),
        BraveWordsScraper(storage),
        MetalInjectionScraper(storage),
        LoudwireScraper(storage),
        MetalTalkScraper(storage),
        MetalSucksScraper(storage),
    ]

#     for scraper in scrapers:
#         print(f"🔍 Coletando notícias de {scraper.__class__.__name__}...")
        
#         news_list = scraper.fetch_articles(limit=LIMIT_PER_SITE)
        
#         for news in news_list:
#             # Traduzir notícia
#             print(f"🌎 Traduzindo: {news['title']}...")
#             translated_title = translator.translate_text(news["title"])
#             translated_content = translator.translate_text(news["content"])
#             news["translated_title"] = translated_title
#             news["translated_content"] = translated_content
#             storage.add_news(**news)  # Armazena a versão traduzida imediatamente
            
#             # Publicar no WordPress
#             print(f"📝 Publicando no WordPress: {translated_title}...")
#             postar_no_wordpress(translated_title, translated_content, news["image_url"], news["entities"])

#     print("✅ Processo concluído!")

# if __name__ == "__main__":
#     main()

    # 1️⃣ Coletar notícias
    for scraper in scrapers:
        print(f"🔍 Coletando notícias de {scraper.__class__.__name__}...")
        scraper.fetch_articles(limit=LIMIT_PER_SITE)

    print("✅ Todas as notícias foram coletadas com sucesso!")

    # 2️⃣ Traduzir antes de processar as entidades
    print("🌎 Traduzindo notícias para Português...")
    translate_news(storage)

    # 3️⃣ Processar entidades no texto traduzido
    # print("🧠 Processando entidades nomeadas nas notícias traduzidas...")
    # process_news_entities(storage)

    # 4️⃣ Publicar no WordPress
    print("📝 Publicando notícias no WordPress...")
    postar_no_wordpress(storage)

    print("✅ Processo finalizado!")
if __name__ == "__main__":
    main()
