import spacy
from src.utils.news_storage import NewsStorage

# Carregar modelo de linguagem do spaCy
nlp = spacy.load("en_core_web_sm")

def extract_named_entities(text):
    """Extrai entidades nomeadas de um texto, como bandas, artistas e locais."""
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT"]:
            entities.append((ent.text, ent.label_))
    
    return entities

def process_news_articles():
    """Processa as notícias armazenadas e extrai entidades nomeadas."""
    storage = NewsStorage()
    news_articles = storage.load_news()

    if not news_articles:  # 🚨 Verifica se há notícias antes de continuar
        print("⚠️ Nenhuma notícia encontrada! O processamento de NER foi abortado.")
        return

    for article in news_articles:
        entities = extract_named_entities(article["content"])
        article["entities"] = entities
    
    storage.news = news_articles  # Atualiza as notícias com as entidades extraídas
    storage.save_news()
    print("✅ Entidades extraídas e notícias salvas com sucesso!")

# Testando com um exemplo
test_text = "Iron Maiden announced a new tour in Brazil, featuring Bruce Dickinson and Steve Harris."
entities = extract_named_entities(test_text)
print("📌 Entidades Nomeadas:", entities)
