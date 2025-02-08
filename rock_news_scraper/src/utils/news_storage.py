import json
import os

class NewsStorage:
    def __init__(self, file_path="news_storage.json"):
        self.file_path = file_path
        self.news = self.load_news()

    def load_news(self):
        """Carrega as notícias do arquivo JSON, se existir."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Arquivo JSON corrompido. Criando um novo arquivo limpo.")
                return []
        return []

    def save_news(self):
        """Salva todas as notícias sem apagar as antigas."""
        if not self.news:
            print("⚠️ Nenhuma notícia para salvar. O arquivo JSON não será modificado.")
            return

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.news, f, indent=4, ensure_ascii=False)
        
        print(f"✅ {len(self.news)} notícias salvas em {self.file_path}")

    def news_exists(self, title):
        """Verifica se uma notícia já foi armazenada pelo título."""
        return any(news["title"] == title for news in self.news)

    def add_news(self, title, link, date, content, image_url=None, video_urls=None):
        """Adiciona uma nova notícia sem sobrescrever as antigas."""
        if self.news_exists(title):
            print(f"⚠️ Notícia já armazenada: {title}")
            return
        
        new_article = {
            "title": title,
            "link": link,
            "date": date,
            "content": content,
            "image_url": image_url,
            "video_urls": video_urls if video_urls else []
        }

        self.news.append(new_article)
        self.save_news()

