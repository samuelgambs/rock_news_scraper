import spacy
import json
import os

class NamedEntityExtractor:
    def __init__(self, model="en_core_web_sm", storage_file="news_storage.json"):
        self.nlp = spacy.load(model)
        self.storage_file = storage_file

    def extract_entities(self, text):
        """Extrai entidades nomeadas do texto usando spaCy"""
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]

    def process_news_articles(self):
        """Processa todas as notícias e adiciona entidades nomeadas"""
        if not os.path.exists(self.storage_file):
            print("⚠️ Arquivo de notícias não encontrado! Abortando processamento de entidades.")
            return

        # 📖 Carrega as notícias do JSON
        with open(self.storage_file, "r", encoding="utf-8") as file:
            try:
                news_articles = json.load(file)
            except json.JSONDecodeError:
                print("⚠️ Erro ao carregar JSON! Abortando processamento de entidades.")
                return

        if not news_articles:
            print("⚠️ Nenhuma notícia encontrada! O processamento de NER foi abortado.")
            return

        # 🧠 Processa entidades e evita duplicação
        updated_articles = []
        for article in news_articles:
            if "content" in article and article["content"]:
                # Verifica se a notícia já tem entidades processadas
                if "entities" not in article or not article["entities"]:
                    article["entities"] = self.extract_entities(article["content"])
            updated_articles.append(article)

        # 💾 Salva de volta no arquivo sem duplicação
        with open(self.storage_file, "w", encoding="utf-8") as file:
            json.dump(updated_articles, file, indent=4, ensure_ascii=False)

        print("✅ Entidades extraídas e salvas com sucesso!")

if __name__ == "__main__":
    extractor = NamedEntityExtractor()
    extractor.process_news_articles()
