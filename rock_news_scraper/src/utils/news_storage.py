# import os

# class NewsStorage:
#     def __init__(self):
#         self.supabase_url = os.getenv("SUPABASE_URL")
#         self.supabase_key = os.getenv("SUPABASE_KEY")
        
#         if not self.supabase_url or not self.supabase_key:
#             raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não foram definidas.")

#         self.client: Client = create_client(self.supabase_url, self.supabase_key)

#     def news_exists(self, title):
#         """Verifica se a notícia já existe no banco de dados."""
#         response = self.client.table("news").select("title").eq("title", title).execute()
#         return len(response.data) > 0  # Se houver pelo menos um resultado, já existe

#     def add_news(self, title, url, date, content, image_url, video_urls):
#         """Adiciona uma nova notícia ao banco de dados, evitando duplicatas."""
#         if not self.news_exists(title):
#             data = {
#                 "title": title,
#                 "url": url,
#                 "date": date,
#                 "content": content,
#                 "image_url": image_url,
#                 "video_urls": video_urls,
#                 # "entities": entities
#             }
#             response = self.client.table("news").insert(data).execute()
#             print(f"✅ Notícia adicionada: {title}")
#             return response
#         else:
#             print(f"⚠️ Notícia já existe: {title}")

#     def get_all_news(self):
#         """Recupera todas as notícias do banco de dados."""
#         response = self.client.table("news").select("*").execute()
#         return response.data if response.data else []

#     def get_published_titles(self):
#         """Recupera todos os títulos já publicados para evitar duplicatas."""
#         response = self.client.table("news").select("title").execute()
#         return [news["title"] for news in response.data] if response.data else []
    
#     def update_translated_news(self, title, translated_title, translated_content):
#         """Atualiza a notícia com a tradução no Supabase."""
#         response = self.client.table("news").update({
#             "translated_title": translated_title,
#             "translated_content": translated_content
#         }).eq("title", title).execute()

#         if response.data:
#             print(f"✅ Tradução salva para: {title}")
#         else:
#             print(f"⚠️ Falha ao atualizar tradução para: {title}")


import json
import os
from supabase import create_client, Client
from datetime import datetime

class NewsStorage:
    def __init__(self, file_path="news_storage.json"):
        self.file_path = file_path
        self.news = self.load_news()
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não foram definidas.")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def load_news(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return []
        return []

    def save_news(self, news_data):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(news_data, file, indent=4, ensure_ascii=False)

    def add_news(self, title, link, date, content, image_url, video_urls):
        if not self.news_exists_db(title):
            self.news.append({
                "title": title,
                "link": link,
                "date": date,
                "content": content,
                "image_url": image_url,
                "video_urls": video_urls
            })
            self.save_news(self.news)
            self.add_news_db(title, link, date, content, image_url, video_urls)


    def news_exists_json(self, title):
        return any(news["title"] == title for news in self.news)
    
    def news_exists_db(self, title):
        """Verifica se a notícia já existe no banco de dados."""

        print(f"🔍 Verificando se a notícia '{title}' já existe no banco de dados...")
        response = self.client.table("news").select("title").eq("title", title).execute()
        return len(response.data)

    def get_all_news(self):
        return self.news
    

    def get_all_news_db(self):
        """Recupera todas as notícias do banco de dados."""
        response = self.client.table("news").select("*").execute()
        return response.data if response.data else []

    def get_published_titles_db(self):
        """Recupera todos os títulos já publicados para evitar duplicatas."""
        response = self.client.table("news").select("title").execute()
        return [news["title"] for news in response.data] if response.data else []
    
    def update_translated_news_db(self, title, translated_title, translated_content, tags):
        """Atualiza a notícia com a tradução e tags no Supabase."""
        response = self.client.table("news").update({
            "translated_title": translated_title,
            "translated_content": translated_content,
            "entities": tags
        }).eq("title", title).execute()

        if response.data:
            print(f"✅ Tradução salva para: {title}")
        else:
            print(f"⚠️ Falha ao atualizar tradução para: {title}")
    
    
    def _load_titles(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def get_published_titles(self):
        return self._load_titles

    def add_published_title(self, title):
        if title not in self.published_titles:
            self.published_titles.append(title)
            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(self.published_titles, file, indent=4, ensure_ascii=False)

    def add_news_db(self, title, link, date, content, image_url, video_urls):
        """Adiciona uma nova notícia ao banco de dados apenas se não existir."""
        # Verifica se a notícia já existe no banco de dados
        existing_news = self.client.table("news").select("id").eq("url", link).execute()

        if existing_news.data:  # Se já existir, não adiciona
            print(f"⚠️ Notícia '{title}' já existe no banco de dados. Pulando...")
            return

        data = {
            "title": title,
            "url": link,
            "date": date,
            "content": content,
            "image_url": image_url,
            "video_urls": video_urls
        }

        try:
            self.client.table("news").insert(data).execute()
            print(f"✅ Notícia adicionada ao banco: {title}")
        except Exception as e:
            print(f"❌ Erro ao adicionar notícia: {e}")


