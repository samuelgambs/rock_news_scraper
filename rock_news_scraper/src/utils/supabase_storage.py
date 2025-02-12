import os
from supabase import create_client, Client

# Configurar as credenciais
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")




# Inicializar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class SupabaseStorage:
    def add_news(self, news_data):
        """Adiciona uma notícia no banco, evitando duplicação."""
        existing = supabase.table("news").select("id").eq("url", news_data["url"]).execute()
        if existing.data:
            print(f"⚠️ Notícia já existe: {news_data['title']}")
            return

        response = supabase.table("news").insert(news_data).execute()
        if response.data:
            print(f"✅ Notícia salva: {news_data['title']}")
        else:
            print(f"⚠️ Erro ao salvar: {news_data['title']}")

    def get_all_news(self):
        """Busca todas as notícias no Supabase."""
        response = supabase.table("news").select("*").execute()
        return response.data if response.data else []
