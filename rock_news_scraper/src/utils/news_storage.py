import json
import os
import logging
from supabase import create_client, Client
from datetime import datetime

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            try:
                with open(self.file_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                logging.error(f"Erro ao decodificar JSON do arquivo: {self.file_path}", exc_info=True)
                return []
        return []

    def save_news(self, news_data):
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(news_data, file, indent=4, ensure_ascii=False)
            logging.info(f"Notícias salvas em: {self.file_path}")
        except Exception as e:
            logging.error(f"Erro ao salvar notícias em: {self.file_path}: {e}", exc_info=True)

    def add_news(self, title, link, date, content, image_url, video_urls):
        if not self.news_exists_db(link):
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
        else:
            logging.info(f"Notícia '{title}' já existe no banco de dados. Pulando...")

    def news_exists_db(self, link):
        """Verifica se a notícia já existe no banco de dados com base na URL."""
        try:
            response = self.client.table("news").select("id").eq("url", link).execute()
            return len(response.data) > 0
        except Exception as e:
            logging.error(f"Erro ao verificar existência da notícia no banco de dados: {e}", exc_info=True)
            return False

    def get_all_news(self):
        return self.news

    def get_all_news_db(self):
        """Recupera todas as notícias do banco de dados."""
        try:
            response = self.client.table("news").select("*").execute()
            return response.data if response.data else []
        except Exception as e:
            logging.error(f"Erro ao recuperar notícias do banco de dados: {e}", exc_info=True)
            return []

    def get_published_titles_db(self):
        """Recupera todos os títulos já publicados para evitar duplicatas."""
        try:
            response = self.client.table("news").select("title").eq("published", True).execute()
            return [news["title"] for news in response.data] if response.data else []
        except Exception as e:
            logging.error(f"Erro ao recuperar títulos publicados do banco de dados: {e}", exc_info=True)
            return []

    def update_translated_news_db(self, title, translated_title, translated_content, tags):
        """Atualiza a notícia com a tradução e tags no Supabase."""
        try:
            response = self.client.table("news").update({
                "translated_title": translated_title,
                "translated_content": translated_content,
                "entities": tags
            }).eq("title", title).execute()

            if response.data:
                logging.info(f"Tradução salva para: {title}")
            else:
                logging.warning(f"Falha ao atualizar tradução para: {title}")
        except Exception as e:
            logging.error(f"Erro ao atualizar tradução para {title}: {e}", exc_info=True)

    def add_news_db(self, title, link, date, content, image_url, video_urls):
        """Adiciona uma nova notícia ao banco de dados apenas se não existir."""
        data = {
            "title": title,
            "url": link,
            "date": date,
            "content": content,
            "image_url": image_url,
            "video_urls": video_urls,
            "published": False  # Adiciona o campo published como False inicialmente
        }

        try:
            self.client.table("news").insert(data).execute()
            logging.info(f"Notícia adicionada ao banco: {title}")
        except Exception as e:
            logging.error(f"Erro ao adicionar notícia: {e}", exc_info=True)
            
    def mark_as_published(self, link):
            """Marca a notícia como publicada no Supabase e atualiza published_at."""
            try:
                now = datetime.utcnow().isoformat()  # Obtém o timestamp UTC atual
                response = self.client.table("news").update({"published": True, "published_at": now}).eq("url", link).execute()
                if response.data:
                    logging.info(f"Notícia marcada como publicada: {link} - published_at: {now}")
                else:
                    logging.warning(f"Falha ao marcar notícia como publicada: {link}")
            except Exception as e:
                logging.error(f"Erro ao marcar notícia como publicada: {e}", exc_info=True)