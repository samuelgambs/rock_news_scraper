
from google.cloud import aiplatform
from src.utils.news_storage import NewsStorage
def process_news_entities(storage):


    aiplatform.init(project="702779039730")

    model = aiplatform.Model("models/gemini-1.5-flash")
    
    news_articles = storage.get_all_news()

    for article in news_articles:
        if "translated_title" in article and article["translated_title"]:
            
            
            response = model.predict(prompt=f"""
                Extraia nomes de artistas de rock e metal do título a seguir e retorne-os como uma lista separada por vírgulas:

                {article["translated_title"]}
            """)


            article["entities"] = response.predictions[0].text

    storage.save_news(news_articles)
#     print("✅ Entidades extraídas e salvas com sucesso!")


    return 


# import spacy
# from src.utils.news_storage import NewsStorage
# def process_news_entities(storage):
#     """Processa entidades nomeadas nas notícias traduzidas."""
#     nlp = spacy.load("pt_core_news_sm")  # Usando modelo em Português

#     news_articles = storage.get_all_news()

#     for article in news_articles:
#         if "translated_content" in article and article["translated_content"]:
#             doc = nlp(article["translated_content"])
#             article["entities"] = [(ent.text, ent.label_) for ent in doc.ents]

#     storage.save_news(news_articles)
#     print("✅ Entidades extraídas e salvas com sucesso!")

# # Carregar modelo de linguagem do spaCy
# nlp = spacy.load("en_core_web_sm")

# def extract_named_entities(text):
#     """
#     Extrai entidades nomeadas do texto usando spaCy.
    
#     Args:
#         text (str): O texto a ser processado.

#     Returns:
#         list: Lista de tuplas contendo a entidade e seu tipo.
#     """
#     doc = nlp(text)
#     return [(ent.text, ent.label_) for ent in doc.ents]

# def process_news_entities(storage):
#     """
#     Processa todas as notícias armazenadas, extrai as entidades nomeadas e atualiza o armazenamento.
    
#     Args:
#         storage (NewsStorage): Instância do gerenciador de armazenamento de notícias.
#     """
#     all_news = storage.get_all_news()

#     if not all_news:
#         print("⚠️ Nenhuma notícia encontrada! O processamento de NER foi abortado.")
#         return

#     for news in all_news:
#         content = news.get("content", "")
#         if content:
#             news["named_entities"] = extract_named_entities(content)
    
#     storage.save_news(storage.get_all_news())  # Agora passa corretamente os dados atualizados
#     print("✅ Entidades nomeadas extraídas e salvas com sucesso!")
